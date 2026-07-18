# Pipeline & refresh modes

## The exporter: `export_snapshot.py`
Single entry point that runs the model and writes `../wc-companion/data/snapshot.json`. Steps:
1. Load/build the **priced survivor pool** (projections).
2. Pull **WC tournament stats** (`build_wc_forms`).
3. Pull **FIFA feed** (`fifa_feed_map`) → fresh ownership + official points.
4. Apply **fresh ownership** + **scouting bonus** to `final_xp` (in-memory only; cache stays clean).
5. Build players, fixtures, **optimal squad** (ILP), **booster plan** (Monte-Carlo), detect **current round** (FIFA `rounds.json`).
6. Write the snapshot (only on success — safe on failure).

## Three refresh modes
| Mode | Command | Cost | When |
|---|---|---|---|
| **Cached** (default) | `python export_snapshot.py` | instant | quick manual regen of display data |
| **Incremental** | `python export_snapshot.py --incremental` | ~50 calls / 1–2 min | **the daily 08:00 task** |
| **Full rebuild** | `python export_snapshot.py --refresh` | hundreds of calls / 15–25 min | rarely — only if static (club/intl) windows must change |

### Why incremental is enough mid-tournament
The expensive windows — **club-season form** (clubs are done) and **international friendly form** (none played mid-tournament) — are **static**. Only **WC form** and **fixture context** change daily. `wc_shortlist.incremental_refresh()` reuses the cached static windows, re-pulls just WC form + national context, re-scores the WC + season windows, and re-blends (`recompute_finals`). ~50 calls instead of several hundred, staying under the per-minute limit.

**WC form is aggregated from completed fixtures, not the lagging season aggregate** — see [data-sources.md](data-sources.md). The WC fixtures list is force-refreshed each run so a newly finished matchday is picked up despite the 12h cache.

**When to use `--refresh` after the bug fix:** `--incremental` only re-blends players **already in the pool** — it can't admit a player who joined the WC starting XI after the pool was last built. Run `--refresh` after a new matchday introduces fresh starters (the actual-starter pool admission in §4 of the projection model runs at pool-build time), or those players stay on FIFA's `avgPoints` fallback.

## Caching
- `.pool_cache.pkl` — the built survivor pool (has every per-window value so incremental can re-blend). `--refresh` rebuilds it.
- `.api_cache/` (12h) — API-Football responses.
- `.fifa_cache/` — FIFA feeds.

## File map (model)
| File | Role |
|---|---|
| `scoring.py` | ruleset constants + `expected_points` / `form_to_xpts` (single source of truth) |
| `player_form.py` | parse a stats payload → `PlayerForm` |
| `wc_form.py` | aggregate actual WC2026 stats per player |
| `wc_shortlist.py` | build pool, 4-window blend, `incremental_refresh`, `attach_wc_form`, `recompute_finals` |
| `national_strength.py` | fixtures, clean-sheet, next-fixture-weighted difficulty, team strength |
| `fifa_rankings.py` | FIFA-ranking strength → `team_attack` |
| `set_piece_takers.py` | national set-piece duty + name matching |
| `fifa_fantasy.py` | FIFA feeds (price/ownership/points/scorers) |
| `optimise.py` | ILP optimiser, transfer ladder, `_pool` (pool→flat dicts) |
| `booster_planner.py` | Monte-Carlo booster EV + recommended schedule |
| `export_snapshot.py` | orchestrates everything → snapshot.json |
