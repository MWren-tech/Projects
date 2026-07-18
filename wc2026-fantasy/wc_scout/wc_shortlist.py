"""
WC2026 best-by-position shortlist.

Ranks players for World Cup fantasy by EXPECTED POINTS after four adjustments
the raw cross-league list lacked:

  1. League strength    — club xPts is multiplied by a per-league coefficient so
                          a goal in Ligue 1 isn't worth a goal in the EPL.
  2. Strong leagues only — pool = Big-5 + Portugal, Netherlands, Brazil.
  3. Current form        — blends recent-form xPts (last-N fixtures) with season.
  4. International role   — keeps ONLY players who are consistent starters for a
                          WC2026 nation, using national-team caps/starts, and
                          applies that nation's set-piece (penalty/FK/corner) duty.

    python wc_shortlist.py                      # top 15 per position
    python wc_shortlist.py --top 20 --recent 30 --min-caps 6 --min-start-rate 0.6

Reads season data from cache (free); recent-form and national-team stats are live
calls (cached afterwards). No WC2026 (league=1) calls are made.
"""

from __future__ import annotations

import argparse
import pickle
import sys
import time
from dataclasses import replace
from pathlib import Path

POOL_CACHE = Path(".pool_cache.pkl")   # built survivor pool, so reruns are instant

from api_football import ApiFootball, ApiFootballError
from scoring import FixtureContext
from player_form import extract_player_form, form_to_xpts
from recent_form import recent_forms
from country_form import build_country_forms
from wc_form import build_wc_forms
from league_report import defense_lookup
from set_piece_takers import canonical_nation, apply_set_pieces
from probable_xi import xi_rank
from national_strength import build_national_context, context_for, DEFAULT_CONTEXT, wc_team_ids
from fifa_fantasy import load_fifa_players, match_price, FifaFantasyError

# Player universe -> (league id, season, strength multiplier vs Premier League=1.00).
# Comprehensive: every league hosting a meaningful number of probable WC starters.
# Weaker leagues are DISCOUNTED via the multiplier, not excluded.
POOL: dict[str, tuple[int, int, float]] = {
    "premierleague": (39,  2025, 1.00),
    "laliga":        (140, 2025, 0.97),
    "seriea_italy":  (135, 2025, 0.95),
    "bundesliga":    (78,  2025, 0.94),
    "ligue1":        (61,  2025, 0.90),
    "primeiraliga":  (94,  2025, 0.82),
    "eredivisie":    (88,  2025, 0.80),
    "brazil_seriea": (71,  2025, 0.78),
    # --- comprehensive additions ---
    "belgium":       (144, 2025, 0.75),
    "championship":  (40,  2025, 0.74),
    "turkey":        (203, 2025, 0.72),
    "argentina":     (128, 2025, 0.72),
    "liga_mx":       (262, 2025, 0.70),
    "mls":           (253, 2025, 0.68),
    "scotland":      (179, 2025, 0.66),
    "switzerland":   (207, 2025, 0.66),
    "saudi":         (307, 2025, 0.65),
    "austria":       (218, 2025, 0.64),
    "greece":        (197, 2025, 0.64),
    "croatia":       (210, 2025, 0.60),
}
LEAGUE_TAG = {"premierleague": "ENG", "laliga": "ESP", "seriea_italy": "ITA",
              "bundesliga": "GER", "ligue1": "FRA", "primeiraliga": "POR",
              "eredivisie": "NED", "brazil_seriea": "BRA", "belgium": "BEL",
              "championship": "ENG2", "turkey": "TUR", "argentina": "ARG",
              "liga_mx": "MEX", "mls": "MLS", "scotland": "SCO",
              "switzerland": "SUI", "saudi": "SAU", "austria": "AUT",
              "greece": "GRE", "croatia": "CRO"}

# Three-component form blend: club season + club recent + country (international).
# Weights are the MAX share each can take; recent/country are scaled down for small
# samples, then the present components are renormalised to sum to 1.
# Four form windows. Once the WC is under way the ACTUAL tournament form is the
# strongest signal, so it carries the largest base weight — but it's sample-weighted,
# so 1-2 games don't dominate; its influence grows as WC minutes accumulate.
SEASON_WEIGHT = 0.30
CLUB_RECENT_WEIGHT = 0.15
COUNTRY_WEIGHT = 0.10
WC_WEIGHT = 0.45
MIN_RECENT_MINUTES = 180             # ignore club recent below ~2 games (per-90 noise)
FULL_RECENT_MINUTES = 540           # club recent earns full weight at ~6 games
MIN_COUNTRY_MINUTES = 45            # count from ~1 cap/half (nations rest stars in friendlies)
FULL_COUNTRY_MINUTES = 270          # country form earns full weight at ~3 internationals
MIN_WC_MINUTES = 30                 # count actual WC form from ~30 minutes played
FULL_WC_MINUTES = 270              # WC form earns full weight at ~3 WC games
INTL_LAST_FIXTURES = 8              # national matches to pull per nation for country form


