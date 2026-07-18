"""
National-team strength + WC2026 fixture-difficulty model.

For World Cup picks the relevant clean-sheet context is the NATIONAL team's
defence against its actual group opponents — not the player's club. This module:

  1. Resolves the 48 WC team ids        -> /teams?league=1&season=2026
  2. Rates each nation's attack/defence -> /fixtures?team=<id>&last=N (GF/GA per game)
  3. Reads each team's group opponents  -> /fixtures?league=1&season=2026 (group stage)
  4. Produces per-nation:
       clean_sheet_prob       Poisson P(0 conceded) averaged over the 3 group games
       expected_goals_against expected goals conceded per group game
       attack_multiplier      fixture difficulty for attackers (opponents' defensive
                              weakness vs average; >1 = soft group, <1 = hard group)

Strength is a simple Dixon-Coles-style ratio model:
    exp goals (T vs O) = attack_strength[T] * defence_weakness[O] * global_avg

These are the published group draw + historical international results — not live
tournament data. Everything is cached 12h like all API calls.
"""

from __future__ import annotations

import math
from statistics import mean

from set_piece_takers import canonical_nation
from fifa_rankings import fifa_strength

FINISHED = {"FT", "AET", "PEN"}
DEFAULT_CONTEXT = {"clean_sheet_prob": 0.28, "expected_goals_against": 1.3,
                   "attack_multiplier": 1.0, "team_attack": 1.0}

# (B) WC-result blending: each played WC game shifts a rating this much toward the
# WC outcome, capped so the larger pre-tournament sample is never fully discarded.
WC_GAME_WEIGHT = 0.25
WC_RATE_CAP = 0.60


def wc_team_ids(api, league: int = 1, season: int = 2026) -> tuple[dict[str, int], dict[int, str]]:
    """(canonical nation -> team id, team id -> canonical nation) for the 48 teams."""
    name_to_id: dict[str, int] = {}
    id_to_name: dict[int, str] = {}
    for r in api.teams(league=league, season=season):
        t = r.get("team", {}) or {}
        tid, name = t.get("id"), t.get("name")
        if not tid or not name:
            continue
        key = canonical_nation(name) or name
        name_to_id[key] = tid
        id_to_name[tid] = key
    return name_to_id, id_to_name


def team_goal_rates(api, team_id: int, last: int = 15,
                    exclude_league: int = 1, exclude_season: int = 2026) -> dict | None:
    """
    {gf_pg, ga_pg, n} from a team's last finished internationals, or None.

    Excludes the WC2026 competition itself (exclude_league/season) so this is a
    clean PRE-tournament baseline — the actual WC results are folded back in
    separately (with extra weight) by wc_goal_rates()/build_national_context().
    """
    gf = ga = n = 0
    for f in api.fixtures(team=team_id, last=last):
        if (f.get("fixture", {}).get("status", {}) or {}).get("short") not in FINISHED:
            continue
        lg = f.get("league", {}) or {}
        if lg.get("id") == exclude_league and lg.get("season") == exclude_season:
            continue
        teams, goals = f.get("teams", {}) or {}, f.get("goals", {}) or {}
        hg, ag = goals.get("home"), goals.get("away")
        if hg is None or ag is None:
            continue
        if (teams.get("home", {}) or {}).get("id") == team_id:
            gf += hg; ga += ag
        else:
            gf += ag; ga += hg
        n += 1
    if n == 0:
        return None
    return {"gf_pg": gf / n, "ga_pg": ga / n, "n": n}


