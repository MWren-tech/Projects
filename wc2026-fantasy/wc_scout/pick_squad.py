"""
pick_squad.py — request-efficient scouting for "best overall squad" picks.

Pulls ONE league at a time:
  - standings (1 request)  -> team attack/defence context
  - players  (paginated)   -> per-match form for every player in the league

then scores everyone through your WC2026 ruleset and prints the top picks
per position, ranked by expected points per match.

Everything is cached to disk, so after the first pull you can re-run this
as many times as you like WITHOUT spending more requests.

Usage:
    python pick_squad.py --league 39 --season 2025
    python pick_squad.py --league 39 --season 2025 --top 15

Find league ids first with:
    python pick_squad.py --list-leagues
"""

from __future__ import annotations

import argparse
import sys

from api_football import ApiFootball, ApiFootballError
from scoring import FixtureContext, expected_points, value_score, _norm_pos
from scout import build_player_form


def list_leagues(api: ApiFootball, limit: int = 80) -> None:
    body = api.get("leagues")
    rows = body.get("response", [])
    print(f"{'ID':>5}  {'League':<32} {'Country'}")
    print("-" * 60)
    for l in rows[:limit]:
        lg = l.get("league", {})
        co = l.get("country", {})
        print(f"{lg.get('id'):>5}  {lg.get('name', '?'):<32} {co.get('name', '')}")
    _print_quota(api)


def team_defensive_strength(api: ApiFootball, league: int, season: int) -> dict[str, float]:
    """
    From standings (1 request): map team name -> a clean-sheet proxy.
    Fewer goals conceded per game => higher clean-sheet probability.
    """
    body = api.get("standings", {"league": league, "season": season})
    resp = body.get("response", [])
    cs_by_team: dict[str, float] = {}
    if not resp:
        return cs_by_team
    # standings[0].league.standings is a list of group tables
    for group in resp[0].get("league", {}).get("standings", []):
        for row in group:
            name = row.get("team", {}).get("name", "")
            played = row.get("all", {}).get("played", 0) or 1
            against = row.get("all", {}).get("goals", {}).get("against", 0)
            gc_per_game = against / played
            # crude monotonic map: 0 conceded/game -> ~0.5, 2+/game -> ~0.05
            cs = max(0.05, min(0.55, 0.5 - 0.22 * gc_per_game))
            cs_by_team[name] = round(cs, 3)
    return cs_by_team


def scout_league(api: ApiFootball, league: int, season: int, top: int) -> None:
    print(f"Pulling standings for league {league}, season {season} ...")
    cs_by_team = team_defensive_strength(api, league, season)
    if cs_by_team:
        print(f"  got clean-sheet proxies for {len(cs_by_team)} teams")
    else:
        print("  no standings (league/season may have no table) - using default CS prob")

    print("Pulling players (paginated) - this is the main request cost ...")
    try:
        entries = api.player_stats_paginated(league=league, season=season)
    except ApiFootballError as e:
        print(f"Player fetch failed: {e}", file=sys.stderr)
        return
    print(f"  got {len(entries)} player-stat entries")

    scored = []
    for entry in entries:
        form = build_player_form(entry)
        if not form or form.appearances < 3:  # skip tiny samples
            continue
        cs_prob = cs_by_team.get(form.team, 0.25)
        ctx = FixtureContext(clean_sheet_prob=cs_prob, start_prob=0.85)
        xp = expected_points(
            position=form.position,
            fixture=ctx,
            goals_per_match=form.goals_per_match,
            assists_per_match=form.assists_per_match,
            shots_on_target_per_match=form.sot_per_match,
            chances_created_per_match=form.chances_per_match,
            tackles_per_match=form.tackles_per_match,
        )
        scored.append((xp, form, cs_prob))

    by_pos: dict[str, list] = {"GK": [], "DEF": [], "MID": [], "FWD": []}
    for xp, form, cs in scored:
        by_pos[_norm_pos(form.position)].append((xp, form, cs))

    for pos in ("GK", "DEF", "MID", "FWD"):
        rows = sorted(by_pos[pos], key=lambda r: r[0], reverse=True)[:top]
        if not rows:
            continue
        print(f"\n=== Top {pos} (by xPts/match) ===")
        print(f"{'xPts':>5}  {'Player':<24} {'Team':<20} {'apps':>4} {'g/m':>5} {'a/m':>5}")
        for xp, f, cs in rows:
            print(
                f"{xp:>5}  {f.name[:24]:<24} {f.team[:20]:<20} "
                f"{f.appearances:>4} {f.goals_per_match:>5} {f.assists_per_match:>5}"
            )
    _print_quota(api)


def _print_quota(api: ApiFootball) -> None:
    if api.requests_remaining is not None:
        print(f"\n[API requests remaining today: {api.requests_remaining}]")


def main(argv=None):
    p = argparse.ArgumentParser(description="Best-squad scouting, one league at a time")
    p.add_argument("--league", type=int)
    p.add_argument("--season", type=int, default=2025)
    p.add_argument("--top", type=int, default=12)
    p.add_argument("--list-leagues", action="store_true")
    args = p.parse_args(argv)

    try:
        api = ApiFootball()
    except ApiFootballError as e:
        print(f"Setup error: {e}", file=sys.stderr)
        return 1

    if args.list_leagues:
        list_leagues(api)
        return 0
    if not args.league:
        print("Give --league ID (or --list-leagues to find one).", file=sys.stderr)
        return 1

    scout_league(api, args.league, args.season, args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
