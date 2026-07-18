# Daily WC2026 data refresh.
# Pulls the latest tournament stats from API-Football, rebuilds the app snapshot
# (projections + per-player WC points), and syncs the local database.
# Intended to run once a day (e.g. 08:00 local time) via Windows Task Scheduler.

$ErrorActionPreference = "Stop"

# wc-companion dir = parent of this script's "scripts" folder
$app = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $app

Write-Host "[$(Get-Date -Format u)] Refreshing WC2026 snapshot..."

# 1. Incremental update: re-pull only what changes mid-tournament (WC form + fixtures)
#    and re-blend projections. ~50 API calls / 1-2 min, vs hundreds for a full rebuild.
#    The static windows (club + international form) don't change during the tournament.
#    Run a full rebuild manually (export_snapshot.py --refresh) if league data ever changes.
python ..\wc_scout\export_snapshot.py --incremental
if ($LASTEXITCODE -ne 0) {
    Write-Error "[$(Get-Date -Format u)] export_snapshot.py failed (exit $LASTEXITCODE) — aborting refresh."
    exit $LASTEXITCODE
}

# 2. Keep the local database in sync (prices / player rows).
$npm = Join-Path $env:ProgramFiles "nodejs\npm.cmd"
& $npm run db:seed
if ($LASTEXITCODE -ne 0) {
    Write-Error "[$(Get-Date -Format u)] db:seed failed (exit $LASTEXITCODE)."
    exit $LASTEXITCODE
}

Write-Host "[$(Get-Date -Format u)] Refresh complete."