def wc_goal_rates(api, league: int = 1, season: int = 2026) -> dict[int, dict]:
    """
    team_id -> {gf_pg, ga_pg, n} from the WC2026 matches already played.

    These are the most relevant data points we have once the tournament is live,
    so build_national_context() blends them into each nation's attack/defence
    rating with extra per-game weight.
    """
    agg: dict[int, dict] = {}
    # force_refresh: the WC fixtures list gains results every matchday; the 12h cache
    # would otherwise freeze difficulty/clean-sheet blending at an earlier round.
    for f in api.fixtures(league=league, season=season, force_refresh=True):
        if (f.get("fixture", {}).get("status", {}) or {}).get("short") not in FINISHED:
            continue
        teams, goals = f.get("teams", {}) or {}, f.get("goals", {}) or {}
        hg, ag = goals.get("home"), goals.get("away")
        h = (teams.get("home", {}) or {}).get("id")
        a = (teams.get("away", {}) or {}).get("id")
        if hg is None or ag is None or not h or not a:
            continue
        for tid, gf, ga in ((h, hg, ag), (a, ag, hg)):
            d = agg.setdefault(tid, {"gf": 0, "ga": 0, "n": 0})
            d["gf"] += gf; d["ga"] += ga; d["n"] += 1
    return {tid: {"gf_pg": d["gf"] / d["n"], "ga_pg": d["ga"] / d["n"], "n": d["n"]}
            for tid, d in agg.items() if d["n"]}


def group_fixtures(api, league: int = 1, season: int = 2026) -> dict[int, list[dict]]:
    """
    team_id -> list of {opp, played, date} for its group-stage games, date-sorted.

    `played` flags finished games so the difficulty model can focus on the
    UPCOMING fixtures (and the imminent one above all).
    """
    fx: dict[int, list[dict]] = {}
    # force_refresh so `played` flags reflect the latest completed matchday.
    for f in api.fixtures(league=league, season=season, force_refresh=True):
        if "group" not in (f.get("league", {}).get("round", "") or "").lower():
            continue
        h = (f.get("teams", {}).get("home", {}) or {}).get("id")
        a = (f.get("teams", {}).get("away", {}) or {}).get("id")
        if not h or not a:
            continue
        played = (f.get("fixture", {}).get("status", {}) or {}).get("short") in FINISHED
        date = (f.get("fixture", {}) or {}).get("date", "")
        fx.setdefault(h, []).append({"opp": a, "played": played, "date": date})
        fx.setdefault(a, []).append({"opp": h, "played": played, "date": date})
    for games in fx.values():
        games.sort(key=lambda g: g["date"])
    return fx


# Difficulty weighting: the next unplayed group game dominates; the rest of the
# remaining group shares the balance.
NEXT_FIXTURE_WEIGHT = 0.6


def upcoming_opponent_weights(games: list[dict]) -> list[tuple[int, float]]:
    """[(opponent_id, weight)] over a team's UNPLAYED group games, weights summing to 1."""
    upcoming = [g for g in games if not g["played"]]
    if not upcoming:
        return []
    if len(upcoming) == 1:
        return [(upcoming[0]["opp"], 1.0)]
    nxt, rest = upcoming[0], upcoming[1:]
    rest_w = (1.0 - NEXT_FIXTURE_WEIGHT) / len(rest)
    return [(nxt["opp"], NEXT_FIXTURE_WEIGHT)] + [(g["opp"], rest_w) for g in rest]


