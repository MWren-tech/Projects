"""
Runs the analytics pipeline and writes snapshot.json for the web app.

    python export_snapshot.py                # fast (reuses cached pool)
    python export_snapshot.py --incremental  # re-pulls WC form + fixtures (~1-2 min)
    python export_snapshot.py --refresh      # full rebuild, all windows (slow)
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from api_football import ApiFootball
from optimise import build_priced_survivors, _pool, optimise_ilp, find_held
from wc_shortlist import incremental_refresh
from national_strength import build_national_context
from wc_form import build_wc_forms
from scoring import (
    SCOUTING_BONUS,
    SCOUTING_OWNERSHIP_THRESHOLD,
    SCOUTING_PTS_THRESHOLD,
)
import booster_planner

OUT = Path(__file__).resolve().parent.parent / "wc-companion" / "data" / "snapshot.json"

# Official WC2026 fantasy rules the app surfaces (kept in sync with the rules page).
RULES = {
    "budget": 100.0,
    "knockoutBudget": 105.0,
    "squad": {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3},
    "formations": ["4-4-2", "4-3-3", "4-5-1", "3-4-3", "3-5-2", "5-4-1", "5-3-2"],
    "transfers": {
        "MD2": 2, "MD3": 2, "R32": "unlimited",
        "R16": 4, "QF": 4, "SF": 5, "Final": 6,
        "hitCost": 3, "carryover": 1,
    },
    "maxPerNation": {"Group": 3, "R32": 3, "R16": 4, "QF": 5, "SF": 6, "Final": 8},
    "boosters": ["Wildcard", "12th Man", "Maximum Captain", "Qualification", "Mystery"],
    "scoring": {
        "appearance": "1 (+1 for 60')", "assist": 3, "yellow": -1, "red": -2,
        "goalGK": 9, "goalDEF": 7, "goalMID": 6, "goalFWD": 5,
        "cleanSheetGKDEF": 5, "cleanSheetMID": 1, "penSave": 3, "saves": "1 per 3",
        "tacklesMID": "1 per 3", "chancesMID": "1 per 2", "sotFWD": "1 per 2",
        "fkBonus": 1, "scoutingBonus": 2,
    },
}


import unicodedata


def slug(name: str, nation: str) -> str:
    # ASCII-only so route URLs never contain accented chars (which broke /players/[id]).
    base = unicodedata.normalize("NFKD", f"{name}-{nation}".lower()).encode("ascii", "ignore").decode()
    out = "".join(c if c.isalnum() else "-" for c in base)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


def percentiles(values: list[float]) -> dict[float, float]:
    """0-100 percentile rank per value, used for the AI rating badge."""
    s = sorted(values)
    n = len(s)
    out = {}
    for v in set(values):
        # share of values strictly below v
        lo = sum(1 for x in s if x < v)
        out[v] = round(100 * lo / max(1, n - 1), 0)
    return out


GOAL_PTS = {"GK": 9, "DEF": 7, "MID": 6, "FWD": 5}
SCORING_POSITIONS = set(GOAL_PTS)  # the four fantasy positions; filters out coaches/invalid rows


def wc_stats(form, pos: str, official_total: int | None = None,
             ownership: float | None = None,
             round_points: list[dict] | None = None) -> dict | None:
    """
    WC2026 tournament tally with per-stat fantasy point breakdown.

    Total comes from FIFA's official feed when available so it matches the game exactly.
    The per-stat lines come from API-Football (can diverge — e.g. on assists); any gap is
    shown as a reconciling "official scoring" line. The scouting bonus (+2 per qualifying
    haul for sub-5%-owned players) is pulled out of that gap separately when detectable.
    Returns None if the player hasn't featured yet.
    """
    if not form or (getattr(form, "minutes", 0) or 0) <= 0:
        return None
    g = form.goals or 0
    a = form.assists or 0
    apps = form.appearances or 0
    starts = form.lineups or 0
    sub_apps = max(0, apps - starts)
    saves = form.saves or 0
    psaved = form.pen_saved or 0
    tackles = form.tackles or 0
    chances = form.key_passes or 0
    sot = form.shots_on or 0
    yel = form.yellows or 0
    red = form.reds or 0
    pwon = form.pen_won or 0
    pcon = form.pen_conceded or 0

    lines: list[dict] = []
    def add(label, count, pts):
        if count:
            lines.append({"label": label, "count": int(count), "pts": int(pts)})

    add("Appearances (60'+ / sub)", apps, starts * 2 + sub_apps)  # +1 play, +1 more for 60'
    add("Goals", g, g * GOAL_PTS[pos])
    add("Assists", a, a * 3)
    if pos == "GK":
        add("Saves", saves, saves // 3)
        add("Penalty saves", psaved, psaved * 3)
    if pos == "MID":
        add("Tackles", tackles, tackles // 3)
        add("Chances created", chances, chances // 2)
    if pos == "FWD":
        add("Shots on target", sot, sot // 2)
    add("Penalties won", pwon, pwon * 2)
    add("Penalties conceded", pcon, -pcon)
    add("Yellow cards", yel, -yel)
    add("Red cards", red, -red * 2)

    computed = sum(l["pts"] for l in lines)
    # use FIFA's official total so the breakdown always ties out to the game
    if official_total is not None:
        diff = official_total - computed
        if diff > 0 and ownership is not None and ownership < SCOUTING_OWNERSHIP_THRESHOLD:
            # pull the scouting bonus out of the gap separately so it shows as its own line
            hauls = sum(1 for rp in (round_points or [])
                        if (rp.get("pts") or 0) > SCOUTING_PTS_THRESHOLD)
            scouting_pts = min(diff, hauls * SCOUTING_BONUS)
            if scouting_pts > 0:
                lines.append({"label": "Scouting bonus (<5% owned)",
                              "count": hauls, "pts": scouting_pts})
                diff -= scouting_pts
        if diff != 0:
            lines.append({"label": "Other (official scoring)", "count": None, "pts": diff})
        total = official_total
    else:
        total = computed

    return {
        "minutes": form.minutes or 0,
        "appearances": apps,
        "starts": starts,
        "goals": g,
        "assists": a,
        "saves": saves,
        "penSaved": psaved,
        "tackles": tackles,
        "chances": chances,
        "shotsOn": sot,
        "yellows": yel,
        "reds": red,
        "penWon": pwon,
        "penConceded": pcon,
        "goalsConceded": form.goals_conceded or 0,
        "rating": round(form.rating, 2) if getattr(form, "rating", None) else None,
        "breakdown": lines,
        "totalPoints": total,
        "official": official_total is not None,
    }


def fallback_wc_stats(official_total: int | None) -> dict | None:
    """Bare wcStats for register players we have no API-Football breakdown for.
    Shows the FIFA official total only. None if the player hasn't scored."""
    if not official_total:
        return None
    return {
        "minutes": 0, "appearances": 0, "starts": 0, "goals": 0, "assists": 0,
        "saves": 0, "penSaved": 0, "tackles": 0, "chances": 0, "shotsOn": 0,
        "yellows": 0, "reds": 0, "penWon": 0, "penConceded": 0, "goalsConceded": 0,
        "rating": None, "breakdown": [], "totalPoints": int(official_total), "official": True,
    }


