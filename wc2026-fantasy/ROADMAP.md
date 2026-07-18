# Roadmap & backlog

Single source of truth for "what's done" and "what's next". Update this instead of relying on chat memory.

## ✅ Shipped
**Model (`wc_scout/`)**
- 4-window projection blend (season / club-recent / country / WC), league strength, fixture difficulty, team strength, national clean-sheet, set-piece duty.
- WC-adjusted start probability (a benched starter like Guéhi is correctly down-weighted).
- ILP optimiser (15-man squad, formation-valid XI, captain, max-3/nation), transfer marginal-gain ladder, Monte-Carlo booster planner.
- FIFA feed integration: price, **ownership**, **official points**, per-round points.
- **Scouting (differential) bonus priced into projections** for <5%-owned players; in the per-game breakdown the realised bonus is split out as a clear "Scouting bonus (<5% owned)" line instead of being lumped into "Other (official scoring)".
- Snapshot exporter with three refresh modes; cheap **incremental** daily refresh.
- Auto current-round detection from FIFA `rounds.json`.
- **Cumulative WC form fix (2026-06-19):** WC stats are now aggregated per completed fixture (`/fixtures/players`) instead of the season aggregate `/players?league=1&season=2026`, which lagged a round mid-group and froze projections at round-1 totals. The WC fixtures list is force-refreshed so a newly finished matchday isn't hidden by the 12h cache. Players with a genuine WC start that the pre-tournament probable XI missed (e.g. **Isak, N. Brown, E. Just**) are now admitted to the engine pool and get a real blended projection instead of FIFA `avgPoints` (run `--refresh` to pick up new starters). Off-the-bench cameos (e.g. **Undav**, 26') stay register-fallback by design.

**App (`wc-companion/`)**
- Dashboard, Players, **Squad Builder (visual pitch + dugout, drag-and-drop subs, transfers)**, Transfer Planner, Boost Strategy, AI Chat, Compare.
- Grounded Claude chat + structured recommendations.
- Prisma + SQLite persistence; daily auto-refresh via Windows Task Scheduler (08:00).
- Design system + WCAG 2.2 AA pass **on the Squad Builder** (tokens, focus, states, keyboard).

## 🔜 Backlog (prioritised)

### ✅ P1 — Full player register (DONE)
**Was:** the snapshot only contained the engine pool (~328 players who passed a 600-minute club-form filter in strong leagues); squad-depth / weak-league / low-minute players (e.g. **Cyle Larin, Wan-Bissaka**) were missing.
**Shipped:** `players[]` now spans the **full FIFA register** (~1,480 WC-squad players). Engine-matched players (`projected: true`, 328) keep their full projection; unmatched players (`projected: false`) get FIFA `avgPoints` as fallback `xp` plus FIFA price / ownership / official points / position. New fields `projected` (per player) and `meta.projectedCount` — see [docs/data/snapshot-contract.md](docs/data/snapshot-contract.md).

### P1 — Points column + per-game breakdown
Every player has FIFA `totalPoints` and per-round `roundPoints` (available for all, no API match needed). Add:
- a **Points** column to the players list and squad picker,
- a **per-game breakdown** (round-by-round) on the profile, alongside the existing `wcStats` stat breakdown.

### P2 — Roll the design system to all pages
Only the Squad Builder is at full AA polish. Apply the same tokens / states / a11y to Dashboard, Players, Transfers, Boosts, Chat, Compare.

### P3 — FIFA-accurate goal/assist attribution
`rounds.json` has FIFA's own scorers + assisters per match (fixes provider gaps like the Haaland assist at source). Optionally fold into `wcStats` instead of the reconciliation line.

### P3 — Multi-user / cloud (only if validated)
Flip Prisma to Postgres/Supabase, add auth, host the exporter on a cron. See [docs/webapp/architecture.md](docs/webapp/architecture.md) "scaling later".

## 🧠 Key decisions (ADR-lite)
- **FIFA points are authoritative** for "points so far"; API-Football is for projections only (providers disagree, e.g. assists).
- **Don't rebuild the pool daily** — club/international form is static mid-tournament; only WC form + fixtures change (→ incremental mode).
- **Local-first, single-user** — SQLite, no cloud, to keep cost/complexity down until validated.
- **ASCII player-id slugs** — accented URLs (Mbappé) 404'd; slugs are normalised.
