# WC2026 Fantasy — from live data to a playable companion

An end-to-end, locally-hosted fantasy-football companion for the **FIFA World Cup 2026**.
It pulls live football and official FIFA-fantasy data, computes its own player projections,
optimal squad, transfer ladder and booster (chip) plan, and serves it all through a
Next.js web app with an optional Claude chat layer grounded in the model's own numbers.

**Stack:** Python (ETL + analytics) · Next.js 14 / TypeScript / Tailwind (app) · SQLite + Prisma · Anthropic API (optional chat)

> **Live demo:** _add your Vercel URL here after deploying_ — one-click setup in [DEPLOY.md](DEPLOY.md).

Built as a two-part monorepo. The two halves are deliberately decoupled and touch through
exactly **one file** — `wc-companion/data/snapshot.json`:

```
   EXTRACT              TRANSFORM                       LOAD            DISPLAY
 ┌───────────┐   ┌───────────────────────┐   ┌──────────────────┐   ┌──────────────┐
 │ API-Football│  │  wc_scout (Python)     │  │  snapshot.json    │  │ wc-companion │
 │ FIFA feeds  │─►│  projections · scoring │─►│  (the contract)   │─►│  Next.js UI  │
 │ (HTTP)      │  │  optimiser · boosters  │  │  1,484 players    │  │ + Claude chat│
 └───────────┘   └───────────────────────┘   └──────────────────┘   └──────────────┘
                        run daily / on demand         read-only         locally hosted
```

The model is the **only** source of numbers; the app never invents players, prices or
stats — it arranges and displays engine output, and the in-app assistant is grounded to
the snapshot's player list.

---

## Screenshots

The companion running locally against the bundled snapshot.

**Dashboard** — engine optimal XI, captain pick, next booster and top differential at a glance:

![Dashboard](docs/screenshots/dashboard.png)

| Squad Builder | Players |
|---|---|
| ![Squad Builder](docs/screenshots/squad.png) | ![Players](docs/screenshots/players.png) |
| **Transfer Planner** | **Boost Strategy** |
| ![Transfer Planner](docs/screenshots/transfers.png) | ![Boost Strategy](docs/screenshots/boosts.png) |

- **Squad Builder** — drag-and-drop pitch, live budget / formation / max-per-nation validation, one-click auto-pick of the engine's optimal XI.
- **Players** — the full 1,484-player pool, searchable and sortable by projected points, price, ownership, value and fixture difficulty.
- **Transfer Planner** — the engine's marginal-gain ladder (points gained per transfer, free vs. −3 hit).
- **Boost Strategy** — expected value of each one-time chip in every remaining round, with the recommended schedule.

---

## Repository layout

```
wc2026-fantasy/
├── wc_scout/              THE MODEL — Python analytics engine (ETL + ranking)
│   ├── export_snapshot.py     entry point: runs the pipeline, writes snapshot.json
│   ├── wc_shortlist.py        builds + incrementally refreshes the player pool
│   ├── optimise.py            ILP optimal-squad solver (PuLP)
│   ├── booster_planner.py     per-round expected value for each chip
│   ├── scoring.py             FIFA scoring constants — single source of truth
│   ├── ... (23 modules)       form windows, national strength, FIFA feeds, set pieces
│   ├── current_squad.json     your held squad (an input to the booster/transfer logic)
│   ├── requirements.txt
│   └── sample-output/         human-readable ranking artifacts the engine produces
│
├── wc-companion/          THE APP — Next.js web companion
│   ├── app/                   App Router pages: players, squad, transfers, boosts, chat
│   ├── components/            squad builder, pitch, tables, compare tool, AI panels
│   ├── services/ai/           the grounded Claude assistant layer
│   ├── lib/ · prisma/         snapshot loader, SQLite persistence
│   └── data/snapshot.json     ◄─ written by the model, read by the app (bundled sample)
│
├── docs/                  architecture, scoring rules, projection model, runbook…
├── reference-data/        source scoring-stat spreadsheets + squad lists (research)
└── .claude/              specialised Claude Code agents used to build this
```

---

## Quickstart

There are two independent things you can run. **You do not need the Python engine to see
the app** — a working `snapshot.json` is bundled, so the app renders the full dataset out
of the box.

