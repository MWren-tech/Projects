# Product vision

## What it is
A **premium AI fantasy-football companion** for the FIFA World Cup 2026 — it helps a manager build and run their squad with the rigour of a quant analyst and the feel of a polished sports app (think "FPL × Bloomberg terminal × AI assistant").

## Who it's for
Initially a **single user** (the owner). Designed so it can grow to multi-user later without re-architecture.

## Core jobs the product does
1. **Build & manage a squad** — visual pitch, drag-and-drop subs, validation against the real rules.
2. **Decide transfers** — marginal-gain ladder, free vs −3 hit, fixtures and form.
3. **Use boosters well** — when to play Wildcard / 12th Man / Maximum Captain / Qualification / Mystery.
4. **Analyse players** — projections, actual tournament points, ownership, differentials, fixtures.
5. **Ask the AI** — grounded answers on captaincy, transfers, differentials, risks.

## Principles
- **Trustworthy numbers first, decoration second.** Everything is grounded in the model and the official FIFA data.
- **Honesty about uncertainty** — show confidence/risk, flag approximations, never fake precision.
- **Rank-aware**, not just points-aware — differentials (low ownership) matter because they win leagues.

## Non-goals (for now)
- No real-money features. No account integration with the official FIFA game (advisory only — the user enters their own squad). No multi-tenant cloud until the concept is validated.
