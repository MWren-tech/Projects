# Project context for Claude Code

> Read this first. It replaces chat history — pull details from the linked docs, not from past conversations.

## What this is
A local, single-user **WC2026 fantasy-football companion**. Two workspaces under this root:
- **`wc_scout/`** — the Python analytics **model**. Pulls API-Football + FIFA feeds, computes projections / optimal squad / transfers / boosters, and exports `snapshot.json`.
- **`wc-companion/`** — the Next.js **web app**. Reads `snapshot.json` and presents it, with a Claude chat layer grounded in that data.

The two only touch through **`wc-companion/data/snapshot.json`** (the contract). The model never imports the app; the app never calls the model at request time.

## Golden rules
1. **The model is the source of truth for numbers.** The app only arranges/displays engine output and must never invent players, prices or stats. Claude in the app is grounded to the snapshot's player list only.
2. **Don't break the data contract** without updating both sides + [docs/data/snapshot-contract.md](docs/data/snapshot-contract.md).
3. **Don't rename `wc_scout/` or `wc-companion/`** — the scheduled task, npm scripts and imports depend on these paths.
4. **Keep it local & free of cloud deps.** SQLite + Prisma; no Supabase/cloud required.
5. **Verify before claiming done.** Python: `python -m py_compile <files>`. App: typecheck via `node node_modules/typescript/bin/tsc --noEmit` (run from `wc-companion/`).

## Conventions
- Python: match existing style in `wc_scout/`; keep the FIFA scoring constants in `scoring.py` as the single source of truth.
- TypeScript/React: Next 14 App Router; design tokens + accessible primitives in `wc-companion/components/ui`; WCAG 2.2 AA. See [docs/webapp/design-system.md](docs/webapp/design-system.md).
- Co-author trailer on commits: `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.

## Specialised agents (use the right one)
Defined in [.claude/agents/](.claude/agents/). Each reads its own docs.
- **architect** — planning, prioritisation, trade-offs, "what next". Read-only advisor.
- **model-engineer** — anything in `wc_scout/` (projections, pipeline, scoring).
- **frontend-engineer** — anything in `wc-companion/` (UI, UX, a11y, AI layer).
- **data-engineer** — API-Football / FIFA feeds, the snapshot exporter, the daily refresh.
- **reviewer** — review/verify a change (typecheck, compile, tests, code-review).

## Where things live
- Scoring rules → [docs/model/scoring-rules.md](docs/model/scoring-rules.md)
- How projections work → [docs/model/projection-model.md](docs/model/projection-model.md)
- Data sources & endpoints → [docs/model/data-sources.md](docs/model/data-sources.md)
- Pipeline & refresh modes → [docs/model/pipeline.md](docs/model/pipeline.md)
- App architecture → [docs/webapp/architecture.md](docs/webapp/architecture.md)
- Run / deploy / troubleshoot → [docs/ops/runbook.md](docs/ops/runbook.md)
- Backlog & decisions → [ROADMAP.md](ROADMAP.md)