def blend_forms(season_xp, recent_xp, recent_min, country_xp, country_min,
                wc_xp=None, wc_min=None):
    """Sample-weighted blend of club-season + club-recent + country + actual-WC xPts."""
    parts = [(season_xp, SEASON_WEIGHT)]
    if recent_xp is not None and (recent_min or 0) >= MIN_RECENT_MINUTES:
        parts.append((recent_xp, CLUB_RECENT_WEIGHT * min(recent_min / FULL_RECENT_MINUTES, 1.0)))
    if country_xp is not None and (country_min or 0) >= MIN_COUNTRY_MINUTES:
        parts.append((country_xp, COUNTRY_WEIGHT * min(country_min / FULL_COUNTRY_MINUTES, 1.0)))
    if wc_xp is not None and (wc_min or 0) >= MIN_WC_MINUTES:
        parts.append((wc_xp, WC_WEIGHT * min(wc_min / FULL_WC_MINUTES, 1.0)))
    total = sum(w for _, w in parts)
    return sum(v * w for v, w in parts) / total if total else season_xp


# --- candidate building ---------------------------------------------------

def wc_adjusted_start(club_start: float, wf) -> tuple[float, float]:
    """
    Correct a player's start probability using ACTUAL WC lineups. Club minutes are
    only a prior; once the tournament starts, who actually started for their COUNTRY
    is the truth (e.g. Guéhi: club-nailed but a 10-minute sub for England). Blend the
    club prior (~1 game of weight) with the real WC start rate.
    Returns (start_prob, p_sixty).
    """
    if not wf or wf.appearances <= 0:
        return club_start, club_start * 0.95
    wc_rate = wf.lineups / wf.appearances
    eff = (1.0 * club_start + wf.appearances * wc_rate) / (1.0 + wf.appearances)
    # p_sixty from actual minutes-per-appearance (gates clean-sheet points)
    mpa = wf.minutes / wf.appearances
    p60 = round(eff * min(1.0, mpa / 75.0), 3)
    return round(eff, 3), p60


