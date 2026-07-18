"""
Country form — recent INTERNATIONAL form per player.

The model's other two form signals (club season + club recent) are both club
football. This adds the missing third: how a player has actually performed for
his NATIONAL team lately. For each WC nation we pull its recent internationals
(/fixtures?team=<id>&last=N) and the per-match player stats (/fixtures/players),
aggregate per player, and return a PlayerForm built from those matches.

Player ids are global in API-Football, so we key by player_id — no name matching.
Same synthetic-appearances trick as recent_form.py (inject per-match appearences/
lineups so extract_player_form's summation yields correct intl totals/per-90s).

Cost: ~(N + 1) API calls per nation (1 fixtures list + 1 /fixtures/players per
fixture). Cached 12h like everything else.
"""

from __future__ import annotations

from player_form import PlayerForm, extract_player_form


def _accumulate_team(api, team_id: int, last: int) -> dict[int, dict]:
    """{player_id: synthetic /players-style entry} from a nation's recent games."""
    agg: dict[int, dict] = {}
    for fx in api.fixtures(team=team_id, last=last):
        fid = (fx.get("fixture", {}) or {}).get("id")
        if not fid:
            continue
        for block in api.fixtures_players(fixture=fid):
            team = block.get("team", {}) or {}
            for pl in block.get("players", []) or []:
                stats = pl.get("statistics") or []
                if not stats:
                    continue
                st = dict(stats[0])
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


def build_country_forms(api, nation_to_id: dict[str, int], last: int = 8) -> dict[int, PlayerForm]:
    """
    {player_id: PlayerForm} of recent international form, across the given nations.
    `nation_to_id` maps canonical nation name -> API-Football national team id.
    """
    out: dict[int, PlayerForm] = {}
    for nation, tid in nation_to_id.items():
        if not tid:
            continue
        try:
            agg = _accumulate_team(api, tid, last)
        except Exception:
            continue
        for pid, entry in agg.items():
            form = extract_player_form(entry)
            if form:
                out[pid] = form
    return out
