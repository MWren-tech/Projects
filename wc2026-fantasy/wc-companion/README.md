# WC2026 Fantasy Companion

A premium AI fantasy-football assistant for the FIFA World Cup 2026, built on top of
the validated Python analytics engine in `../wc_scout`.

It is **not** a generic chatbot: every number (projected points, fixture ease,
ownership, booster EV) comes from the engine, and the AI is grounded so it can only
ever reference players from the official FIFA WC list.

---

## Architecture (and why)

```
wc_scout (Python engine)                wc-companion (Next.js app)
┌────────────────────────┐  snapshot   ┌─────────────────────────────┐
│ wc_shortlist / optimise│ ──────────▶ │ data/snapshot.json (source  │
│ booster_planner        │  (batch)    │ of truth, read-only)        │
│ export_snapshot.py     │             │                             │
└────────────────────────┘             │ lib/engine.ts  advisory math│
                                        │ services/ai/   Claude layer │
                                        │ app/, components/  UI       │
                                        │ Prisma + SQLite  persistence│
                                        └─────────────────────────────┘
```

**Key decisions:**

1. **The Python engine stays the source of truth.** Re-porting the ILP optimiser and
   Monte-Carlo booster model to TypeScript would risk diverging from numbers validated
   over days of work. Instead, `export_snapshot.py` runs the engine once (a batch) and
   writes `data/snapshot.json`. The app reads that. Re-run after each matchday.
2. **The app's own logic is TypeScript** (`lib/engine.ts`): squad validation, best-XI /
   captain selection, team rating, and the transfer marginal-gain ladder — all run at
   request time on engine-sourced players, honouring the real WC2026 rules.
3. **Grounded AI.** `services/ai` injects the engine's player table + your squad + the
   rules into every prompt and constrains Claude to those players only. Structured
   answers use a forced tool so output always matches the `{recommendation, confidence,
   reasoning, expectedOutcome, risk, alternatives}` contract.
4. **Local-first, single user.** Prisma + **SQLite** — no cloud account. Swap the
   datasource to Postgres/Supabase later without touching the models.
5. **Graceful AI degradation.** Without an Anthropic API key, all engine-driven cards,
   tables, the squad builder, transfer ladder and boost strategy still work — only the
   free-text chat is disabled.

---

## Prerequisites

- **Node.js 18+** — not currently installed on this machine. Get it from
  <https://nodejs.org> (LTS). After installing, restart your terminal so `node`/`npm`
  are on PATH.
- **Python** with the `wc_scout` engine working (already set up).
- (Optional) an **Anthropic API key** for the chat — <https://console.anthropic.com>.
  This is pay-as-you-go and **separate from a Claude Pro subscription**.

---

## Setup (run once)

```bash
cd "World Cup 2026/wc-companion"

# 1. Install dependencies
npm install

# 2. Environment
cp .env.example .env.local
#    then open .env.local and paste your ANTHROPIC_API_KEY (optional)

# 3. Generate the engine snapshot (runs the Python exporter)
npm run snapshot          # = python ../wc_scout/export_snapshot.py

# 4. Create the local database and seed it from the snapshot
npm run db:push
npm run db:seed
```

## Run

```bash
npm run dev
# open http://localhost:3000
```

## Refresh data after a matchday

```bash
npm run snapshot && npm run db:seed
# restart `npm run dev` to clear the in-memory snapshot cache
```

---

## Features

| Page | What it does |
|------|--------------|
| **Dashboard** | Engine-optimal XI, captain pick, booster schedule, your squad's AI rating, top picks, differentials |
| **AI Assistant** | Streaming, grounded chat — captains, transfers, differentials, boosts |
| **Squad Builder** | Pick 15 with live budget / formation / nation-cap validation and an AI team rating |
| **Players** | Filter/sort the full pool by xPts, value, differential, ownership; player profiles |
| **Transfer Planner** | The engine's marginal-gain ladder (FREE vs −3 hit, USE vs BANK) + AI rationale |
| **Boost Strategy** | When to play each WC2026 booster (Wildcard / 12th Man / Maximum Captain / Qualification / Mystery) with EV by round |
| **Compare** | Head-to-head player metrics with an engine verdict |

---

## Project structure

```
app/            routes (dashboard, chat, squad, players, transfers, boosts, compare) + API
components/     UI kit + feature components
lib/            snapshot loader, engine advisory math, db, hooks, utils
services/ai/    Claude client, grounded prompts, structured schema, orchestrator
prisma/         SQLite schema + seed
data/           snapshot.json (engine output — git-ignored if large)
types/          shared TypeScript types (mirror the snapshot)
```

## Moving to multi-user / cloud later

- Flip `prisma/schema.prisma` datasource to `postgresql`, set a Supabase `DATABASE_URL`.
- Add Supabase Auth; replace `DEFAULT_USER_ID` / `ensureLocalUser()` with the session user.
- Host the Python exporter on a schedule (Railway/Fly cron) writing the snapshot to
  object storage or a `snapshots` table instead of a local file.
