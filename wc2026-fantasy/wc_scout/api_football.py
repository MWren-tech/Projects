"""
API-Football v3 wrapper for the WC2026 scout pipeline.

Key is read from API_FOOTBALL_KEY (env or wc_scout/.env).
Free tier is ~100 req/day so everything is cached to disk for 12h.
Delete .api_cache/ to force fresh pulls.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

import requests

BASE_URL = "https://v3.football.api-sports.io"
CACHE_DIR = Path(os.environ.get("API_FOOTBALL_CACHE", ".api_cache"))
CACHE_TTL_SECONDS = int(os.environ.get("API_FOOTBALL_CACHE_TTL", 60 * 60 * 12))  # 12h


class ApiFootballError(RuntimeError):
    pass


def _key_from_dotenv() -> str | None:
    """Read API_FOOTBALL_KEY from .env in cwd or next to this file."""
    candidates = [Path(".env"), Path(__file__).parent / ".env"]
    for env in candidates:
        if not env.exists():
            continue
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("API_FOOTBALL_KEY=") and "=" in line:
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


class ApiFootball:
    """Thin, cache-backed wrapper around the API-Football v3 REST endpoints."""

    def __init__(self, api_key: str | None = None, *, use_cache: bool = True):
        self.api_key = api_key or os.environ.get("API_FOOTBALL_KEY") or _key_from_dotenv()
        if not self.api_key:
            raise ApiFootballError(
                "No API key. Set API_FOOTBALL_KEY in your environment "
                "(do not hardcode it)."
            )
        self.use_cache = use_cache
        if use_cache:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "x-apisports-key": self.api_key,
                "Accept": "application/json",
            }
        )
        self.requests_remaining: int | None = None  # set from response headers

    # ---- internal helpers -------------------------------------------------

    def _cache_path(self, endpoint: str, params: dict[str, Any]) -> Path:
        raw = endpoint + json.dumps(params, sort_keys=True)
        digest = hashlib.sha256(raw.encode()).hexdigest()[:24]
        safe = endpoint.strip("/").replace("/", "_")
        return CACHE_DIR / f"{safe}__{digest}.json"

    def _read_cache(self, path: Path) -> dict | None:
        if not (self.use_cache and path.exists()):
            return None
        age = time.time() - path.stat().st_mtime
        if age > CACHE_TTL_SECONDS:
            return None
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return None

    def _write_cache(self, path: Path, payload: dict) -> None:
        if self.use_cache:
            try:
                path.write_text(json.dumps(payload))
            except OSError:
                pass  # caching is best-effort

    def get(
        self, endpoint: str, params: dict[str, Any] | None = None, *,
        max_retries: int = 3, force_refresh: bool = False
    ) -> dict:
        """GET an endpoint; returns parsed JSON, cached on disk.
        force_refresh skips the read cache but still writes back."""
        params = params or {}
        cache_path = self._cache_path(endpoint, params)

        cached = None if force_refresh else self._read_cache(cache_path)
        if cached is not None:
            return cached

        url = f"{BASE_URL}/{endpoint.lstrip('/')}"
        backoff = 2.0
        for attempt in range(1, max_retries + 1):
            resp = self.session.get(url, params=params, timeout=30)

            remaining = resp.headers.get("x-ratelimit-requests-remaining")
            if remaining is not None:
                try:
                    self.requests_remaining = int(remaining)
                except ValueError:
                    pass

            if resp.status_code == 429:
                if attempt == max_retries:
                    raise ApiFootballError("Rate limited (429) after retries.")
                time.sleep(backoff)
                backoff *= 2
                continue

            if resp.status_code != 200:
                raise ApiFootballError(
                    f"{endpoint} returned HTTP {resp.status_code}: {resp.text[:200]}"
                )

            body = resp.json()
            # logical errors come back as HTTP 200 with an errors field
            errors = body.get("errors")
            if errors:
                # per-minute limit returns here (not 429) — wait it out
                if isinstance(errors, dict) and "rateLimit" in errors:
                    if attempt == max_retries:
                        raise ApiFootballError(
                            f"Per-minute rate limit not cleared after retries: {errors}"
                        )
                    wait = 61  # the window is per-minute; wait it out
                    print(f"  [per-minute limit hit; pausing {wait}s then retrying...]")
                    time.sleep(wait)
                    continue
                raise ApiFootballError(f"{endpoint} API error: {errors}")

            self._write_cache(cache_path, body)
            return body

        raise ApiFootballError(f"{endpoint}: exhausted retries.")

    @staticmethod
    def response(body: dict) -> list:
        """Pull the 'response' array out of a v3 body."""
        return body.get("response", [])

    # ---- endpoint convenience methods ------------------------------------

    def fixtures(self, *, force_refresh: bool = False, **params) -> list:
        """league=1, season=2026, team=..., date=YYYY-MM-DD, next=N"""
        return self.response(self.get("fixtures", params, force_refresh=force_refresh))

    def odds(self, **params) -> list:
        """Pre-match odds. e.g. fixture=..., league=..., season=..., bet=1"""
        return self.response(self.get("odds", params))

    def players(self, **params) -> list:
        """Player stats. e.g. team=..., season=2025, league=..., id=..., page=N"""
        return self.response(self.get("players", params))

    def player_stats_paginated(self, page_pause: float = 0.2, **params) -> list:
        """Pull all pages of /players (~20 per page). page_pause keeps us under the rate cap."""
        out: list = []
        page = 1
        while True:
            body = self.get("players", {**params, "page": page})
            out.extend(self.response(body))
            paging = body.get("paging", {})
            if page >= paging.get("total", 1):
                break
            page += 1
            time.sleep(page_pause)
        return out

    def injuries(self, **params) -> list:
        """e.g. league=..., season=..., team=..., fixture=..."""
        return self.response(self.get("injuries", params))

    def predictions(self, fixture: int) -> list:
        """Win/CS signals + season gf/ga averages."""
        return self.response(self.get("predictions", {"fixture": fixture}))

    def lineups(self, fixture: int) -> list:
        return self.response(self.get("fixtures/lineups", {"fixture": fixture}))

    def fixtures_players(self, fixture: int) -> list:
        """Per-match player stats + rating for one fixture (both teams)."""
        return self.response(self.get("fixtures/players", {"fixture": fixture}))

    def standings(self, **params) -> list:
        """e.g. league=..., season=..."""
        return self.response(self.get("standings", params))

    def teams(self, **params) -> list:
        return self.response(self.get("teams", params))

    def search_team(self, name: str) -> list:
        return self.teams(search=name)