def expected_scouting_bonus(xp: float, ownership: float | None) -> float:
    """E[scouting bonus] = 2 * P(match pts > 4) for sub-5%-owned players, else 0."""
    if ownership is None or ownership >= SCOUTING_OWNERSHIP_THRESHOLD:
        return 0.0
    p_haul = max(0.0, min(0.7, (xp - 3.0) / 7.0))   # ~0 at 3xp, ~0.43 at 6xp, capped 0.7
    return round(SCOUTING_BONUS * p_haul, 2)


def _round_label(r: dict) -> str:
    stage, rid = r.get("stage"), r.get("id")
    if stage == "GROUP":
        return f"MD{rid}"
    return {"R32": "R32", "R16": "R16", "QF": "QF", "SF": "SF", "F": "Final"}.get(stage, str(stage))


def current_round_label() -> str:
    """Active round from FIFA's rounds.json — auto-advances each matchday."""
    try:
        from fifa_fantasy import _get_json, _as_list
        rounds = _as_list(_get_json("rounds.json"))
        active = (next((r for r in rounds if r.get("status") == "playing"), None)
                  or next((r for r in rounds if r.get("status") == "scheduled"), None)
                  or (rounds[-1] if rounds else None))
        return _round_label(active) if active else "MD2"
    except Exception:
        return "MD2"


