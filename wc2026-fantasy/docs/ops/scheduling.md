# Scheduled daily refresh

## What runs
**`wc-companion/scripts/daily-refresh.ps1`** at **08:00 local time**, daily:
1. `python ../wc_scout/export_snapshot.py --incremental` — re-pull WC form + fixtures + FIFA feed, re-blend projections, refresh ownership + official points + scouting bonus, detect current round.
2. `npm run db:seed` — sync the database.

Runs in ~1–2 minutes (incremental). The app auto-reloads the snapshot on next page load — no restart needed. On failure the exporter doesn't overwrite, so the last good snapshot survives.

## The Windows Task Scheduler entry
Registered as **`WC2026 Daily Refresh`**.
```powershell
# (re)create:
schtasks /Create /TN "WC2026 Daily Refresh" /TR "powershell -NoProfile -ExecutionPolicy Bypass -File \"C:\Users\Micha\FantasyInfo\World Cup 2026\wc-companion\scripts\daily-refresh.ps1\"" /SC DAILY /ST 08:00 /F

# run on demand:
schtasks /Run /TN "WC2026 Daily Refresh"
# inspect:
schtasks /Query /TN "WC2026 Daily Refresh" /FO LIST
# remove:
schtasks /Delete /TN "WC2026 Daily Refresh" /F
```

## Notes
- Runs **only while logged in** (a user task) — fine for a desktop app. For run-when-logged-off it needs admin + stored credentials.
- "08:00 local time" follows the machine's timezone (≈ 08:00 BST in summer on a UK clock).
- The FIFA feed + API responses are 12h-cached, so an 08:00 run naturally picks up the previous evening's completed matches.
- Use `--refresh` (manual) only if the static club/international windows ever need rebuilding.
