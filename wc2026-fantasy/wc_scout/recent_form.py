"""
Recent-form (last-N) layer.

Season aggregates dilute current form. This module pulls the league's most recent
finished fixtures via /fixtures?last=N, aggregates each player's per-match stats
from /fixtures/players, and scores that recent window with the same ruleset — so
you can compare a player's recent xPts against their season xPts.

Cost: roughly (N + 1) API requests per league (1 for the fixtures list, 1 per
fixture for its player stats). Opt-in via league_report's --recent flag.

Implementation note: /fixtures/players' per-match `games` block has `minutes`,
`rating`, `substitute` — but not the season's `appearences`/`lineups`. We inject
those per match (appeared = minutes>0; started = not substitute) so the existing
extract_player_form() summation produces correct recent totals, per-90 rates and
start_prob with zero duplicated logic.
"""

from __future__ import annotations

from scoring import FixtureContext
from player_form import PlayerForm, extract_player_form, form_to_xpts


def _accumulate(api, league: int, season: int, n_fixtures: int) -> dict[int, dict]:
    """Build {player_id: synthetic /players-style entry} from recent fixtures."""
    fixtures = api.fixtures(league=league, season=season, last=n_fixtures)
    agg: dict[int, dict] = {}
    for fx in fixtures:
        fid = (fx.get("fixture", {}) or {}).get("id")
        if not fid:
            continue
        for block in api.fixtures_players(fixture=fid):
            team = block.get("team", {}) or {}
            for pl in block.get("players", []) or []:
                stats = pl.get("statistics") or []
                if not stats:
                    continue
                st = dict(stats[0])  # shallow copy so we can inject fields
                g = dict(st.get("games", {}) or {})
                mins = g.get("minutes") or 0
                g["appearences"] = 1 if mins > 0 else 0
                g["lineups"] = 0 if g.get("substitute") else (1 if mins > 0 else 0)
                st["games"] = g
                st["team"] = team
                pid = (pl.get("player", {}) or {}).get("id")
                if pid is None:
                    continue
                entry = agg.setdefault(pid, {"player": pl["player"], "statistics": []})
                entry["statistics"].append(st)
    return agg


def recent_forms(api, league: int, season: int, n_fixtures: int,
                 defense: dict[int, dict]) -> dict[int, tuple[PlayerForm, float]]:
    """
    Return {player_id: (recent PlayerForm, recent xPts/match)} over the last
    n_fixtures of the league. `defense` is the season clean-sheet/xGA lookup
    (reused so recent GK/DEF scoring still reflects team strength).
    """
    out: dict[int, tuple[PlayerForm, float]] = {}
    for pid, entry in _accumulate(api, league, season, n_fixtures).items():
        form = extract_player_form(entry)
        if not form:
            continue
        d = defense.get(form.team_id, {"clean_sheet_prob": 0.30, "expected_goals_against": 1.2})
        ctx = FixtureContext(
            clean_sheet_prob=d["clean_sheet_prob"],
            expected_goals_against=d["expected_goals_against"],
            start_prob=form.start_prob,
            p_sixty=form.p_sixty,
        )
        out[pid] = (form, form_to_xpts(form, ctx))
    return out