def fifa_feed_map() -> dict[int, dict]:
    """FIFA players.json -> {id: {points, ownership}}. Refreshed daily."""
    try:
        from fifa_fantasy import _get_json, _as_list
        out: dict[int, dict] = {}
        for p in _as_list(_get_json("players.json")):
            if p.get("id") is None:
                continue
            tp = (p.get("stats") or {}).get("totalPoints")
            own = p.get("percentSelected")
            out[p["id"]] = {
                "points": int(tp) if tp is not None else None,
                "ownership": round(float(own), 1) if own is not None else None,
            }
        return out
    except Exception as e:
        print(f"  (FIFA feed unavailable: {e}; falling back to cached values)")
        return {}


def _round_labels() -> dict[str, str]:
    """FIFA round id (stringified) -> human label ("MD1", "R32", "Final" etc.)"""
    try:
        from fifa_fantasy import _get_json, _as_list
        return {str(r["id"]): _round_label(r) for r in _as_list(_get_json("rounds.json"))
                if r.get("id") is not None}
    except Exception:
        return {}


def fifa_round_points_map() -> dict[int, list[dict]]:
    """FIFA player id -> [{round, pts}] ordered by round. Sums to wcStats.totalPoints."""
    try:
        from fifa_fantasy import _get_json, _as_list
        labels = _round_labels()
        out: dict[int, list[dict]] = {}
        for p in _as_list(_get_json("players.json")):
            fid = p.get("id")
            rp = (p.get("stats") or {}).get("roundPoints")
            if fid is None or not isinstance(rp, dict):
                continue
            def _key(item):
                try:
                    return int(item[0])
                except (TypeError, ValueError):
                    return 0
            rounds = []
            for rid, pts in sorted(rp.items(), key=_key):
                rounds.append({"round": labels.get(str(rid), str(rid)), "pts": int(pts or 0)})
            out[fid] = rounds
        return out
    except Exception as e:
        print(f"  (FIFA round points unavailable: {e}; emitting empty roundPoints)")
        return {}


def fifa_register() -> list[dict]:
    """Full FIFA squad register (~1,250 players). Fallback for depth players the engine pool
    doesn't cover — gives them price/ownership/official points and avgPoints as xp."""
    try:
        from fifa_fantasy import _get_json, _as_list, _squad_nations, _player_name
        from scoring import norm_pos
        nations = _squad_nations()
        out: list[dict] = []
        for p in _as_list(_get_json("players.json")):
            fid = p.get("id")
            nation = nations.get(p.get("squadId"))
            pos = norm_pos(p.get("position") or "")
            if fid is None or not nation or pos not in SCORING_POSITIONS:
                continue
            stats = p.get("stats") or {}
            tp = stats.get("totalPoints")
            avg = stats.get("avgPoints")
            own = p.get("percentSelected")
            out.append({
                "fifa_id": fid,
                "name": _player_name(p),
                "nation": nation,
                "pos": pos,
                "price": float(p["price"]) if p.get("price") is not None else None,
                "ownership": round(float(own), 1) if own is not None else None,
                "points": int(tp) if tp is not None else None,
                "avgPoints": round(float(avg), 2) if avg is not None else None,
            })
        return out
    except Exception as e:
        print(f"  (FIFA register unavailable: {e}; shipping engine pool only)")
        return []


def _wc_by_name_nation(wc: dict) -> dict[tuple[str, str], object]:
    """(normalised_name, canonical_nation) -> PlayerForm, for register players with no pid.
    Collisions resolved by minutes so a cameo doesn't shadow a regular starter."""
    from set_piece_takers import _norm, canonical_nation
    out: dict[tuple[str, str], object] = {}
    for form in wc.values():
        nat = canonical_nation(getattr(form, "nationality", "") or "") or (
            getattr(form, "nationality", "") or "")
        key = (_norm(getattr(form, "name", "") or ""), nat)
        if not key[0] or not key[1]:
            continue
        cur = out.get(key)
        if cur is None or (getattr(form, "minutes", 0) or 0) > (getattr(cur, "minutes", 0) or 0):
            out[key] = form
    return out