### A. Run the app (no API key needed)

```powershell
cd wc-companion
npm install
Copy-Item .env.example .env           # Prisma + the app both read .env; edit to add keys
npm run db:push                       # create the local SQLite db
npm run db:seed                       # load players from the bundled snapshot
npm run dev                           # http://localhost:3000
```

> **Use `.env`, not `.env.local`.** The Prisma CLI (`db:push`) and the seed script only read
> `.env`, so `DATABASE_URL` must live there. Next.js reads `.env` too, so this one file covers
> everything.

Everything except the free-text AI chat works with no keys at all. The chat layer needs a
pay-as-you-go `ANTHROPIC_API_KEY` (not a Claude subscription) — see `wc-companion/.env.example`.

### B. Regenerate the model from live data (needs an API-Football key)

```powershell
cd wc_scout
python -m venv .venv; .\.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env           # paste your API_FOOTBALL_KEY (free tier works)

python export_snapshot.py --refresh       # full rebuild (slow, ~hundreds of API calls)
# thereafter, the fast daily-style refresh:
python export_snapshot.py --incremental   # re-pull WC form + fixtures, re-blend (~1-2 min)
```

This rewrites `../wc-companion/data/snapshot.json`; the app hot-reloads on the file change.
A free API-Football key (~100 requests/day) is enough for `--incremental`; the engine caches
every response to disk to stay under the limit. Get one at <https://www.api-football.com>.

---

## How the ranking works (the Transform step)

Each player's **projected points (xp)** blends several scored windows through the official
FIFA-fantasy ruleset in [`scoring.py`](wc_scout/scoring.py):

- **Club form** — recent per-90 output from domestic leagues (`recent_form.py`)
- **International form** — national-team form over recent windows (`country_form.py`)
- **Live WC form** — actual tournament stats once matches are played (`wc_form.py`)
- **Fixture ease & team strength** — FIFA ranking blended with form, used as an
  advance-probability proxy for the knockouts (`national_strength.py`, `fifa_rankings.py`)
- **Start probability** — projected minutes / probable XI (`probable_xi.py`)
- **Set-piece duty** and a **scouting-bonus** term that prices in low-owned upside

From that pool the engine builds the **optimal squad** (an integer-linear-program under the
budget, formation and max-per-nation rules) and a **booster plan** that assigns each chip to
its highest-EV round. See [`docs/model/projection-model.md`](docs/model/projection-model.md)
and [`docs/data/snapshot-contract.md`](docs/data/snapshot-contract.md) for the details and the
exact JSON contract.

Want to see the output without running anything? Browse
[`wc_scout/sample-output/`](wc_scout/sample-output/) for the ranked lists and reports the
engine emits.

---

## Data sources

- **[API-Football](https://www.api-football.com)** — fixtures, lineups, per-match player stats,
  predictions (club + international competitions).
- **FIFA official fantasy feed** — authoritative prices, ownership, official points and the
  full 48-squad register.

All external calls are cached to disk (`.api_cache/`, `.fifa_cache/`) and never committed.

---

## Documentation

| Topic | Doc |
|---|---|
| Big-picture architecture | [docs/overview/architecture.md](docs/overview/architecture.md) |
| Scoring rules | [docs/model/scoring-rules.md](docs/model/scoring-rules.md) |
| Projection model | [docs/model/projection-model.md](docs/model/projection-model.md) |
| Data sources & endpoints | [docs/model/data-sources.md](docs/model/data-sources.md) |
| Pipeline & refresh modes | [docs/model/pipeline.md](docs/model/pipeline.md) |
| The snapshot.json contract | [docs/data/snapshot-contract.md](docs/data/snapshot-contract.md) |
| App architecture | [docs/webapp/architecture.md](docs/webapp/architecture.md) |
| Run / troubleshoot | [docs/ops/runbook.md](docs/ops/runbook.md) |

---

## Notes

- **Local & free by design** — SQLite + Prisma, no cloud account required.
- The bundled `snapshot.json` is a point-in-time sample; regenerate it (step B) for live numbers.
- Secrets are never committed — copy the `.env.example` templates and fill in your own keys.
