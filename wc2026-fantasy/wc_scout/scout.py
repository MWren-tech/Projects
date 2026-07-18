"""
Full scout pipeline: pull fixtures, match signals (predictions/odds), player
form and injuries, then turn them into ranked fantasy recommendations under the
WC2026 ruleset.

Run directly:
    setx API_FOOTBALL_KEY "..."        # or put it in .env
    python scout.py --league 1 --season 2026 --next 10

Because API-Football won't have WC2026 player data until the tournament is live,
you'll mostly point this at qualifiers / friendlies / club seasons to build form,
then map those players onto your squad list. The CSV/JSON output is designed to
be eyeballed or fed into a notebook.

Signal priority for each fixture's clean-sheet / expected-goals-against:
    1. /predictions  -> Poisson clean-sheet from the opponent's season scoring avg
    2. /odds         -> Over/Under 2.5 proxy (fallback)
    3. defaults
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys

from api_football import ApiFootball, ApiFootballError
from scoring import FixtureContext
from player_form import extract_player_form, flat_row, form_to_xpts
from set_piece_takers import apply_set_pieces


# --- Odds parsing (fallback signal) --------------------------------------

def implied_prob(decimal_odds: float) -> float:
    return 1.0 / decimal_odds if decimal_odds and decimal_odds > 0 else 0.0


def extract_match_signals(odds_response: list, fixture_id: int) -> dict:
    """
    Rough clean-sheet / goals signals from the odds payload.
    Structure: response[].bookmakers[].bets[].values[]. Bet id 1 = Match Winner;
    'Goals Over/Under' gives totals. Averaged across bookmakers, de-vigged naively.
    """
    home_win, draw, away_win = [], [], []
    over25, under25 = [], []

    for entry in odds_response:
        if entry.get("fixture", {}).get("id") != fixture_id:
            continue
        for bm in entry.get("bookmakers", []):
            for bet in bm.get("bets", []):
                name = bet.get("name", "")
                vals = {v.get("value"): v.get("odd") for v in bet.get("values", [])}
                if bet.get("id") == 1 or name == "Match Winner":
                    for key, bucket in (("Home", home_win), ("Draw", draw), ("Away", away_win)):
                        if key in vals:
                            bucket.append(implied_prob(float(vals[key])))
                if "Over/Under" in name and "Goals" in name:
                    if "Over 2.5" in vals:
                        over25.append(implied_prob(float(vals["Over 2.5"])))
                    if "Under 2.5" in vals:
                        under25.append(implied_prob(float(vals["Under 2.5"])))

    def avg(xs):
        return sum(xs) / len(xs) if xs else 0.0

    p_under = avg(under25)
    cs_proxy = round(min(0.6, p_under * 0.6), 3)
    return {
        "p_home": round(avg(home_win), 3),
        "p_draw": round(avg(draw), 3),
        "p_away": round(avg(away_win), 3),
        "p_over_2_5": round(avg(over25), 3),
        "clean_sheet_proxy": cs_proxy,
    }


# --- Predictions parsing (preferred signal) ------------------------------

def _avg_goals_for(team_block: dict) -> float | None:
    """Pull a team's season average goals-for from a /predictions teams block."""
    try:
        val = team_block["league"]["goals"]["for"]["average"]["total"]
        return float(val) if val not in (None, "") else None
    except (KeyError, TypeError, ValueError):
        return None


def predictions_context(predictions: list) -> dict[int, dict]:
    """
    Map team_id -> {clean_sheet_prob, expected_goals_against} for one fixture.
    Each side's xGA = the OTHER side's average goals-for; clean-sheet prob is the
    Poisson P(0 goals conceded) = exp(-xGA).
    """
    if not predictions:
        return {}
    p = predictions[0]
    teams = p.get("teams", {}) or {}
    home, away = teams.get("home", {}) or {}, teams.get("away", {}) or {}
    hid = (home.get("id") or (home.get("team") or {}).get("id"))
    aid = (away.get("id") or (away.get("team") or {}).get("id"))
    h_gf, a_gf = _avg_goals_for(home), _avg_goals_for(away)

    out: dict[int, dict] = {}
    if hid and a_gf is not None:  # home concedes ~ away's scoring rate
        out[hid] = {"clean_sheet_prob": round(math.exp(-a_gf), 3), "expected_goals_against": round(a_gf, 3)}
    if aid and h_gf is not None:
        out[aid] = {"clean_sheet_prob": round(math.exp(-h_gf), 3), "expected_goals_against": round(h_gf, 3)}
    return out


# --- Pipeline -------------------------------------------------------------

