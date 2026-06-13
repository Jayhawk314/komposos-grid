# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs
#
# Daily grid refresh for the published site.
#
# Runs the keyless daily pulse and regenerates docs/ (dashboard +
# interactive network map, including the latest daily-pulse layer), then
# commits and pushes the published artifacts so GitHub Pages updates.
#
# The big EIA/eGRID source files are gitignored and live only on this
# machine, so this MUST run locally (not in CI) for the map to rebuild.
#
# Register it with scripts\register_daily_task.ps1 (Windows Task
# Scheduler). Run manually with -NoPush to rebuild without publishing.

param(
    [switch]$NoPush,
    [string]$Python = "python",
    [string]$Remote = "grid",       # komposos-grid (NOT origin / KOMPOSOS-IV)
    [string]$Branch = "master"
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

Write-Host "[$(Get-Date -Format s)] grid daily refresh in $repo"

# 1. Daily pulse + regenerate docs/ (dashboard + map with fresh daily layer).
& $Python -m domains.grid.run_daily_update
if ($LASTEXITCODE -ne 0) {
    Write-Warning "run_daily_update exited $LASTEXITCODE (pulse may be partial); docs still regenerated."
}

# 2. Publish only the generated artifacts.
$paths = @("docs", "reports/daily")
git add -- $paths
$changed = git status --porcelain -- $paths
if (-not $changed) {
    Write-Host "no published changes; nothing to commit."
    return
}

git commit -m "Daily grid refresh: $(Get-Date -Format yyyy-MM-dd) pulse + map"
if ($NoPush) {
    Write-Host "committed locally (-NoPush set); skipping push."
    return
}
# Publish to the grid site repo. Push only this branch to the named remote
# so it can never land on origin (KOMPOSOS-IV) by accident.
git push $Remote "HEAD:$Branch"
if ($LASTEXITCODE -ne 0) {
    Write-Error "git push to '$Remote' $Branch failed (exit $LASTEXITCODE); NOT published. Resolve and rerun."
    exit 1
}
Write-Host "pushed to $Remote/$Branch; GitHub Pages will update shortly."
