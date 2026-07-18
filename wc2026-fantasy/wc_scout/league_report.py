"""
Generate the per-league fantasy scouting reports (the .txt files).

Each league has its own output file. Re-running refreshes the file with the full
data the current pipeline pulls: per-90 rates, minutes/start security, saves,
cards, clean-sheet model, injuries — all scored under the WC2026 ruleset.

    setx API_FOOTBALL_KEY "your_key"        # or put it in .env
    python league_report.py                 # refresh ALL leagues
    python league_report.py --only premierleague laliga
    python league_report.py --top 30 --min-minutes 270

Responses are cached (12h) to .api_cache/, so a re-run within the day is cheap.
"""

from __future__ import annotations

import argparse
import datetime
import math
import sys

from api_football import ApiFootball, ApiFootballError
from scoring import FixtureContext
from player_form import PlayerForm, extract_player_form, form_to_xpts

# filename stem -> (league id, season, human title)
LEAGUES: dict[str, tuple[int, int, str]] = {
    "premierleague":   (39,  2025, "Premier League (England)"),
    "laliga":          (140, 2025, "La Liga (Spain)"),
    "seriea_italy":    (135, 2025, "Serie A (Italy)"),
    "bundesliga":      (78,  2025, "Bundesliga (Germany)"),
    "ligue1":          (61,  2025, "Ligue 1 (France)"),
    "eredivisie":      (88,  2025, "Eredivisie (Netherlands)"),
    "primeiraliga":    (94,  2025, "Primeira Liga (Portugal)"),
    "belgium":         (144, 2025, "Pro League (Belgium)"),
    "superlig_turkey": (203, 2025, "Süper Lig (Türkiye)"),
    "brazil_seriea":   (71,  2025, "Série A (Brazil)"),
    "euro2024":        (4,   2024, "UEFA Euro 2024"),
    "saudi":           (307, 2025, "Pro League (Saudi Arabia)"),
}


# --- data gathering -------------------------------------------------------

def defense_lookup(api: ApiFootball, league: int, season: int) -> dict[int, dict]:
    """team_id -> {clean_sheet_prob, expected_goals_against} via Poisson on GA/game."""
    out: dict[int, dict] = {}
    for entry in api.standings(league=league, season=season):
        for group in entry.get("league", {}).get("standings", []) or []:
            for row in group:
                tid = row.get("team", {}).get("id")
                allp = row.get("all", {}) or {}
                played = allp.get("played") or 0
                against = (allp.get("goals", {}) or {}).get("against") or 0
                if not tid:
                    continue
                if played == 0:
                    out[tid] = {"clean_sheet_prob": 0.30, "expected_goals_against": 1.2}
                else:
                    xga = against / played
                    out[tid] = {"clean_sheet_prob": round(math.exp(-xga), 3),
                                "expected_goals_against": round(xga, 3)}
    return out


def injured_ids(api: ApiFootball, league: int, season: int) -> set[int]:
    return {
        (r.get("player", {}) or {}).get("id")
        for r in api.injuries(league=league, season=season)
        if (r.get("player", {}) or {}).get("id")
    }


def gather(api: ApiFootball, league: int, season: int, min_minutes: int, recent: int = 0):
    defense = defense_lookup(api, league, season)
    injured = injured_ids(api, league, season)
    entries = api.player_stats_paginated(league=league, season=season)

    recent_map: dict[int, tuple] = {}
    if recent > 0:
        from recent_form import recent_forms
        recent_map = recent_forms(api, league, season, recent, defense)

    scored: list[tuple[PlayerForm, float, dict, bool]] = []
    for entry in entries:
        form = extract_player_form(entry)
        if not form or form.minutes < min_minutes:
            continue
        d = defense.get(form.team_id, {"clean_sheet_prob": 0.30, "expected_goals_against": 1.2})
        ctx = FixtureContext(
            clean_sheet_prob=d["clean_sheet_prob"],
            expected_goals_against=d["expected_goals_against"],
            start_prob=form.start_prob,
            p_sixty=form.p_sixty,
        )
        xp = form_to_xpts(form, ctx)
        # Attach recent-form (None if not requested / player absent from window).
        rf = recent_map.get(form.player_id)
        form.recent_xp = rf[1] if rf else None
        form.recent_games = rf[0].appearances if rf else None
        scored.append((form, xp, d, form.player_id in injured))
    return scored, len(entries), len(defense), len(injured)


