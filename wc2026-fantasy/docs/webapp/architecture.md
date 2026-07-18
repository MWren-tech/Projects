# Web app architecture (`wc-companion/`)

Next.js 14 (App Router) + TypeScript + Tailwind + Prisma/SQLite. Local, single-user.

## Structure
```
app/            routes + API (route handlers)
  page.tsx          Dashboard
  players/          list + [id] profile
  squad/            Squad Builder (reference UI)
  transfers/  boosts/  compare/  chat/
  api/chat  api/recommend  api/squad
components/      feature components (SquadPitch, PlayerPicker, ...)
  ui/primitives.tsx   the design system (Button, Badge, Alert, SegmentedControl, ...)
lib/
  snapshot.ts       load + hot-reload snapshot.json (mtime cache)
  engine.ts         client advisory math (validate, pickBestXI, suggestTransfers, subs, lineup)
  useSquad.ts       shared squad store (localStorage, useSyncExternalStore)
  kits.ts  utils.ts
services/ai/      Claude client, grounded prompts, structured zod schema, assistant
prisma/           schema.prisma (SQLite) + seed.ts
data/             snapshot.json (from the model)
types/index.ts    mirrors the snapshot contract
scripts/          daily-refresh.ps1
```

## Data & state
- **Read path:** server components call `getSnapshot()` (`lib/snapshot.ts`) → render. No request-time call to the model.
- **User squad:** `useSquad()` keeps the working 15 (+ manual bench order) in `localStorage` via a shared external store, so every component stays in sync; "Save" persists to SQLite (`/api/squad`).
- **Advisory math** is pure TS in `lib/engine.ts` (no server round-trip): squad validation, best-XI/formation, captain/vice, transfer ladder, legal substitutions.

## Database (Prisma + SQLite)
- `DATABASE_URL` lives in **`.env`** (Prisma CLI reads `.env`, not `.env.local`). Secrets like `ANTHROPIC_API_KEY` live in `.env.local`.
- Seeded from the snapshot (`npm run db:seed` → `tsx prisma/seed.ts`, which self-loads `.env`).
- Tables: User, Player, PlayerStat, Fixture, Squad, SquadPlayer, Transfer, BoostUsage, AIRecommendation, Watchlist, FavouritePlayer.

## Conventions
- Player ids are **ASCII slugs** (accents normalised) — keep it that way.
- Keep `components/ui` primitives backward-compatible (other pages depend on them).
- See [design-system.md](design-system.md) and [ai-layer.md](ai-layer.md).

## Scaling later (not now)
Switch Prisma datasource to Postgres/Supabase + add auth (replace `DEFAULT_USER_ID`/`ensureLocalUser`); host the exporter on a cron writing the snapshot to storage instead of a local file.