def build_candidates(api: ApiFootball, min_minutes: int, recent_n: int,
                     national: dict[str, dict], fifa: dict,
                     wc_forms: dict | None = None) -> list[dict]:
    """One row per qualifying club player (WC nation, strong league), pre-intl-filter."""
    candidates: list[dict] = []
    for stem, (league, season, strength) in POOL.items():
        print(f"  [{stem}] gathering season + last-{recent_n} form ...", flush=True)
        defense = defense_lookup(api, league, season)
        recent = recent_forms(api, league, season, recent_n, defense) if recent_n else {}
        entries = api.player_stats_paginated(league=league, season=season)

        for entry in entries:
            form = extract_player_form(entry)
            if not form or form.minutes < min_minutes:
                continue
            nation = canonical_nation(form.nationality)
            if not nation:                     # not a WC2026 nation -> irrelevant
                continue

            # FIFA Fantasy is the AUTHORITATIVE universe: a player must exist in the game,
            # and FIFA's position + price are authoritative. Drop anyone not in the list
            # (removes club players mis-matched into a WC nation, e.g. non-squad "Gabriels").
            # Match by name; use the club (API) position as a TIEBREAKER to disambiguate
            # same-surname, same-initial players (Lisandro vs Lautaro vs Lucas Martínez).
            # FIFA position still wins for the final classification (set below).
            fm = match_price(fifa, nation, form.name, form.position)
            if fifa and not fm:
                continue
            fifa_id = price = ownership = None
            if fm:
                fifa_id = fm.get("id")
                if fm.get("position"):
                    form.position = fm["position"]   # apply BEFORE scoring (DEF CS +5 vs MID +1)
                price, ownership = fm.get("price"), fm.get("ownership")

            apply_set_pieces(form, nation)     # national set-piece duty (real WC threat)

            # Correct start probability with ACTUAL WC lineups (a sub like Guéhi gets
            # cut down even if club-nailed). Done BEFORE scoring so it shades everything.
            if wc_forms:
                form.start_prob, form.p_sixty = wc_adjusted_start(
                    form.start_prob, wc_forms.get(form.player_id))

            # International clean-sheet + group fixture difficulty for this nation.
            nc = context_for(national, nation)
            ctx = FixtureContext(clean_sheet_prob=nc["clean_sheet_prob"],
                                 expected_goals_against=nc["expected_goals_against"],
                                 attack_multiplier=nc["attack_multiplier"],
                                 team_attack=nc.get("team_attack", 1.0),
                                 start_prob=form.start_prob, p_sixty=form.p_sixty)
            season_xp = form_to_xpts(form, ctx)

            rf = recent.get(form.player_id)
            recent_xp = recent_min = None
            if rf and rf[0].minutes >= MIN_RECENT_MINUTES:
                rform = rf[0]
                rform.position = form.position  # use FIFA position for recent too
                rform.sp_pen_rank, rform.sp_fk_rank, rform.sp_corner_rank = (
                    form.sp_pen_rank, form.sp_fk_rank, form.sp_corner_rank)
                recent_xp = form_to_xpts(rform, ctx)
                recent_min = rform.minutes

            # Country form is attached later (attach_country_form); provisional blend now.
            blended = blend_forms(season_xp, recent_xp, recent_min, None, None)

            candidates.append({
                "form": form, "nation": nation, "league_tag": LEAGUE_TAG[stem],
                "strength": strength, "ctx": ctx,
                "season_xp": season_xp, "recent_xp": recent_xp, "recent_min": recent_min,
                "country_xp": None, "country_min": None, "wc_xp": None, "wc_min": None,
                "blended_xp": blended, "final_xp": round(blended * strength, 2),
                "cs": nc["clean_sheet_prob"], "diff": nc["attack_multiplier"],
                "opponents": nc.get("opponents", []),
                "price": price, "ownership": ownership, "value": None,
                "fifa_id": fifa_id,
            })
    return candidates


def dedupe_by_fifa(rows: list[dict]) -> list[dict]:
    """One row per real FIFA player: if several club players matched the same FIFA
    entry (mononym collisions, e.g. Carlos Vinícius vs Vinícius Júnior), keep the
    highest-projected one."""
    best: dict[int, dict] = {}
    passthrough = []
    for c in rows:
        fid = c.get("fifa_id")
        if fid is None:
            passthrough.append(c)
            continue
        if fid not in best or c["final_xp"] > best[fid]["final_xp"]:
            best[fid] = c
    return list(best.values()) + passthrough


def apply_starter_filter(candidates: list[dict], wc_forms: dict | None = None):
    """
    Keep only players in their nation's probable WC starting XI. A probable-XI entry is
    often a bare surname ("Romero"), so two squad-mates can match the same slot (Cristian
    AND Zaid Romero). Keep ONE player per (nation, XI slot): the genuine starter, judged
    by FIFA ownership (the template pick) then projection. Drops depth-player lookalikes.

    Once the tournament is live, ACTUAL WC lineups override the pre-tournament prediction:
    any player who has genuinely started a completed WC match (per `wc_forms`) is admitted
    even if the published probable-XI list missed him (e.g. Isak, Undav, Elijah Just). This
    is the same "real lineups are the truth" principle as wc_adjusted_start — without it,
    such players fall back to FIFA's avgPoints and their projection never moves past round 1.
    """
    matched = []
    for c in candidates:
        rank = xi_rank(c["nation"], c["form"].name)
        if rank is None:
            continue
        c["xi_rank"] = rank
        matched.append(c)

    def starter_score(c):
        return (c.get("ownership") if c.get("ownership") is not None else -1.0, c["final_xp"])

    best: dict[tuple, dict] = {}
    for c in matched:
        key = (c["nation"], c["xi_rank"])
        if key not in best or starter_score(c) > starter_score(best[key]):
            best[key] = c
    survivors = list(best.values())

    # WC-actual-starter bypass: admit anyone with a real WC start the probable XI missed.
    if wc_forms:
        seen = {id(c) for c in survivors}
        for c in candidates:
            if id(c) in seen:
                continue
            wf = wc_forms.get(c["form"].player_id)
            if wf and wf.lineups >= 1:          # actually started a completed WC match
                survivors.append(c)
                seen.add(id(c))

    n_nations = len({c["nation"] for c in survivors})
    return survivors, n_nations