# --- rendering ------------------------------------------------------------

def _pk_cell(f, xp, d, i) -> str:
    """Penalties scored/attempted; '*' marks a designated taker (2+ attempts)."""
    if f.pen_attempts == 0:
        return "-"
    return f"{f.pen_scored}/{f.pen_attempts}" + ("*" if f.pen_taker else "")


def _recent_xp_cell(f, xp, d, i) -> str:
    return "-" if getattr(f, "recent_xp", None) is None else f"{f.recent_xp:.2f}"


def _recent_gp_cell(f, xp, d, i) -> str:
    g = getattr(f, "recent_games", None)
    return "-" if not g else str(g)


# Per-position column layouts: (header, width, value-fn taking (form, xp, d, inj))
def _cols(pos: str, recent: bool = False):
    common = [
        ("xPts", 5, lambda f, xp, d, i: f"{xp:.2f}"),
        ("Player", 22, lambda f, xp, d, i: f.name[:22]),
        ("Team", 16, lambda f, xp, d, i: f.team[:16]),
        ("Ap", 3, lambda f, xp, d, i: f.appearances),
        ("Min", 5, lambda f, xp, d, i: f.minutes),
        ("St%", 4, lambda f, xp, d, i: f"{f.start_prob*100:.0f}"),
    ]
    if pos == "GK":
        extra = [
            ("Sv", 4, lambda f, xp, d, i: f.saves),
            ("Sv/90", 5, lambda f, xp, d, i: f"{f.per90['saves']:.2f}"),
            ("GC", 3, lambda f, xp, d, i: f.goals_conceded),
            ("PSv", 3, lambda f, xp, d, i: f.pen_saved),
            ("CS%", 4, lambda f, xp, d, i: f"{d['clean_sheet_prob']*100:.0f}"),
        ]
    elif pos == "DEF":
        extra = [
            ("G", 2, lambda f, xp, d, i: f.goals),
            ("A", 2, lambda f, xp, d, i: f.assists),
            ("Tk/90", 5, lambda f, xp, d, i: f"{f.per90['tackles']:.2f}"),
            ("GC", 3, lambda f, xp, d, i: f.goals_conceded),
            ("CS%", 4, lambda f, xp, d, i: f"{d['clean_sheet_prob']*100:.0f}"),
            ("PK", 5, _pk_cell),
            ("YC", 3, lambda f, xp, d, i: f.yellows),
        ]
    elif pos == "MID":
        extra = [
            ("G", 2, lambda f, xp, d, i: f.goals),
            ("A", 2, lambda f, xp, d, i: f.assists),
            ("G/90", 5, lambda f, xp, d, i: f"{f.per90['goals']:.2f}"),
            ("A/90", 5, lambda f, xp, d, i: f"{f.per90['assists']:.2f}"),
            ("KP/90", 5, lambda f, xp, d, i: f"{f.per90['key_passes']:.2f}"),
            ("Sh/90", 5, lambda f, xp, d, i: f"{f.per90['shots_total']:.2f}"),
            ("Tk/90", 5, lambda f, xp, d, i: f"{f.per90['tackles']:.2f}"),
            ("PK", 5, _pk_cell),
            ("YC", 3, lambda f, xp, d, i: f.yellows),
        ]
    else:  # FWD
        extra = [
            ("G", 2, lambda f, xp, d, i: f.goals),
            ("A", 2, lambda f, xp, d, i: f.assists),
            ("G/90", 5, lambda f, xp, d, i: f"{f.per90['goals']:.2f}"),
            ("A/90", 5, lambda f, xp, d, i: f"{f.per90['assists']:.2f}"),
            ("Sh/90", 5, lambda f, xp, d, i: f"{f.per90['shots_total']:.2f}"),
            ("SoT/90", 6, lambda f, xp, d, i: f"{f.per90['shots_on']:.2f}"),
            ("PK", 5, _pk_cell),
            ("YC", 3, lambda f, xp, d, i: f.yellows),
        ]
    tail = [
        ("Rt", 4, lambda f, xp, d, i: f"{f.rating:.1f}"),
        ("Inj", 3, lambda f, xp, d, i: "Y" if i else "-"),
    ]
    recent_cols = [
        ("rXP", 5, _recent_xp_cell),   # recent xPts/match over the last-N window
        ("rGp", 3, _recent_gp_cell),   # games played in that window
    ] if recent else []
    return common + extra + tail + recent_cols


