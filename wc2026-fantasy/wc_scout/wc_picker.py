"""
WC2026 Fantasy Picker — standalone-ish ranker.

Pulls World Cup 2026 data from API-Football (league=1, season=2026) following
the official "Guide to Using Data with API-SPORTS", scores every player under
the FIFA World Cup Fantasy ruleset, and prints/writes a ranked shortlist.

It shares the data-extraction (player_form.py) and ruleset (scoring.py) layers
with scout.py, so both tools stay consistent. It only needs `requests` + a key.

    pip install requests
    setx API_FOOTBALL_KEY "your_key"      # Windows; or a .env file
    python wc_picker.py

Endpoints used (plain HTTP GETs with the x-apisports-key header):
    /players?league=1&season=2026&page=N   -> squads + per-player season stats
    /standings?league=1&season=2026        -> team defensive strength (GA/game)
    /injuries?league=1&season=2026         -> exclude injured / suspended

Note from the guide: WC2026 player rows fill in as the tournament progresses,
so early on this may return little. Point --season/--league at a club league or
the qualifiers to build form, then read the same shortlist format.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys

from api_football import ApiFootball, ApiFootballError
from scoring import FixtureContext
from player_form import extract_player_form, flat_row, form_to_xpts
from set_piece_takers import apply_set_pieces

WC_LEAGUE = 1
WC_SEASON = 2026


# --------------------------------------------------------------------------
# Team defensive strength -> clean-sheet proxy + expected goals against
# --------------------------------------------------------------------------

def team_defense(api: ApiFootball, league: int, season: int) -> dict[int, dict]:
    """
    From /standings, estimate each team's clean-sheet prob and expected goals
    against from goals conceded per game. Poisson: P(0 conceded) = exp(-GA/game).
    Returns {team_id: {clean_sheet_prob, expected_goals_against}}.
    """
    try:
        standings = api.standings(league=league, season=season)
    except ApiFootballError:
        return {}

    out: dict[int, dict] = {}
    for entry in standings:
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
                    continue
                xga = against / played
                out[tid] = {
                    "clean_sheet_prob": round(math.exp(-xga), 3),
                    "expected_goals_against": round(xga, 3),
                }
    return out


def injured_player_ids(api: ApiFootball, league: int, season: int) -> set[int]:
    try:
        rows = api.injuries(league=league, season=season)
    except ApiFootballError:
        return set()
    return {
        (r.get("player", {}) or {}).get("id")
        for r in rows
        if (r.get("player", {}) or {}).get("id")
    }


# --------------------------------------------------------------------------
# Orchestration + output
# --------------------------------------------------------------------------

def build_shortlist(
    api: ApiFootball,
    league: int,
    season: int,
    min_minutes: int,
    exclude_injured: bool,
) -> list[dict]:
    defense = team_defense(api, league, season)
    injured = injured_player_ids(api, league, season) if exclude_injured else set()
    entries = api.player_stats_paginated(league=league, season=season)

    rows: list[dict] = []
    for entry in entries:
        form = extract_player_form(entry)
        if not form or form.minutes < min_minutes:
            continue
        if form.player_id in injured:
            continue
        # WC overlay: national-team set-piece duty (no-op for club team names).
        role = apply_set_pieces(form, form.team)
        d = defense.get(form.team_id, {"clean_sheet_prob": 0.30, "expected_goals_against": 1.2})
        ctx = FixtureContext(
            clean_sheet_prob=d["clean_sheet_prob"],
            expected_goals_against=d["expected_goals_against"],
            start_prob=form.start_prob,
            p_sixty=form.p_sixty,
        )
        row = flat_row(form)
        row["clean_sheet_prob"] = d["clean_sheet_prob"]
        row["expected_goals_against"] = d["expected_goals_against"]
        row["set_piece_role"] = role.label() if role else ""
        row["xpts_per_match"] = form_to_xpts(form, ctx)
        rows.append(row)

    rows.sort(key=lambda r: r["xpts_per_match"], reverse=True)
    return rows


def write_csv(rows: list[dict], path: str) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def print_table(rows: list[dict], top: int) -> None:
    if not rows:
        print("No players with stats yet for this league/season.")
        print("WC2026 player rows fill in as the tournament progresses — try a")
        print("club league or the qualifiers via --league/--season to build form.")
        return

    print(f"\nTop {min(top, len(rows))} fantasy picks (by expected points/match):\n")
    header = (f"{'#':>2}  {'Player':<20} {'Team':<14} {'Pos':<4} {'xPts':>5} "
              f"{'Start':>5} {'G/90':>5} {'A/90':>5} {'Tk/90':>5} {'CS%':>4} {'Rt':>4}")
    print(header)
    print("-" * len(header))
    for i, r in enumerate(rows[:top], 1):
        print(
            f"{i:>2}  {r['name'][:20]:<20} {r['team'][:14]:<14} {r['position']:<4} "
            f"{r['xpts_per_match']:>5.2f} {r['start_prob']*100:>4.0f}% "
            f"{r['goals_per90']:>5.2f} {r['assists_per90']:>5.2f} {r['tackles_per90']:>5.2f} "
            f"{r['clean_sheet_prob']*100:>3.0f}% {r['rating']:>4.1f}"
        )

    print("\nBest by position:")
    for pos in ("GK", "DEF", "MID", "FWD"):
        best = [r for r in rows if r["position"] == pos][:3]
        names = ", ".join(f"{r['name']} ({r['xpts_per_match']:.2f})" for r in best)
        print(f"  {pos}: {names or '—'}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="WC2026 Fantasy Picker")
    parser.add_argument("--league", type=int, default=WC_LEAGUE, help="API-Football league id (WC=1)")
    parser.add_argument("--season", type=int, default=WC_SEASON)
    parser.add_argument("--top", type=int, default=30, help="rows to print")
    parser.add_argument("--min-minutes", type=int, default=90, help="filter out tiny samples")
    parser.add_argument("--include-injured", action="store_true", help="don't drop injured/suspended")
    parser.add_argument("--out", default="wc_picks.csv")
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args(argv)

    try:
        api = ApiFootball(use_cache=not args.no_cache)
        rows = build_shortlist(
            api, args.league, args.season, args.min_minutes,
            exclude_injured=not args.include_injured,
        )
    except ApiFootballError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    write_csv(rows, args.out)
    print_table(rows, args.top)
    if rows:
        print(f"\nWrote {len(rows)} ranked players to {args.out}")
    if api.requests_remaining is not None:
        print(f"API requests remaining today: {api.requests_remaining}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
