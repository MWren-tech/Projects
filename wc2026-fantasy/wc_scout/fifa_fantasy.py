"""
FIFA World Cup 2026 Fantasy game data — price & ownership.

API-Football has no fantasy price or ownership (those exist only in the official
game). This module pulls FIFA's public Fantasy JSON feeds:

    players.json      id, firstName, lastName, knownName, squadId, position,
                      price, percentSelected (ownership %), stats{...}
    squads.json       id (1..48) -> name (nation), abbr, group  [the 2026 map;
                      note squads_fifa.json is a stale 2022 file — do not use]

and exposes a per-nation lookup so the shortlist can attach price, ownership and
value (xPts per $m). Responses are cached to disk (12h) like the API-Football
client. No auth required — the player list is public pre-login.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import requests

from set_piece_takers import canonical_nation, name_matches
from scoring import norm_pos

BASE = "https://play.fifa.com/json/fantasy"
CACHE = Path(".fifa_cache")
CACHE_TTL = 43200  # 12h
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


class FifaFantasyError(RuntimeError):
    pass


def _get_json(name: str, *, cache_ttl: int = CACHE_TTL) -> object:
    CACHE.mkdir(exist_ok=True)
    cpath = CACHE / f"{name}"
    if cpath.exists() and (time.time() - cpath.stat().st_mtime) < cache_ttl:
        return json.loads(cpath.read_text(encoding="utf-8"))
    url = f"{BASE}/{name}"
    try:
        resp = requests.get(url, headers={"User-Agent": UA, "Accept": "application/json"}, timeout=30)
    except requests.RequestException as e:
        raise FifaFantasyError(f"{url} -> network error: {e}") from e
    if resp.status_code != 200:
        raise FifaFantasyError(f"{url} -> HTTP {resp.status_code}")
    try:
        data = resp.json()
    except ValueError as e:
        raise FifaFantasyError(f"{url} -> not JSON: {e}") from e
    cpath.write_text(json.dumps(data), encoding="utf-8")
    return data


def _as_list(payload: object) -> list:
    """Feeds are sometimes a bare list, sometimes {'data': [...]} or {'players': [...]}."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("players", "data", "items", "squads", "value"):
            v = payload.get(key)
            if isinstance(v, list):
                return v
        # dict keyed by id -> entry
        if all(isinstance(v, dict) for v in payload.values()):
            return list(payload.values())
    return []


def _squad_nations() -> dict[int, str]:
    out: dict[int, str] = {}
    for s in _as_list(_get_json("squads.json")):
        sid, name = s.get("id"), s.get("name")
        if sid is not None and name:
            out[sid] = canonical_nation(name) or name
    return out


def _player_name(p: dict) -> str:
    return (p.get("knownName")
            or " ".join(x for x in (p.get("firstName"), p.get("lastName")) if x)
            or p.get("lastName") or "").strip()


def load_fifa_players() -> dict[str, list[dict]]:
    """nation -> [ {name, price, ownership, position, fifa_points, fifa_form} ]"""
    nations = _squad_nations()
    out: dict[str, list[dict]] = {}
    for p in _as_list(_get_json("players.json")):
        nation = nations.get(p.get("squadId"))
        if not nation:
            continue
        stats = p.get("stats") or {}
        out.setdefault(nation, []).append({
            "id": p.get("id"),
            "name": _player_name(p),
            "price": p.get("price"),
            "ownership": p.get("percentSelected"),
            "position": norm_pos(p.get("position") or ""),
            "fifa_points": stats.get("totalPoints"),
            "fifa_form": stats.get("form"),
        })
    return out


def match_price(fifa_by_nation: dict[str, list[dict]], nation: str,
                player_name: str, position: str | None = None) -> dict | None:
    """Best FIFA price/ownership entry for a player, matched within their nation."""
    candidates = fifa_by_nation.get(nation, [])
    best = None
    for f in candidates:
        if not name_matches(f["name"], player_name):
            continue
        # prefer a position-consistent match when several names collide
        if position and f["position"] and f["position"] == position:
            return f
        best = best or f
    return best
