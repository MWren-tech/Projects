"""
Actual World Cup 2026 tournament form.

Once the tournament is under way, a player's real WC output is the strongest
signal we have. This builds a per-player PlayerForm — keyed by global player_id —
of each player's CUMULATIVE WC2026 output so far, so it can be blended into the
projection like any other form window.

Why we aggregate fixtures instead of reading the season total
-------------------------------------------------------------
API-Football exposes a season-aggregate at /players?league=1&season=2026, but
that aggregate LAGS the actual matches — mid-group it can still report only
round-1 totals even though round-2 games have finished (observed: a player who
started both group games shows apps=1 there). The authoritative, immediately
updated source is the per-fixture feed /fixtures/players, which has every
completed match. So we enumerate completed WC fixtures and sum each player's
per-match lines into a cumulative aggregate, then reuse the normal extractor.

Early in the tournament this is a tiny sample (1-2 games), so the blend
sample-weights it; its influence grows as more WC minutes accumulate.
"""

from __future__ import annotations

from player_form import PlayerForm, extract_player_form

FINISHED = {"FT", "AET", "PEN"}


def _agg_init() -> dict:
    """A blank API-Football-shaped statistics entry we can accumulate into."""
    return {
        "games": {"appearences": 0, "lineups": 0, "minutes": 0, "position": None,
                  "rating": None},
        "_ratings": [],
        "team": {"id": None, "name": None},
        "goals": {"total": 0, "conceded": 0, "assists": 0, "saves": 0},
        "shots": {"total": 0, "on": 0},
        "passes": {"key": 0},
        "tackles": {"total": 0},
        "penalty": {"won": 0, "commited": 0, "scored": 0, "missed": 0, "saved": 0},
        "cards": {"yellow": 0, "yellowred": 0, "red": 0},
        "fouls": {"committed": 0},
    }


def _num(d, key) -> int:
    if not d:
        return 0
    return d.get(key) or 0


def _accumulate(agg: dict, stat: dict, team: dict) -> None:
    """Add one fixture's per-player statistics line into the running aggregate."""
    g = stat.get("games") or {}
    mins = _num(g, "minutes")
    # /fixtures/players has no appearences/lineups field; derive it. A player with a
    # statistics line for the match appeared; `substitute=False` means he started.
    agg["games"]["appearences"] += 1
    if g.get("substitute") is False:
        agg["games"]["lineups"] += 1
    agg["games"]["minutes"] += mins
    agg["games"]["position"] = g.get("position") or agg["games"]["position"]
    if g.get("rating"):
        try:
            agg["_ratings"].append(float(g["rating"]))
        except (TypeError, ValueError):
            pass
    if team:
        agg["team"]["id"] = team.get("id") or agg["team"]["id"]
        agg["team"]["name"] = team.get("name") or agg["team"]["name"]

    agg["goals"]["total"] += _num(stat.get("goals"), "total")
    agg["goals"]["assists"] += _num(stat.get("goals"), "assists")
    agg["goals"]["saves"] += _num(stat.get("goals"), "saves")
    agg["goals"]["conceded"] += _num(stat.get("goals"), "conceded")
    agg["shots"]["total"] += _num(stat.get("shots"), "total")
    agg["shots"]["on"] += _num(stat.get("shots"), "on")
    agg["passes"]["key"] += _num(stat.get("passes"), "key")
    agg["tackles"]["total"] += _num(stat.get("tackles"), "total")
    agg["penalty"]["won"] += _num(stat.get("penalty"), "won")
    agg["penalty"]["commited"] += _num(stat.get("penalty"), "commited")
    agg["penalty"]["scored"] += _num(stat.get("penalty"), "scored")
    agg["penalty"]["missed"] += _num(stat.get("penalty"), "missed")
    agg["penalty"]["saved"] += _num(stat.get("penalty"), "saved")
    agg["cards"]["yellow"] += _num(stat.get("cards"), "yellow")
    agg["cards"]["yellowred"] += _num(stat.get("cards"), "yellowred")
    agg["cards"]["red"] += _num(stat.get("cards"), "red")
    agg["fouls"]["committed"] += _num(stat.get("fouls"), "committed")


def build_wc_forms(api, league: int = 1, season: int = 2026) -> dict[int, PlayerForm]:
    """
    {player_id: PlayerForm} of CUMULATIVE actual WC2026 output, aggregated across all
    completed fixtures (the season-aggregate endpoint lags and misses recent rounds).
    Only players with >0 minutes are returned.

    Falls back to the season-aggregate endpoint if no completed fixtures are found
    (e.g. before the tournament kicks off, or if the fixtures feed is unavailable).
    """
    from national_strength import wc_team_ids

    # Force-refresh the fixtures list: it gains newly completed matches every
    # matchday, and the 12h cache would otherwise hide the latest round (the bug
    # where projections froze at round-1 totals). Per-fixture stats below stay
    # cached — a finished match's stats never change.
    fixtures = api.fixtures(league=league, season=season, force_refresh=True)
    completed = [
        f for f in fixtures
        if (f.get("fixture", {}).get("status", {}) or {}).get("short") in FINISHED
    ]

    if not completed:
        return _build_from_season_aggregate(api, league, season)

    # team id -> canonical nation, so each player's PlayerForm carries the nationality
    # downstream code (e.g. export_snapshot._find_wc_form) matches on.
    _, id_to_nation = wc_team_ids(api, league, season)

    aggregates: dict[int, dict] = {}
    names: dict[int, str] = {}
    for f in completed:
        fixture_id = f.get("fixture", {}).get("id")
        if fixture_id is None:
            continue
        for team_block in api.fixtures_players(fixture_id):
            team = team_block.get("team", {}) or {}
            for pl in team_block.get("players", []) or []:
                p = pl.get("player", {}) or {}
                pid = p.get("id")
                if pid is None:
                    continue
                stats = pl.get("statistics") or []
                if not stats:
                    continue
                stat = stats[0] or {}
                # Skip unused players (no minutes AND no recorded line activity).
                if not (stat.get("games") or {}).get("minutes"):
                    continue
                agg = aggregates.get(pid)
                if agg is None:
                    agg = aggregates[pid] = _agg_init()
                names[pid] = p.get("name") or names.get(pid, "?")
                _accumulate(agg, stat, team)

    out: dict[int, PlayerForm] = {}
    for pid, agg in aggregates.items():
        ratings = agg.pop("_ratings", [])
        if ratings:
            agg["games"]["rating"] = round(sum(ratings) / len(ratings), 2)
        team_id = agg["team"].get("id")
        nationality = id_to_nation.get(team_id, "")
        entry = {
            "player": {"id": pid, "name": names.get(pid, "?"),
                       "nationality": nationality},
            "statistics": [agg],
        }
        form = extract_player_form(entry)
        if form and form.minutes > 0:
            out[pid] = form
    return out


def _build_from_season_aggregate(api, league: int, season: int) -> dict[int, PlayerForm]:
    """Pre-tournament / fallback: read the season-aggregate /players endpoint."""
    out: dict[int, PlayerForm] = {}
    for entry in api.player_stats_paginated(league=league, season=season):
        form = extract_player_form(entry)
        if form and form.minutes > 0 and form.player_id is not None:
            out[form.player_id] = form
    return out