def _find_wc_form(wc_by_nn: dict, name: str, nation: str, pos: str, wc: dict):
    """Exact (name, nation) lookup first; falls back to fuzzy match within the nation.
    Position guard avoids attaching a namesake's stats."""
    from set_piece_takers import _norm, name_matches, canonical_nation
    key = (_norm(name or ""), nation)
    hit = wc_by_nn.get(key)
    if hit is not None:
        return hit
    best = None
    for form in wc.values():
        fnat = canonical_nation(getattr(form, "nationality", "") or "") or (
            getattr(form, "nationality", "") or "")
        if fnat != nation:
            continue
        if pos and getattr(form, "position", "") and form.position != pos:
            continue
        if name_matches(name, getattr(form, "name", "") or ""):
            if best is None or (getattr(form, "minutes", 0) or 0) > (getattr(best, "minutes", 0) or 0):
                best = form
    return best


def build_players(pool, wc: dict, fifa: dict, register: list[dict],
                  round_pts: dict[int, list[dict]] | None = None) -> list[dict]:
    round_pts = round_pts or {}
    wc_by_nn = _wc_by_name_nation(wc)
    by_pos: dict[str, list[float]] = {}
    for p in pool:
        by_pos.setdefault(p["pos"], []).append(p["xp"])
    pct = {pos: percentiles(vals) for pos, vals in by_pos.items()}

    players = []
    matched_fids: set = set()
    for p in pool:
        if p.get("fifa_id") is not None:
            matched_fids.add(p["fifa_id"])
        fd = fifa.get(p.get("fifa_id")) or {}
        # Fresh ownership from the FIFA feed (refreshed daily); fall back to the cached pool.
        own = fd["ownership"] if fd.get("ownership") is not None else p.get("own")
        # Differential score: reward high projection at low ownership (0-100).
        diff_score = round(min(100, (p["xp"] / 13.0) * 100 * (1.6 if (own or 100) < 5 else
                                    1.25 if (own or 100) < 15 else 1.0)), 0)
        players.append({
            "id": slug(p["name"], p["nation"]),
            "name": p["name"],
            "nation": p["nation"],
            "club": p.get("club"),
            "pos": p["pos"],
            "price": p["price"],
            "xp": round(p["xp"], 2),
            "ownership": own,
            "value": round(p.get("value", 0), 2),
            "goals": p.get("goals"),
            "assists": p.get("assists"),
            "g90": round(p.get("g90", 0), 2),
            "a90": round(p.get("a90", 0), 2),
            "cleanSheet": round(p.get("cs", 0), 2),
            "fixtureEase": round(p.get("diff", 1.0), 2),
            "setPieces": p.get("sp") or "",
            "rating": p.get("rating"),
            "startProb": round(p.get("start", 0), 2),
            "aiRating": pct[p["pos"]].get(p["xp"], 50),
            "differential": diff_score,
            "scoutingBonus": round(p.get("scouting_xp", 0), 2),
            "wcStats": wc_stats(wc.get(p.get("pid")), p["pos"], fd.get("points"),
                                ownership=own,
                                round_points=round_pts.get(p.get("fifa_id"), [])),
            "roundPoints": round_pts.get(p.get("fifa_id"), []),
            "projected": True,   # full engine projection (matched by fifa_id)
        })

    # depth players not in the engine pool: fill from the FIFA register
    seen_ids = {p["id"] for p in players}
    for r in register:
        if r["fifa_id"] in matched_fids:
            continue
        rid = slug(r["name"], r["nation"])
        if rid in seen_ids:   # never emit a duplicate slug (the app keys players by id)
            continue
        seen_ids.add(rid)
        own = r.get("ownership")
        xp = r.get("avgPoints") or 0.0
        # look up by name+nation since register players have no API-Football pid
        wc_form = _find_wc_form(wc_by_nn, r["name"], r["nation"], r["pos"], wc)
        wstats = (wc_stats(wc_form, r["pos"], r.get("points"), ownership=own,
                           round_points=round_pts.get(r["fifa_id"], []))
                  if wc_form is not None else fallback_wc_stats(r.get("points")))
        diff_score = round(min(100, (xp / 13.0) * 100 * (1.6 if (own or 100) < 5 else
                                    1.25 if (own or 100) < 15 else 1.0)), 0)
        players.append({
            "id": rid,
            "name": r["name"],
            "nation": r["nation"],
            "club": None,
            "pos": r["pos"],
            "price": r.get("price"),
            "xp": round(xp, 2),
            "ownership": own,
            "value": round(xp / r["price"], 2) if r.get("price") else None,
            "goals": None,
            "assists": None,
            "g90": None,
            "a90": None,
            "cleanSheet": None,
            "fixtureEase": None,
            "setPieces": "",
            "rating": None,
            "startProb": None,
            "aiRating": None,
            "differential": diff_score,
            "scoutingBonus": 0,
            "wcStats": wstats,
            "roundPoints": round_pts.get(r["fifa_id"], []),
            "projected": False,  # FIFA fallback (avgPoints as xp); no engine projection
        })

    players.sort(key=lambda x: -x["xp"])
    return players


