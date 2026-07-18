# Runbook — run, build, troubleshoot

## Prerequisites
- **Node.js 18+** (installed). If `npm` is blocked by PowerShell policy: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.
- **Python** with the `wc_scout` engine working; `wc_scout/.env` has `API_FOOTBALL_KEY`.
- Optional **`ANTHROPIC_API_KEY`** in `wc-companion/.env.local` for AI chat (pay-as-you-go).

## First-time setup (web app)
```powershell
cd wc-companion
npm install
Copy-Item .env.example .env            # Prisma + seed read .env (not .env.local)
npm run db:push                         # create the local SQLite db
npm run db:seed                         # seed from the bundled data/snapshot.json
# npm run snapshot                       # optional: regenerate snapshot (needs API_FOOTBALL_KEY)
```

## Run the app
```powershell
cd "World Cup 2026/wc-companion"
npm run dev      # http://localhost:3000  (leave running; Ctrl+C stops it)
```

## Refresh data manually
```powershell
# fast display-only refresh:
npm run snapshot
# full projection re-blend (what the daily task does):
python ../wc_scout/export_snapshot.py --incremental
npm run db:seed
```
The app auto-reloads the snapshot on file change — no restart needed.

## Verify a change
- Python: `python -m py_compile <files>` (in `wc_scout/`).
- App typecheck (in `wc-companion/`): `node node_modules/typescript/bin/tsc --noEmit` — use the full path if Node isn't on PATH: `"C:\Program Files\nodejs\node.exe" node_modules\typescript\bin\tsc --noEmit`.

## Troubleshooting
| Symptom | Cause / fix |
|---|---|
| `npm` "running scripts is disabled" | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Prisma "Environment variable not found: DATABASE_URL" | `DATABASE_URL` must be in `.env` (not only `.env.local`). Seed runs via `tsx prisma/seed.ts`, which self-loads `.env`. |
| Player profile 404 | id slug must be ASCII (accents normalised) — re-run the exporter. |
| Spinning page on first load | Next compiles routes on first hit (10–30s). Check the `npm run dev` terminal for errors. |
| Snapshot stale | re-run the exporter; the loader picks up the new mtime. |
| Engine run very slow (61s pauses) | per-minute API limit on a big burst — use `--incremental`, not `--refresh`. |

## Deploy (future, optional)
Local-only today. To host: Vercel (app) + a Python host/cron (exporter) writing the snapshot to storage + Postgres/Supabase (DB). See [webapp/architecture.md](../webapp/architecture.md).
