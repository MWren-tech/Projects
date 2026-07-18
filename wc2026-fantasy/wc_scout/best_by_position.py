"""
Combined cross-league ranking: the best players by position across every league
in league_report.LEAGUES, scored under the WC2026 ruleset.

xPts is per-match and uses the same model everywhere, so it's comparable across
leagues. A single minutes filter keeps the comparison fair (default 600 ≈ 6-7
full games). Reads from the .api_cache, so re-runs cost no API quota.

    python best_by_position.py                 # top 15 per position, min 600'
    python best_by_position.py --top 20 --min-minutes 900
"""

from __future__ import annotations

import argparse
import sys

from api_football import ApiFootball, ApiFootballError
from league_report import LEAGUES, gather

# short league tags for the combined table
LEAGUE_TAG = {
    "premierleague": "ENG", "laliga": "ESP", "seriea_italy": "ITA",
    "bundesliga": "GER", "ligue1": "FRA", "eredivisie": "NED",
    "primeiraliga": "POR", "belgium": "BEL", "superlig_turkey": "TUR",
    "brazil_seriea": "BRA", "euro2024": "EURO", "saudi": "SAU",
}


def _pk(f) -> str:
    if f.pen_attempts == 0:
        return "-"
    return f"{f.pen_scored}/{f.pen_attempts}" + ("*" if f.pen_taker else "")


def _cols(pos: str):
    common = [
        ("xPts", 5, lambda f, xp, lg: f"{xp:.2f}"),
        ("Player", 22, lambda f, xp, lg: f.name[:22]),
        ("Team", 16, lambda f, xp, lg: f.team[:16]),
        ("Lg", 4, lambda f, xp, lg: lg),
        ("Min", 5, lambda f, xp, lg: f.minutes),
    ]
    if pos == "GK":
        extra = [("Sv/90", 5, lambda f, xp, lg: f"{f.per90['saves']:.2f}"),
                 ("GC", 3, lambda f, xp, lg: f.goals_conceded),
                 ("PSv", 3, lambda f, xp, lg: f.pen_saved)]
    elif pos == "DEF":
        extra = [("G", 2, lambda f, xp, lg: f.goals), ("A", 2, lambda f, xp, lg: f.assists),
                 ("Tk/90", 5, lambda f, xp, lg: f"{f.per90['tackles']:.2f}"),
                 ("PK", 5, lambda f, xp, lg: _pk(f))]
    elif pos == "MID":
        extra = [("G", 2, lambda f, xp, lg: f.goals), ("A", 2, lambda f, xp, lg: f.assists),
                 ("G/90", 5, lambda f, xp, lg: f"{f.per90['goals']:.2f}"),
                 ("A/90", 5, lambda f, xp, lg: f"{f.per90['assists']:.2f}"),
                 ("KP/90", 5, lambda f, xp, lg: f"{f.per90['key_passes']:.2f}"),
                 ("PK", 5, lambda f, xp, lg: _pk(f))]
    else:  # FWD
        extra = [("G", 2, lambda f, xp, lg: f.goals), ("A", 2, lambda f, xp, lg: f.assists),
                 ("G/90", 5, lambda f, xp, lg: f"{f.per90['goals']:.2f}"),
                 ("SoT/90", 6, lambda f, xp, lg: f"{f.per90['shots_on']:.2f}"),
                 ("PK", 5, lambda f, xp, lg: _pk(f))]
    tail = [("Rt", 4, lambda f, xp, lg: f"{f.rating:.1f}")]
    return common + extra + tail


def _table(rows, pos: str, top: int) -> str:
    cols = _cols(pos)
    subset = [r for r in rows if r[0].position == pos][:top]
    head = "  ".join(f"{n:<{w}}" if n in ("Player", "Team") else f"{n:>{w}}" for n, w, _ in cols)
    lines = [f"=== Top {top} {pos} (all leagues, by xPts/match) ===", head, "-" * len(head)]
    for i, (form, xp, lg) in enumerate(subset, 1):
        cells = []
        for n, w, fn in cols:
            v = str(fn(form, xp, lg))
            cells.append(f"{v:<{w}}" if n in ("Player", "Team") else f"{v:>{w}}")
        lines.append(f"{i:>2}  " + "  ".join(cells))
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Combined best-by-position ranking")
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument("--min-minutes", type=int, default=600)
    parser.add_argument("--out", default="best_by_position.txt")
    args = parser.parse_args(argv)

    try:  # Windows consoles default to cp1252; don't crash on accented names
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    try:
        api = ApiFootball()
    except ApiFootballError as e:
        print(f"Setup error: {e}", file=sys.stderr)
        return 1

    pool: list[tuple] = []
    for stem, (league, season, _title) in LEAGUES.items():
        try:
            scored, *_ = gather(api, league, season, args.min_minutes)
        except ApiFootballError as e:
            print(f"  [{stem}] skipped: {e}", file=sys.stderr)
            continue
        tag = LEAGUE_TAG.get(stem, stem[:4].upper())
        pool.extend((form, xp, tag) for (form, xp, _d, _inj) in scored)

    pool.sort(key=lambda r: r[1], reverse=True)
    header = (f"Best players by position across {len(LEAGUES)} leagues  |  "
              f"min {args.min_minutes}' | WC2026 ruleset | xPts/match | pool: {len(pool)} players\n")
    body = "\n\n".join(_table(pool, pos, args.top) for pos in ("GK", "DEF", "MID", "FWD"))
    report = header + "\n" + body + "\n"

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print(f"[wrote {args.out}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