def build_national_context(api, last: int = 15) -> dict[str, dict]:
    """
    canonical nation -> {clean_sheet_prob, expected_goals_against, attack_multiplier,
                         gf_pg, ga_pg, n_games, opponents}.
    """
    name_to_id, id_to_name = wc_team_ids(api)

    # (B) Fold the already-played WC2026 results into each nation's rating. The WC
    # sample is tiny early on, so weight it per-game (WC_GAME_WEIGHT each) against
    # the pre-tournament baseline and cap its total share so a single shock result
    # can't fully rewrite a rating.
    wc_rates = wc_goal_rates(api)

    def blend_rate(hist: dict | None, tid: int) -> dict | None:
        wc = wc_rates.get(tid)
        if hist and wc:
            w = min(WC_RATE_CAP, WC_GAME_WEIGHT * wc["n"])
            return {
                "gf_pg": (1 - w) * hist["gf_pg"] + w * wc["gf_pg"],
                "ga_pg": (1 - w) * hist["ga_pg"] + w * wc["ga_pg"],
                "n": hist["n"], "wc_n": wc["n"],
            }
        if wc:  # no historical baseline: use WC alone
            return {**wc, "n": 0, "wc_n": wc["n"]}
        return hist

    rates: dict[str, dict] = {}
    for nation, tid in name_to_id.items():
        r = blend_rate(team_goal_rates(api, tid, last), tid)
        if r:
            rates[nation] = r

    # Normalise attack and defence by their OWN averages (qualifying blowouts make
    # goals-for >> goals-against in these samples, so a single average distorts).
    a_avg = max(0.4, mean(r["gf_pg"] for r in rates.values())) if rates else 1.3
    d_avg = max(0.4, mean(r["ga_pg"] for r in rates.values())) if rates else 1.1

    strength = {
        nation: {"attack": r["gf_pg"] / a_avg, "defence_weak": r["ga_pg"] / d_avg, **r}
        for nation, r in rates.items()
    }

    try:
        gfx = group_fixtures(api)
    except Exception:
        gfx = {}

    # Team-attack factor = 50% FIFA world-ranking strength + 50% recent goals-for rate.
    # Discounts a great player in a weak side (fewer chances). Normalised to mean 1.0.
    fifa = fifa_strength()
    raw_ta = {n: 0.5 * fifa.get(n, 1.0) + 0.5 * s["attack"] for n, s in strength.items()}
    ta_mean = mean(raw_ta.values()) if raw_ta else 1.0

    out: dict[str, dict] = {}
    for nation, s in strength.items():
        tid = name_to_id.get(nation)
        # (A) Weight by the UPCOMING group games, next fixture heaviest. Already-played
        # games carry no fixture difficulty (they're done); fall back to whole-group
        # average only if this nation's fixtures didn't resolve at all.
        weights = upcoming_opponent_weights(gfx.get(tid, []))
        weighted = [(id_to_name.get(o), w) for o, w in weights if id_to_name.get(o) in strength]
        if not weighted:
            allg = gfx.get(tid, [])
            weighted = [(id_to_name.get(g["opp"]), 1.0 / len(allg)) for g in allg
                        if id_to_name.get(g["opp"]) in strength] if allg else []

        if weighted:
            cs = xga = attack_mult = 0.0
            for onat, w in weighted:
                o = strength[onat]
                # goals O is expected to score vs T = O's attack x T's defensive weakness
                exp_conceded = o["attack"] * s["defence_weak"] * d_avg
                cs += w * math.exp(-exp_conceded)
                xga += w * exp_conceded
                attack_mult += w * o["defence_weak"]    # weak opp defences (>1) -> easier
            next_opp = weighted[0][0]
        else:  # no fixtures resolved: CS from own defence, neutral difficulty
            exp_conceded = s["defence_weak"] * d_avg
            cs, xga, attack_mult, next_opp = math.exp(-exp_conceded), exp_conceded, 1.0, None

        out[nation] = {
            "clean_sheet_prob": round(cs, 3),
            "expected_goals_against": round(xga, 3),
            "attack_multiplier": round(max(0.6, min(1.5, attack_mult)), 3),
            "team_attack": round(max(0.75, min(1.25, raw_ta[nation] / ta_mean)), 3),
            "gf_pg": round(s["gf_pg"], 2),
            "ga_pg": round(s["ga_pg"], 2),
            "n_games": s["n"],
            "wc_games": s.get("wc_n", 0),
            "next_opponent": next_opp,
            "opponents": sorted(n for n, _ in weighted),
        }
    return out


def context_for(national: dict[str, dict], nation: str) -> dict:
    return national.get(nation, DEFAULT_CONTEXT)