def attach_country_form(api: ApiFootball, rows: list[dict], verbose: bool = True) -> int:
    """
    Pull recent INTERNATIONAL form for the nations present in `rows`, blend it into
    each player's projection (as the 3rd form component), and recompute final_xp.
    Mutates rows. Returns the number of players that got a country-form value.
    """
    nations = sorted({c["nation"] for c in rows})
    name_to_id, _ = wc_team_ids(api)
    nation_to_id = {n: name_to_id[n] for n in nations if n in name_to_id}
    if verbose:
        print(f"  pulling international form for {len(nation_to_id)} nations "
              f"(last {INTL_LAST_FIXTURES} matches each)...", flush=True)
    country = build_country_forms(api, nation_to_id, last=INTL_LAST_FIXTURES)

    n_with = 0
    for c in rows:
        cf = country.get(c["form"].player_id)
        if cf and cf.minutes >= MIN_COUNTRY_MINUTES:
            # carry the player's FIFA position + national set-piece duty onto the intl
            # form, then score it in the same national context as the rest of his projection.
            cf.position = c["form"].position
            cf.sp_pen_rank = c["form"].sp_pen_rank
            cf.sp_fk_rank = c["form"].sp_fk_rank
            cf.sp_corner_rank = c["form"].sp_corner_rank
            # Country form already reflects the player's weak/strong side, so don't
            # re-apply the team-attack discount to it (avoid double-counting).
            intl_ctx = replace(c["ctx"], team_attack=1.0)
            c["country_xp"] = form_to_xpts(cf, intl_ctx)
            c["country_min"] = cf.minutes
            n_with += 1
    return n_with


def attach_wc_form(rows: list[dict], wc: dict) -> int:
    """
    Blend in ACTUAL World Cup 2026 form (the strongest in-tournament signal). Uses the
    pre-pulled WC forms, matches by global player_id, scores in the player's national
    context (team_attack=1.0 — it's real output), and stores wc_xp/wc_min.
    Returns the number of players who have WC minutes.
    """
    n_with = 0
    for c in rows:
        wf = wc.get(c["form"].player_id)
        if wf and wf.minutes >= MIN_WC_MINUTES:
            wf.position = c["form"].position
            wf.sp_pen_rank, wf.sp_fk_rank, wf.sp_corner_rank = (
                c["form"].sp_pen_rank, c["form"].sp_fk_rank, c["form"].sp_corner_rank)
            intl_ctx = replace(c["ctx"], team_attack=1.0)
            c["wc_xp"] = form_to_xpts(wf, intl_ctx)
            c["wc_min"] = wf.minutes
            n_with += 1
    return n_with


def recompute_finals(rows: list[dict]) -> None:
    """Blend all four form windows and set blended_xp / final_xp / value. Mutates rows."""
    for c in rows:
        blended = blend_forms(c["season_xp"], c["recent_xp"], c["recent_min"],
                              c["country_xp"], c["country_min"],
                              c.get("wc_xp"), c.get("wc_min"))
        c["blended_xp"] = blended
        c["final_xp"] = round(blended * c["strength"], 2)
        c["value"] = (round(c["final_xp"] / c["price"], 2) if c.get("price") else None)


# --- rendering ------------------------------------------------------------

