# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs
#
# Register (or remove) a Windows Task Scheduler job that runs the grid
# daily refresh every morning. Local-only by necessity: the EIA/eGRID
# source files are gitignored and present only on this machine.
#
#   powershell -ExecutionPolicy Bypass -File scripts\register_daily_task.ps1
#   powershell -File scripts\register_daily_task.ps1 -At 06:30
#   powershell -File scripts\register_daily_task.ps1 -Remove

param(
    [string]$At = "07:00",
    [string]$TaskName = "KompososGridDailyRefresh",
    [switch]$Remove
)

$ErrorActionPreference = "Stop"

if ($Remove) {
    schtasks /delete /tn $TaskName /f
    Write-Host "removed scheduled task '$TaskName'."
    return
}

$script = Join-Path $PSScriptRoot "daily_refresh.ps1"
$action = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$script`""

# /sc DAILY at $At; runs as the current user so it uses your git credentials.
schtasks /create /tn $TaskName /tr $action /sc DAILY /st $At /f
Write-Host "registered '$TaskName' to run daily at $At."
Write-Host "It runs daily_refresh.ps1 (pulse -> rebuild docs/ -> commit & push)."
Write-Host "Test now:  powershell -File scripts\daily_refresh.ps1 -NoPush"
Write-Host "Remove:    powershell -File scripts\register_daily_task.ps1 -Remove"
