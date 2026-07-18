# wc_scout — the model (Python analytics engine)

This is the **model** workspace. It computes projections and exports `../wc-companion/data/snapshot.json`.

➡️ **Work here with the `model-engineer` or `data-engineer` agent.** Open Claude Code at the repo root (`World Cup 2026/`) so agents + docs resolve.

Read before changing anything:
- Scoring rules (source of truth): `../docs/model/scoring-rules.md`
- How projections work: `../docs/model/projection-model.md`
- Data sources & endpoints: `../docs/model/data-sources.md`
- Pipeline & refresh modes: `../docs/model/pipeline.md`
- The output contract: `../docs/data/snapshot-contract.md`

Rules of thumb:
- `scoring.py` constants are the single source of truth — don't duplicate the ruleset.
- Use `export_snapshot.py --incremental` for daily-style refreshes; `--refresh` only when static (club/intl) windows must change.
- Verify: `python -m py_compile <files>` and regenerate the snapshot, spot-check known players.
- Don't break the snapshot contract without updating both sides + the contract doc.

Backlog & decisions: `../ROADMAP.md`.
