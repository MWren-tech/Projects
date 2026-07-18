# System architecture

## The two halves and the contract between them

```
┌─────────────────────────── wc_scout (Python model) ───────────────────────────┐
│                                                                                │
│  API-Football v3 ─┐                                                            │
│  (league=1,       │   build_priced_survivors()  ──►  4-window projection blend │
│   season=2026)    ├─► + national_strength (fixtures/CS/difficulty)             │
│  FIFA feeds ──────┘   + scouting bonus + ILP optimiser + booster planner       │
│  (players/squads/                                                              │
│   rounds .json)                 │                                              │
│                                 ▼                                              │
│                       export_snapshot.py                                       │
└─────────────────────────────────│──────────────────────────────────────────────┘
                                   ▼  writes (read-only contract)
                       wc-companion/data/snapshot.json
                                   │
┌──────────────────────────────────▼──── wc-companion (Next.js app) ─────────────┐
│  lib/snapshot.ts (loads + hot-reloads)                                          │
│  lib/engine.ts (client advisory math: validate, best-XI, transfers, subs)       │
│  app/ pages (dashboard, players, squad, transfers, boosts, compare, chat)       │
│  services/ai/ (Claude, grounded to the snapshot's player list)                  │
│  Prisma + SQLite (user squad / watchlist / history)                             │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Principles
- **One-way data flow.** The model produces `snapshot.json`; the app consumes it. The app never calls the model at request time and never invents data.
- **Numbers vs narrative.** All numbers come from the model. Claude (in the app) only explains/arranges them, grounded to the snapshot's players.
- **Local-first, single-user.** No cloud required: SQLite + a local snapshot file. A Windows scheduled task refreshes data daily.

## Runtime / refresh flow
1. **08:00 daily** — `wc-companion/scripts/daily-refresh.ps1` runs `export_snapshot.py --incremental` (re-pull WC form + fixtures + FIFA feed, re-blend) then re-seeds the DB.
2. The exporter writes `snapshot.json`; `lib/snapshot.ts` notices the changed mtime and reloads — updated data appears without a server restart.
3. The user interacts with the app; the squad lives in `localStorage` (instant) and can be saved to SQLite.

## Why it's split this way
- The validated projection model is **Python** (ILP, Monte-Carlo, stats). Re-porting it to TS would risk diverging from numbers built over weeks. So Python stays the producer; the app does only light advisory math in `lib/engine.ts`.
- Caching the model output as a snapshot keeps the app fast and cheap, and decouples release cycles.

See also: [model pipeline](../model/pipeline.md) · [snapshot contract](../data/snapshot-contract.md) · [app architecture](../webapp/architecture.md).
