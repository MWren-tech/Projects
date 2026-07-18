# Data sources, endpoints & join keys

## API-Football v3 (`api_football.py`)
- Base `https://v3.football.api-sports.io`, header `x-apisports-key` (in `wc_scout/.env` as `API_FOOTBALL_KEY`). Paid plan (~7,500/day) but **per-minute limit** → big bursts trigger 61s pauses.
- WC identifiers: **`league=1`, `season=2026`**.
- Responses cached **12h** to `.api_cache/`.
- Used for: club-league season form, recent form, international form, **WC tournament stats**, team/fixture data for national strength.
- **WC tournament stats are aggregated per completed fixture** (`/fixtures` → `/fixtures/players`), NOT read from the season aggregate `/players?league=1&season=2026`. The season aggregate **lags by a round mid-group** (it can still report round-1-only totals after round-2 games finish), which froze projections at round-1 output. `wc_form.build_wc_forms` enumerates finished fixtures and sums each player's per-match lines; it **force-refreshes the WC fixtures list** (`api.fixtures(..., force_refresh=True)`) so newly completed matches aren't hidden by the 12h cache. Per-fixture stats of finished matches are immutable, so they stay cached. Falls back to the season aggregate only when no fixtures are complete (pre-tournament).

## FIFA public fantasy feeds (`fifa_fantasy.py`, no auth — plain `requests`)
Base `https://play.fifa.com/json/fantasy/`. Cached to `.fifa_cache/`. (The browser extension blocks this domain — fetch server-side.)
| Feed | Key fields |
|---|---|
| `players.json` | `id`, name, `squadId`, `position`, `price`, **`percentSelected`** (ownership), `roundsSelected` (per-round ownership), **`stats.totalPoints`**, **`stats.roundPoints`** (per-round), `avgPoints`, `form`, `fifaId` |
| `squads.json` | `id` 1–48 → nation, abbr, group (**2026** file; not the stale `squads_fifa.json`) |
| `rounds.json` | per round: status (`complete`/`playing`/`scheduled`), start/end dates, stage; per match: squads, scores, **`homeGoalScorersAssists` / `awayGoalScorersAssists`** = `{playerId, assistId, isOwnGoal}` |

## Authoritative source per field
- **Price, ownership, official points (total + per-round)** → FIFA feed.
- **Projections + detailed stat breakdown** → API-Football (providers disagree, e.g. assists — FIFA credited Haaland an assist API-Football didn't).
- **Current round / fixture schedule** → FIFA `rounds.json`.

## Join keys
- Engine pool **`fifa_id`** == FIFA `players.json` **`id`**.
- Engine **`pid`** == API-Football player id (for WC stat breakdown).

## What's NOT available
- The per-line **points breakdown** (which exact bonus a player earned) is **behind login** — not public. Hence the app uses FIFA's authoritative total and reconciles any gap.
- Direct-free-kick goal flag — not in any feed.

## Backlog hook (P1)
The **full FIFA register** (`players.json` filtered to the 48 squads via `squads.json`) is the complete universe (~1,250 players). The engine pool is a filtered subset. To include everyone, iterate the register and enrich with engine projections by `fifa_id`; use `avgPoints` as fallback xp. See [ROADMAP](../../ROADMAP.md).
