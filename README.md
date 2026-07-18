# Projects

A collection of things I've built.

## [wc2026-fantasy](wc2026-fantasy/)

An end-to-end, locally-hosted fantasy-football companion for the **FIFA World Cup 2026** —
from live-data ETL to a playable web app.

- **Model** (`wc_scout/`, Python) — pulls API-Football + official FIFA-fantasy feeds and computes
  its own player projections, an ILP-optimised squad, a transfer ladder and a booster plan.
- **Companion** (`wc-companion/`, Next.js + TypeScript) — squad builder, player analytics,
  transfers and an optional Claude chat layer grounded in the model's own numbers.

The two halves connect through a single JSON contract (`snapshot.json`). A working sample is
bundled, so the app runs out of the box. See [wc2026-fantasy/README.md](wc2026-fantasy/README.md).