def _render_table(rows, pos: str, top: int, recent: bool = False) -> str:
    cols = _cols(pos, recent)
    subset = [r for r in rows if r[0].position == pos][:top]
    head = "  ".join(f"{name:<{w}}" if name in ("Player", "Team") else f"{name:>{w}}"
                      for name, w, _ in cols)
    lines = [f"=== Top {pos} (by xPts/match) ===", head, "-" * len(head)]
    for form, xp, d, inj in subset:
        cells = []
        for name, w, fn in cols:
            val = str(fn(form, xp, d, inj))
            cells.append(f"{val:<{w}}" if name in ("Player", "Team") else f"{val:>{w}}")
        lines.append("  ".join(cells))
    return "\n".join(lines)


def render_report(title, league, season, scored, n_entries, n_teams, n_inj,
                  top, min_minutes, requests_remaining, recent=0) -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    header = [
        f"{title}  -  league {league}, season {season}",
        f"Generated {now} | scoring: WC2026 Fantasy ruleset | xPts = expected points/match",
        f"Clean-sheet model: Poisson on standings GA/game ({n_teams} teams) | "
        f"player-stat entries: {n_entries} | players with injury records this season: {n_inj}",
        f"Filter: minutes >= {min_minutes} | showing top {top} per position | "
        f"St% = start prob (lineups/apps) | PK = pens scored/attempted, * = designated taker | "
        f"Inj = Y if listed in this season's injuries/suspensions (history, not live status)",
    ]
    if recent:
        header.append(f"rXP/rGp = recent xPts/match and games played over the last {recent} "
                      f"league fixtures (current form vs season xPts)")
    header.append("")
    body = "\n\n".join(_render_table(scored, pos, top, recent=bool(recent))
                       for pos in ("GK", "DEF", "MID", "FWD"))
    footer = ""
    if requests_remaining is not None:
        footer = f"\n\n[API requests remaining today: {requests_remaining}]"
    return "\n".join(header) + body + footer + "\n"


# --- driver ---------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Generate per-league fantasy reports")
    parser.add_argument("--only", nargs="*", help="subset of league stems (default: all)")
    parser.add_argument("--top", type=int, default=25)
    parser.add_argument("--min-minutes", type=int, default=90)
    parser.add_argument("--recent", type=int, default=0, metavar="N",
                        help="also compute recent-form xPts over the last N league fixtures "
                             "(costs ~N+1 extra API requests per league; 0 = off)")
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args(argv)

    targets = args.only or list(LEAGUES)
    unknown = [t for t in targets if t not in LEAGUES]
    if unknown:
        print(f"Unknown league stem(s): {unknown}\nKnown: {list(LEAGUES)}", file=sys.stderr)
        return 1

    try:
        api = ApiFootball(use_cache=not args.no_cache)
    except ApiFootballError as e:
        print(f"Setup error: {e}", file=sys.stderr)
        return 1

    for stem in targets:
        league, season, title = LEAGUES[stem]
        print(f"[{stem}] league {league} season {season} ...", flush=True)
        try:
            scored, n_entries, n_teams, n_inj = gather(
                api, league, season, args.min_minutes, recent=args.recent)
        except ApiFootballError as e:
            print(f"  FAILED: {e}", file=sys.stderr)
            continue
        scored.sort(key=lambda r: r[1], reverse=True)
        report = render_report(title, league, season, scored, n_entries, n_teams,
                               n_inj, args.top, args.min_minutes, api.requests_remaining,
                               recent=args.recent)
        with open(f"{stem}.txt", "w", encoding="utf-8") as f:
            f.write(report)
        print(f"  wrote {stem}.txt ({n_entries} entries, {len(scored)} qualified)"
              f"  quota left: {api.requests_remaining}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