def _table(rows: list[dict], pos: str, top: int, sort_label: str = "final xPts") -> str:
    subset = [r for r in rows if r["form"].position == pos][:top]
    header = (f"{'xPts':>5}  {'Player':<20} {'Nation':<14} {'Club':<14} {'Lg':<4} "
              f"{'$':>5} {'Own%':>6} {'Val':>5} {'sXP':>5} {'rXP':>5} {'cXP':>5} {'wXP':>5} "
              f"{'CS%':>4} {'Dif':>4} {'SP':<9}")
    lines = [f"=== Top {top} {pos} (WC2026 expected points; sorted by {sort_label}) ===",
             header, "-" * len(header)]
    for i, c in enumerate(subset, 1):
        f = c["form"]
        sp = ""
        if f.sp_pen_rank or f.sp_fk_rank or f.sp_corner_rank:
            sp = " ".join(t for t in (
                f"P{f.sp_pen_rank}" if f.sp_pen_rank else "",
                f"FK{f.sp_fk_rank}" if f.sp_fk_rank else "",
                f"C{f.sp_corner_rank}" if f.sp_corner_rank else "") if t)
        price = f"{c['price']:.1f}" if c.get("price") else "-"
        own = c.get("ownership")
        own_s = (f"{own:.1f}*" if (own is not None and own < 5.0) else
                 f"{own:.1f}" if own is not None else "-")   # * = differential (<5%)
        val = f"{c['value']:.2f}" if c.get("value") is not None else "-"
        rxp = f"{c['recent_xp']:.2f}" if c.get("recent_xp") is not None else "-"
        cxp = f"{c['country_xp']:.2f}" if c.get("country_xp") is not None else "-"
        wxp = f"{c['wc_xp']:.2f}" if c.get("wc_xp") is not None else "-"
        lines.append(
            f"{i:>2}  {c['final_xp']:>5.2f}  {f.name[:20]:<20} {c['nation'][:14]:<14} "
            f"{f.team[:14]:<14} {c['league_tag']:<4} "
            f"{price:>5} {own_s:>6} {val:>5} {c['season_xp']:>5.2f} {rxp:>5} {cxp:>5} {wxp:>5} "
            f"{c['cs']*100:>3.0f}% {c['diff']:>4.2f} {sp:<9}")
    return "\n".join(lines)


def build_priced_survivors(api: ApiFootball, min_minutes: int = 600, recent: int = 40,
                           verbose: bool = True, refresh: bool = False) -> list[dict]:
    """Cached wrapper: build the full priced survivor pool once, reuse from disk after.
    Pass refresh=True (or delete .pool_cache.pkl) to rebuild from the API."""
    if not refresh and POOL_CACHE.exists():
        try:
            surv = pickle.loads(POOL_CACHE.read_bytes())
            age_min = (time.time() - POOL_CACHE.stat().st_mtime) / 60
            if verbose:
                print(f"  using cached player pool ({len(surv)} players, {age_min:.0f} min old; "
                      f"--refresh to rebuild)", flush=True)
            return surv
        except Exception:
            pass
    surv = _build_priced_survivors(api, min_minutes, recent, verbose)
    try:
        POOL_CACHE.write_bytes(pickle.dumps(surv))
    except Exception:
        pass
    return surv


def incremental_refresh(api: ApiFootball, surv: list[dict], verbose: bool = True) -> list[dict]:
    """
    Cheap daily update of an already-built pool.

    During the tournament the expensive windows are STATIC — club-season form (clubs are
    done) and international friendly form (none are played mid-tournament). Only two things
    move day to day: the actual WC output, and the fixture context (next opponent, fixture
    difficulty, clean-sheet odds, team strength shifting with new goals). So we re-pull only
    those (~50 calls vs several hundred for a full rebuild), re-score the WC + season windows
    in the fresh context, and re-blend. Mutates and re-persists `surv`.
    """
    if verbose:
        print("  incremental: refreshing fixtures + national context...", flush=True)
    national = build_national_context(api)
    for c in surv:
        nc = context_for(national, c["nation"])
        ctx = FixtureContext(
            clean_sheet_prob=nc["clean_sheet_prob"],
            expected_goals_against=nc["expected_goals_against"],
            attack_multiplier=nc["attack_multiplier"],
            team_attack=nc.get("team_attack", 1.0),
            start_prob=c["form"].start_prob, p_sixty=c["form"].p_sixty)
        c["ctx"] = ctx
        c["cs"] = nc["clean_sheet_prob"]
        c["diff"] = nc["attack_multiplier"]
        c["opponents"] = nc.get("opponents", [])
        c["season_xp"] = form_to_xpts(c["form"], ctx)   # re-score in the fresh fixture context

    if verbose:
        print("  incremental: refreshing WC tournament form...", flush=True)
    wc = build_wc_forms(api)
    n = attach_wc_form(surv, wc)                          # re-score the WC window
    recompute_finals(surv)                                # re-blend all four windows
    if verbose:
        print(f"  incremental: {n} players with WC minutes; projections re-blended.", flush=True)

    try:
        POOL_CACHE.write_bytes(pickle.dumps(surv))
    except Exception:
        pass
    return surv


