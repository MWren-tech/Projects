# Projects

Selected engineering projects by Michael Wren ([@MWren-tech](https://github.com/MWren-tech)).

[![CI](https://github.com/MWren-tech/Projects/actions/workflows/ci.yml/badge.svg)](https://github.com/MWren-tech/Projects/actions/workflows/ci.yml)

---

## [wc2026-fantasy](wc2026-fantasy/) — data → model → product, end to end

**[▶ Live demo](https://wc-azure.vercel.app/)**  ·  **[Full write-up](wc2026-fantasy/README.md)**

An end-to-end, locally-hosted fantasy-football companion for the **FIFA World Cup 2026** — from
live-data ETL through an analytics model to a deployed, playable web app.

- **Model** (`wc_scout/`, Python) — pulls API-Football + official FIFA-fantasy feeds and computes
  its own player projections, an **ILP-optimised** squad, a transfer ladder and a booster plan;
  exports one `snapshot.json`.
- **Companion** (`wc-companion/`, Next.js 14 / TypeScript) — squad builder, player analytics,
  transfer planner, and an optional Claude chat layer **grounded** in the model's own numbers.

The two halves are decoupled through a single JSON contract. A working snapshot is bundled, so
the app runs out of the box; the engine, scoring model and app logic are unit-tested in CI.

`Python` · `Next.js` · `TypeScript` · `Tailwind` · `Prisma/SQLite` · `PuLP` · `Anthropic API` · `Vercel`
