# wc-companion — the app (Next.js web companion)

This is the **app** workspace. It reads `data/snapshot.json` (produced by `../wc_scout`) and presents it, with a grounded Claude chat layer.

➡️ **Work here with the `frontend-engineer` agent.** Open Claude Code at the repo root (`World Cup 2026/`) so agents + docs resolve.

Read before changing anything:
- App architecture: `../docs/webapp/architecture.md`
- Design system & accessibility (WCAG 2.2 AA): `../docs/webapp/design-system.md`
- AI layer (grounding): `../docs/webapp/ai-layer.md`
- The data you render: `../docs/data/snapshot-contract.md`

Rules of thumb:
- Render engine output; **never invent player data**. Claude chat is grounded to the snapshot's players only.
- Match the **Squad Builder**'s quality bar (states, a11y, tokens). Keep `components/ui` primitives backward-compatible.
- `DATABASE_URL` goes in `.env`; secrets (`ANTHROPIC_API_KEY`) in `.env.local`.
- Verify: typecheck from here — `node node_modules/typescript/bin/tsc --noEmit` (full node path if not on PATH).
- Run/troubleshoot: `../docs/ops/runbook.md`.

Backlog & decisions: `../ROADMAP.md`.