def _build_priced_survivors(api: ApiFootball, min_minutes: int = 600, recent: int = 40,
                            verbose: bool = True) -> list[dict]:
    """Full pipeline -> probable WC starters with final_xp, price, ownership, value.
    Shared by the shortlist CLI and the squad optimiser."""
    def log(msg):
        if verbose:
            print(msg, flush=True)

    log("Building national-team strength + group fixture-difficulty model...")
    try:
        national = build_national_context(api)
    except ApiFootballError as e:
        log(f"  national context unavailable ({e}); using neutral defaults")
        national = {}

    log("Loading FIFA Fantasy data (authoritative position + price/ownership)...")
    try:
        fifa = load_fifa_players()
    except FifaFantasyError as e:
        log(f"  FIFA Fantasy data unavailable ({e}); using API positions, no price")
        fifa = {}

    log("Pulling ACTUAL WC2026 tournament form (also corrects start probabilities)...")
    try:
        wc_forms = build_wc_forms(api)
    except ApiFootballError as e:
        log(f"  WC form unavailable ({e})")
        wc_forms = {}

    log("Building candidate pool + filtering to probable WC starters...")
    candidates = build_candidates(api, min_minutes, recent, national, fifa, wc_forms)
    survivors, _ = apply_starter_filter(candidates, wc_forms)

    log("Blending in international (country) form...")
    try:
        n_country = attach_country_form(api, survivors, verbose=verbose)
        log(f"  country form applied to {n_country}/{len(survivors)} players")
    except ApiFootballError as e:
        log(f"  country form unavailable ({e}); using club form only")

    n_wc = attach_wc_form(survivors, wc_forms)
    log(f"  WC form applied to {n_wc}/{len(survivors)} players")

    recompute_finals(survivors)   # blend all four windows -> final_xp + value

    # Dedupe mononym collisions to one row per real FIFA player.
    before = len(survivors)
    survivors = dedupe_by_fifa(survivors)
    if before != len(survivors):
        log(f"  deduped {before - len(survivors)} duplicate FIFA-player matches")
    return survivors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="WC2026 best-by-position shortlist")
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument("--min-minutes", type=int, default=600, help="club-season minutes filter")
    parser.add_argument("--recent", type=int, default=40, help="last-N league fixtures for form")
    parser.add_argument("--sort", choices=["points", "value"], default="points",
                        help="rank by expected points (default) or value (xPts per $m)")
    parser.add_argument("--max-price", type=float, default=None, help="only show players <= this price")
    parser.add_argument("--refresh", action="store_true",
                        help="rebuild the player pool from the API (else use .pool_cache.pkl)")
    parser.add_argument("--out", default="wc_shortlist.txt")
    args = parser.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    try:
        api = ApiFootball()
    except ApiFootballError as e:
        print(f"Setup error: {e}", file=sys.stderr)
        return 1

    survivors = build_priced_survivors(api, args.min_minutes, args.recent, refresh=args.refresh)
    print(f"  {len(survivors)} probable starters; "
          f"{sum(1 for c in survivors if c.get('price'))} with FIFA price")

    if args.max_price is not None:
        survivors = [c for c in survivors if c.get("price") and c["price"] <= args.max_price]

    if args.sort == "value":
        survivors.sort(key=lambda c: (c["value"] is not None, c["value"] or 0), reverse=True)
        sort_label = "value (xPts/$m)"
    else:
        survivors.sort(key=lambda c: c["final_xp"], reverse=True)
        sort_label = "final xPts"

    head = (f"WC2026 best by position - {sort_label} (league-strength x form, probable WC starters)\n"
            f"Pool: {', '.join(LEAGUE_TAG.values())} | club min {args.min_minutes}' | "
            f"form blend: season {int(SEASON_WEIGHT*100)}% / club-recent {int(CLUB_RECENT_WEIGHT*100)}% "
            f"(last-{args.recent}) / country {int(COUNTRY_WEIGHT*100)}% (last-{INTL_LAST_FIXTURES} intl), sample-weighted | "
            f"starter: probable WC2026 XI" + (f" | max price {args.max_price}" if args.max_price else "") + "\n"
            f"$ = FIFA price | Own% = ownership (* = differential <5%) | Val = final xPts per $m | "
            f"sXP = club season | rXP = club recent | cXP = country (intl) form | "
            f"CS% = national group clean-sheet | Dif = attacking fixture difficulty\n")
    body = "\n\n".join(_table(survivors, pos, args.top, sort_label) for pos in ("GK", "DEF", "MID", "FWD"))
    report = head + "\n" + body + "\n"

    Path(args.out).write_text(report, encoding="utf-8")
    print("\n" + report)
    print(f"[wrote {args.out}]  quota left: {api.requests_remaining}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