def run_scout(
    api: ApiFootball,
    *,
    league: int,
    season: int,
    next_n: int,
    default_cs_prob: float = 0.3,
    default_xga: float = 1.2,
) -> dict:
    out: dict = {"fixtures": [], "players": [], "warnings": []}

    # 1. Fixtures
    try:
        fixtures = api.fixtures(league=league, season=season, next=next_n)
    except ApiFootballError as e:
        out["warnings"].append(f"fixtures fetch failed: {e}")
        fixtures = []

    # 2. Per-team match context (clean sheet + xGA), predictions first, odds fallback
    team_ctx: dict[int, dict] = {}
    for fx in fixtures:
        fid = fx.get("fixture", {}).get("id")
        teams = fx.get("teams", {})
        out["fixtures"].append({
            "id": fid,
            "date": fx.get("fixture", {}).get("date"),
            "home": teams.get("home", {}).get("name"),
            "away": teams.get("away", {}).get("name"),
        })

        ctx_for_fixture: dict[int, dict] = {}
        try:
            ctx_for_fixture = predictions_context(api.predictions(fixture=fid))
        except ApiFootballError as e:
            out["warnings"].append(f"predictions for fixture {fid} unavailable: {e}")

        if not ctx_for_fixture:  # fall back to odds proxy
            try:
                sig = extract_match_signals(api.odds(fixture=fid), fid)
                for side in ("home", "away"):
                    tid = teams.get(side, {}).get("id")
                    if tid:
                        ctx_for_fixture[tid] = {
                            "clean_sheet_prob": sig["clean_sheet_proxy"],
                            "expected_goals_against": default_xga,
                        }
            except ApiFootballError as e:
                out["warnings"].append(f"odds for fixture {fid} unavailable: {e}")

        # keep the best (soonest) fixture's context per team
        for tid, c in ctx_for_fixture.items():
            team_ctx.setdefault(tid, c)

    # 3. Injuries / suspensions — flag affected players
    injured_ids: set[int] = set()
    try:
        for inj in api.injuries(league=league, season=season):
            pid = (inj.get("player", {}) or {}).get("id")
            if pid:
                injured_ids.add(pid)
    except ApiFootballError as e:
        out["warnings"].append(f"injuries fetch failed: {e}")

    # 4. Player form per team, scored under the ruleset
    team_ids = {
        fx.get("teams", {}).get(side, {}).get("id")
        for fx in fixtures for side in ("home", "away")
        if fx.get("teams", {}).get(side, {}).get("id")
    }

    for tid in team_ids:
        try:
            entries = api.player_stats_paginated(team=tid, season=season, league=league)
        except ApiFootballError as e:
            out["warnings"].append(f"players for team {tid} failed: {e}")
            continue

        c = team_ctx.get(tid, {"clean_sheet_prob": default_cs_prob, "expected_goals_against": default_xga})

        for entry in entries:
            form = extract_player_form(entry)
            if not form:
                continue
            # WC overlay: for national teams the team name IS the nation, so this
            # sets the real penalty/FK/corner threat (no-op for club team names).
            role = apply_set_pieces(form, form.team)
            ctx = FixtureContext(
                clean_sheet_prob=c["clean_sheet_prob"],
                expected_goals_against=c["expected_goals_against"],
                start_prob=form.start_prob,
                p_sixty=form.p_sixty,
            )
            row = flat_row(form)
            row["clean_sheet_prob"] = round(c["clean_sheet_prob"], 3)
            row["expected_goals_against"] = round(c["expected_goals_against"], 3)
            row["set_piece_role"] = role.label() if role else ""
            row["injured"] = form.player_id in injured_ids
            row["xpts_per_match"] = form_to_xpts(form, ctx)
            out["players"].append(row)

    out["players"].sort(key=lambda r: r["xpts_per_match"], reverse=True)
    return out


def write_outputs(data: dict, prefix: str) -> None:
    with open(f"{prefix}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    if data["players"]:
        with open(f"{prefix}_players.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(data["players"][0].keys()))
            w.writeheader()
            w.writerows(data["players"])
    print(f"Wrote {prefix}.json and {prefix}_players.csv")
    print(f"Fixtures: {len(data['fixtures'])}  Players ranked: {len(data['players'])}")
    if data["warnings"]:
        print(f"Warnings: {len(data['warnings'])} (see JSON)")
    if _API is not None and _API.requests_remaining is not None:
        print(f"API requests remaining today: {_API.requests_remaining}")


_API: ApiFootball | None = None


def main(argv=None):
    parser = argparse.ArgumentParser(description="WC2026 Fantasy scout pipeline")
    parser.add_argument("--league", type=int, required=True, help="API-Football league id")
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--next", type=int, default=10, dest="next_n")
    parser.add_argument("--out", default="scout_output")
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args(argv)

    global _API
    try:
        _API = ApiFootball(use_cache=not args.no_cache)
    except ApiFootballError as e:
        print(f"Setup error: {e}", file=sys.stderr)
        return 1

    data = run_scout(_API, league=args.league, season=args.season, next_n=args.next_n)
    write_outputs(data, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