def build_fixtures(api) -> dict:
    nat = build_national_context(api)
    out = {}
    for nation, d in nat.items():
        out[nation] = {
            "nextOpponent": d.get("next_opponent"),
            "opponents": d.get("opponents", []),
            "fixtureEase": d.get("attack_multiplier"),
            "cleanSheet": d.get("clean_sheet_prob"),
            "gfPg": d.get("gf_pg"),
            "gaPg": d.get("ga_pg"),
            "wcGames": d.get("wc_games", 0),
        }
    return out


def build_optimal_squad(pool) -> dict:
    squad, starters, captain, score = optimise_ilp(pool, 100.0, 3, 0.1, None, None)
    def view(i):
        p = pool[i]
        return {"id": slug(p["name"], p["nation"]), "name": p["name"], "nation": p["nation"],
                "pos": p["pos"], "price": p["price"], "xp": round(p["xp"], 2)}
    return {
        "xi": [view(i) for i in sorted(starters, key=lambda i: -pool[i]["xp"])],
        "bench": [view(i) for i in squad if i not in starters],
        "captain": view(captain),
        "projectedPoints": round(score, 1),
    }


def main():
    api = ApiFootball(os.environ.get("API_FOOTBALL_KEY"))
    refresh = "--refresh" in sys.argv
    incremental = "--incremental" in sys.argv and not refresh
    mode = "full rebuild" if refresh else "incremental" if incremental else "cached"
    print(f"loading engine pool ({mode})...")
    surv = build_priced_survivors(api, 600, 0, refresh=refresh)
    if incremental:
        surv = incremental_refresh(api, surv)
    print("pulling WC tournament stats...")
    wc = build_wc_forms(api)
    print("pulling FIFA official points + ownership...")
    fifa = fifa_feed_map()
    print("building full FIFA register (depth players)...")
    register = fifa_register()
    print("pulling FIFA per-round points...")
    round_pts = fifa_round_points_map()

    # layer in live ownership + scouting bonus; in-memory only so cache stays clean
    for c in surv:
        fd = fifa.get(c.get("fifa_id")) or {}
        if fd.get("ownership") is not None:
            c["ownership"] = fd["ownership"]
        c["scouting_xp"] = expected_scouting_bonus(c["final_xp"], c.get("ownership"))
        c["final_xp"] = round(c["final_xp"] + c["scouting_xp"], 2)
        c["value"] = round(c["final_xp"] / c["price"], 2) if c.get("price") else None
    pool = _pool(surv)

    print("building players, fixtures, optimal squad, booster plan...")
    players = build_players(pool, wc, fifa, register, round_pts)
    snapshot = {
        "meta": {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "season": 2026,
            "currentRound": current_round_label(),
            "playerCount": len(players),
            "projectedCount": sum(1 for p in players if p["projected"]),
        },
        "rules": RULES,
        "players": players,
        "fixtures": build_fixtures(api),
        "optimalSquad": build_optimal_squad(pool),
        "boosterPlan": booster_planner.plan_data(api),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    kb = OUT.stat().st_size / 1024
    print(f"[wrote {OUT}  ({len(snapshot['players'])} players, {kb:.0f} KB)]")


if __name__ == "__main__":
    raise SystemExit(main())
