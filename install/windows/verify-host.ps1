<#
.SYNOPSIS
    Prove the render host actually survived a reboot.

.DESCRIPTION
    Run this AFTER restarting Windows, without logging into the distro first.
    It answers the one question the install cannot answer for itself: did the
    machine come back on its own, with the worker running and the door open?

    docs/15-windows-host.md SS7 explains why this needs checking rather than
    assuming - starting WSL at boot with nobody logged in is the one part of
    this design Microsoft does not document a supported path for.

    Read-only. Changes nothing.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File install\windows\verify-host.ps1
#>
# Write-Host is deliberate: this is a report for a human at the console.
[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSAvoidUsingWriteHost', '',
    Justification = 'Interactive verification report intended for a console reader')]
[CmdletBinding()]
param(
    [string]$Distro = 'Ubuntu-24.04',
    [string]$TaskName = 'ViralReel WSL keepalive'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'

$script:Bad = @()
function Write-Head([string]$T) { Write-Host ''; Write-Host "== $T" -ForegroundColor Cyan }
function Ok([string]$T)   { Write-Host "  OK    $T" -ForegroundColor Green }
function Bad([string]$T)  { Write-Host "  FAIL  $T" -ForegroundColor Red; $script:Bad += $T }
function Warn([string]$T) { Write-Host "  WARN  $T" -ForegroundColor Yellow }
function Note([string]$T) { Write-Host "        $T" -ForegroundColor DarkGray }

function Get-WslOutput([string[]]$WslArgs) {
    $prev = [Console]::OutputEncoding
    try {
        [Console]::OutputEncoding = [System.Text.Encoding]::Unicode
        return (& wsl.exe @WslArgs 2>&1 | Out-String)
    } catch { return '' } finally { [Console]::OutputEncoding = $prev }
}

Write-Host 'ViralReel - host verification' -ForegroundColor White

# --- uptime -----------------------------------------------------------------
# A verification run five minutes after a manual `wsl` launch proves nothing.

Write-Head 'Since boot'
try {
    $boot = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
    $up = (Get-Date) - $boot
    Write-Host ("  booted {0:yyyy-MM-dd HH:mm}, up {1:N0}h {2:N0}m" -f $boot, $up.TotalHours, $up.Minutes)
    if ($up.TotalMinutes -lt 3) {
        Warn 'only just booted - give the boot task a minute before trusting this run'
    }
} catch { Warn 'could not read boot time' }

# --- boot task --------------------------------------------------------------

Write-Head 'Boot task'
$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($null -eq $task) {
    Warn "no scheduled task named '$TaskName'"
    Note 'WSL will only run while somebody is logged in. See docs/15 SS7.'
} else {
    Ok "task registered, state: $($task.State)"
    $info = Get-ScheduledTaskInfo -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($null -ne $info) {
        Write-Host "        last run: $($info.LastRunTime)  result: $($info.LastTaskResult)"
        if ($info.LastTaskResult -ne 0 -and $info.LastTaskResult -ne 267009) {
            # 267009 = still running, which is exactly what we want here.
            Bad "boot task last exited with $($info.LastTaskResult)"
        }
    }
}

# --- wsl --------------------------------------------------------------------

Write-Head 'WSL'
$running = Get-WslOutput @('--list', '--running', '--quiet')
$runningList = @($running -split "`r?`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' })
if ($runningList -contains $Distro) {
    Ok "$Distro is running"
} else {
    Bad "$Distro is NOT running"
    Note 'Nothing came up on its own. Either the boot task did not fire, or it fired'
    Note 'and exited. Fallback in docs/15 SS7: auto-login plus a logon task.'
}

# --- inside the distro ------------------------------------------------------

Write-Head 'Inside the distro'
$systemd = (& wsl.exe -d $Distro -- sh -c 'test -d /run/systemd/system && echo yes || echo no' 2>&1 | Out-String).Trim()
if ($systemd -match 'yes') {
    Ok 'systemd is running'
} else {
    Bad 'systemd is not running - the job worker cannot be supervised'
    Note "Set [boot] systemd=true in /etc/wsl.conf, then: wsl --shutdown"
}

foreach ($unit in @('viralreel-jobd', 'viralreel-remote-control')) {
    $state = (& wsl.exe -d $Distro -- systemctl is-active $unit 2>&1 | Out-String).Trim()
    if ($state -eq 'active') {
        Ok "$unit is active"
    } elseif ($state -match 'inactive|failed|activating') {
        Bad "$unit is $state"
        Note "journalctl -u $unit -n 40"
    } else {
        Warn "$unit not installed ($state)"
    }
}

# --- the queue answers ------------------------------------------------------

Write-Head 'Studio'
$hostReport = (& wsl.exe -d $Distro -- sh -lc 'cd ~/ViralReel 2>/dev/null && python3 scripts/studio/hostinfo.py --assert-ready >/dev/null 2>&1 && echo ready || echo notready' 2>&1 | Out-String).Trim()
if ($hostReport -match '\bready\b' -and $hostReport -notmatch 'notready') {
    Ok 'the studio reports itself ready to render'
} else {
    Warn 'the studio is not ready - run `make host` inside the distro for the reasons'
}

# --- verdict ----------------------------------------------------------------

Write-Host ''
if ($script:Bad.Count -eq 0) {
    Write-Host 'HOST VERIFIED - it came back on its own.' -ForegroundColor Green
    Write-Host 'Check claude.ai/code for the Remote Control session.' -ForegroundColor DarkGray
    exit 0
}
Write-Host 'HOST NOT VERIFIED' -ForegroundColor Red
foreach ($b in $script:Bad) { Write-Host "  - $b" -ForegroundColor Red }
exit 1
