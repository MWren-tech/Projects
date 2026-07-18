# The snapshot contract (`wc-companion/data/snapshot.json`)

The **only** interface between the model and the app. Produced by `wc_scout/export_snapshot.py`; typed in `wc-companion/types/index.ts`. **Changing the shape requires updating both sides + this doc.**

## Top level
```ts
{ meta, rules, players[], fixtures{}, optimalSquad, boosterPlan }
```

### meta
`{ generatedAt, season, currentRound, playerCount, projectedCount }` — `currentRound` auto-detected from FIFA `rounds.json` (e.g. "MD2", "R32", "Final"). `playerCount` is the full FIFA register (~1,480); `projectedCount` is how many have a full engine projection (`projected: true`).

### rules
Budget, squad shape, formations, transfer allocations, max-per-nation by stage, booster list, scoring table. Mirrors [scoring-rules.md](../model/scoring-rules.md).

### players[] (full FIFA register — every WC-squad player across the 48 nations)
```ts
{
  id,            // ASCII slug, e.g. "k-mbappe-france" (accents normalised → no 404s); unique
  name, nation, club, pos,          // pos: GK|DEF|MID|FWD; club null for fallback players
  price, xp,                        // xp = final_xp incl. scouting bonus (projected); FIFA avgPoints (fallback)
  ownership, value,                 // ownership = FIFA percentSelected; value = xp/price
  goals, assists, g90, a90,         // season form (null for fallback players)
  cleanSheet, fixtureEase, setPieces,
  rating, startProb,
  aiRating,                         // 0–100 percentile within position (null for fallback players)
  differential,                     // 0–100
  scoutingBonus,                    // expected diff bonus already in xp (0 for fallback)
  wcStats,                          // tournament tally + points, or null
  roundPoints,                      // FIFA per-round official points (see below)
  projected                         // see below
}
```

**`projected` (boolean) — matched vs fallback.** Distinguishes the two tiers in `players[]`:
- `projected: true` — the player is in the **engine pool** (matched to the engine by `fifa_id`). Full projection: `xp` is the blended `final_xp` (incl. scouting bonus), all form / fixture / start-prob fields populated, `wcStats` carries the API-Football stat breakdown reconciled to FIFA's official total.
- `projected: false` — a **full-register fallback** player the engine pool didn't cover (depth / weak-league / low-minute, e.g. Cyle Larin, Wan-Bissaka). FIFA is authoritative: `price`, `ownership`, `pos`, and (when they've featured) `wcStats.totalPoints` come straight from the feed. `xp` is a **fallback** = FIFA `stats.avgPoints` (per-round average); engine-only fields (`goals`, `g90`, `cleanSheet`, `startProb`, `aiRating`, `rating`, …) are `null` and `club` is `null`. `wcStats`, when present, carries `official: true` (FIFA total is authoritative). Its **`breakdown` is populated** when the player can be matched to their API-Football WC form by **name + canonical nation** (fallback players have no `fifa_id`/`pid`, so the per-stat lines are attached via this secondary name+nation join, guarded by position) — e.g. Elijah Just (90 mins, 2 goals, MD1 16) shows full stat lines. When no name+nation match is found (e.g. a player API-Football logged 0 WC minutes for, like Wan-Bissaka), `breakdown` is an **empty array** (FIFA total only, no per-stat lines).

Consumers should not treat a fallback player's `xp` as a true projection — it is a coarse FIFA-average stand-in so depth players still rank and surface in lists/search.

### wcStats (per player, null until they've featured)
```ts
{
  minutes, appearances, starts, goals, assists, saves, penSaved,
  tackles, chances, shotsOn, yellows, reds, penWon, penConceded,
  goalsConceded, rating,
  breakdown: [{ label, count, pts }],   // count may be null (reconciliation line)
  totalPoints,                          // FIFA's authoritative total when available
  official                              // true = totalPoints is FIFA's own figure
}
```
The breakdown is API-Football-derived; any gap to FIFA's `totalPoints` appears as an "Other (official scoring)" line so it reconciles exactly. When the player is under the scouting-ownership threshold (`<5%`) and that gap is attributable to the FIFA scouting bonus (+2 per qualifying haul), the bonus portion is split out into its own "Scouting bonus (<5% owned)" line (with `count` = number of qualifying matches) before any residual reconciliation line.

### roundPoints (per player — always present; empty array until they've featured)
```ts
roundPoints: [{ round, pts }]   // e.g. [{ "round": "MD1", "pts": 8 }, { "round": "MD2", "pts": 13 }]
```
FIFA's authoritative per-round official points, straight from `players.json` `stats.roundPoints` (same source as `wcStats.totalPoints`). Ordered by round; `round` is the snapshot round label ("MD1".."MD3", "R32", "R16", "QF", "SF", "Final"). Present for **every** player — engine-pool and FIFA-fallback alike (no API-Football match needed). The array **sums exactly to `wcStats.totalPoints`** when that exists; an empty array means no rounds recorded yet. Purely additive; consumers must not invent per-round values.

### fixtures{} (keyed by nation)
`{ nextOpponent, opponents[], fixtureEase, cleanSheet, gfPg, gaPg, wcGames }`

### optimalSquad
`{ xi[], bench[], captain, projectedPoints }` — each player view `{ id, name, nation, pos, price, xp }`.

### boosterPlan
`{ perRound[], schedule{} }` — per-round EV for Maximum Captain / 12th Man / Qualification, plus the recommended round per chip.

## Consumers in the app
- `lib/snapshot.ts` loads + hot-reloads (on mtime change).
- `lib/engine.ts` does client advisory math on `players` (validation, best-XI, transfers, subs).
- Pages render directly; `services/ai` injects a relevant subset into Claude prompts.

## Consumed-today notes
- The **Points** column in the players list + squad picker reads `wcStats.totalPoints` (FIFA's authoritative tournament total; shows "—" until a player has featured). No new field was added — the app reads the existing nested value.

## Pending contract changes (P1)
- Promote **`points` (FIFA total)** to a top-level player field (today the app derives it from `wcStats.totalPoints`).
- ~~Add **`roundPoints` (per-round)**~~ — DONE. Every player now carries `roundPoints` (FIFA per-round official points; see the live contract above). The profile round-by-round breakdown can read it directly.
- ~~Expand `players[]` to the **full FIFA register**~~ — DONE. `players[]` now spans every WC-squad player; `projected` flags engine-projected vs FIFA-fallback (`meta.projectedCount`).
