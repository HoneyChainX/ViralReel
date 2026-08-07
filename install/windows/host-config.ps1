<#
.SYNOPSIS
    Configure a Windows 11 desktop to behave like an always-on render host.

.DESCRIPTION
    A desktop PC is tuned to be a good desktop: it sleeps, it scans everything it
    touches, and it reboots for updates when it feels like it. Each of those is
    wrong for a machine that must finish a six-hour render while nobody is in the
    room. This script changes only those things, reports every change, and can be
    re-run safely.

    Run from an Administrator PowerShell. Use -WhatIf to see the plan first.

    Antivirus exclusions are OPT-IN (-DefenderExclusions). They speed up
    frame-heavy work substantially, but they reduce protection on somebody's
    personal computer, so this script will not do it behind their back.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File install\windows\host-config.ps1 -WhatIf

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File install\windows\host-config.ps1 -DefenderExclusions -EnableSsh
#>
# Write-Host is deliberate: this is a change report for a human at the console.
[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSAvoidUsingWriteHost', '',
    Justification = 'Interactive installer report intended for a console reader')]
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
param(
    # Exclude the WSL virtual disk and the render tree from real-time scanning.
    [switch]$DefenderExclusions,

    # Install and start the in-box OpenSSH server (pair with Tailscale, docs/15).
    [switch]$EnableSsh,

    # Turn the display off after this many minutes. 0 keeps it on.
    [int]$DisplayOffMinutes = 15
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:Changed = @()
$script:Skipped = @()

function Write-Head([string]$Text) { Write-Host ''; Write-Host "== $Text" -ForegroundColor Cyan }
function Note([string]$Text) { Write-Host "  $Text" }
function Did([string]$Text)  { Write-Host "  CHANGED $Text" -ForegroundColor Green; $script:Changed += $Text }
function Skip([string]$Text) { Write-Host "  skipped $Text" -ForegroundColor DarkGray; $script:Skipped += $Text }
function Warn([string]$Text) { Write-Host "  WARN    $Text" -ForegroundColor Yellow }

function Test-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $p = New-Object Security.Principal.WindowsPrincipal($id)
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Admin)) {
    Write-Host 'This script must run from an Administrator PowerShell.' -ForegroundColor Red
    Write-Host 'Right-click PowerShell > Run as administrator, then re-run.' -ForegroundColor Red
    exit 1
}

Write-Host 'ViralReel - Windows render host configuration' -ForegroundColor White

# --- power ------------------------------------------------------------------
# powercfg /change takes MINUTES; 0 means never. AC only: on a laptop lid we
# still want battery behaviour left alone.

Write-Head 'Power (a render must not be interrupted by sleep)'
$powerPlan = @(
    @{ Setting = 'standby-timeout-ac';   Value = 0;                  What = 'never sleep on AC' },
    @{ Setting = 'hibernate-timeout-ac'; Value = 0;                  What = 'never hibernate on AC' },
    @{ Setting = 'disk-timeout-ac';      Value = 0;                  What = 'never spin disks down on AC' },
    @{ Setting = 'monitor-timeout-ac';   Value = $DisplayOffMinutes; What = "display off after $DisplayOffMinutes min (does not affect rendering)" }
)
foreach ($p in $powerPlan) {
    if ($PSCmdlet.ShouldProcess("powercfg /change $($p.Setting) $($p.Value)", 'set power setting')) {
        & powercfg /change $p.Setting $p.Value
        if ($LASTEXITCODE -eq 0) { Did $p.What } else { Warn "powercfg failed for $($p.Setting)" }
    }
}
# Hibernation also reclaims the hiberfil.sys, which is RAM-sized disk we would
# rather keep for renders.
if ($PSCmdlet.ShouldProcess('powercfg /hibernate off', 'disable hibernation')) {
    & powercfg /hibernate off 2>$null
    if ($LASTEXITCODE -eq 0) { Did 'hibernation disabled (frees hiberfil.sys)' }
    else { Skip 'hibernation was already off or is not supported' }
}

# --- long paths -------------------------------------------------------------

Write-Head 'Long path support'
$fsKey = 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem'
$current = (Get-ItemProperty -Path $fsKey -Name LongPathsEnabled -ErrorAction SilentlyContinue).LongPathsEnabled
if ($current -eq 1) {
    Skip 'LongPathsEnabled already 1'
} elseif ($PSCmdlet.ShouldProcess($fsKey, 'set LongPathsEnabled=1')) {
    # node_modules and frame sequences blow past MAX_PATH routinely; without
    # this, npm installs and render trees fail with errors that blame the wrong
    # thing entirely.
    New-ItemProperty -Path $fsKey -Name LongPathsEnabled -Value 1 -PropertyType DWORD -Force | Out-Null
    Did 'LongPathsEnabled=1 (takes effect after reboot)'
}

# --- defender ---------------------------------------------------------------

Write-Head 'Microsoft Defender'
if (-not $DefenderExclusions) {
    Skip 'antivirus exclusions not requested (pass -DefenderExclusions)'
    Note 'Real-time scanning of thousands of PNG frames is a measurable tax on render time.'
} else {
    $paths = @()
    # The WSL disk: one file, constantly written, already inside a VM boundary.
    $lxss = Join-Path $env:LOCALAPPDATA 'Packages'
    if (Test-Path $lxss) { $paths += $lxss }
    $repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    if (Test-Path $repo) { $paths += $repo }

    foreach ($path in $paths) {
        if ($PSCmdlet.ShouldProcess($path, 'add Defender exclusion')) {
            try {
                Add-MpPreference -ExclusionPath $path -ErrorAction Stop
                Did "Defender exclusion: $path"
            } catch {
                Warn "could not add exclusion for ${path}: $($_.Exception.Message)"
            }
        }
    }
    Note 'Review later with: Get-MpPreference | Select-Object -ExpandProperty ExclusionPath'
}

# --- windows update ---------------------------------------------------------

Write-Head 'Windows Update restarts'
# There is no supported command-line switch for active hours on Home editions,
# so this is guidance rather than an automated change - claiming otherwise would
# be worse than saying it plainly.
Note 'Set Settings > Windows Update > Advanced options > Active hours to cover'
Note 'the times renders run, so an automatic restart cannot land mid-job.'
Note 'A render killed by a reboot is resumable (chunked), but the queue will'
Note 'show it as interrupted and it must be re-queued.'
Skip 'active hours (no supported CLI on all editions - set it in Settings)'

# --- openssh ----------------------------------------------------------------

if ($EnableSsh) {
    Write-Head 'OpenSSH server'
    try {
        $cap = Get-WindowsCapability -Online -Name 'OpenSSH.Server*' -ErrorAction Stop |
               Select-Object -First 1
        if ($cap.State -ne 'Installed') {
            if ($PSCmdlet.ShouldProcess($cap.Name, 'install OpenSSH server')) {
                Add-WindowsCapability -Online -Name $cap.Name | Out-Null
                Did "installed $($cap.Name)"
            }
        } else {
            Skip 'OpenSSH server already installed'
        }
        if ($PSCmdlet.ShouldProcess('sshd', 'enable and start')) {
            Set-Service -Name sshd -StartupType Automatic
            Start-Service sshd
            Did 'sshd running and set to start automatically'
        }
        Note 'Reach it over Tailscale rather than opening a port to the internet (docs/15 SS6.3).'
    } catch {
        Warn "OpenSSH setup failed: $($_.Exception.Message)"
    }
} else {
    Write-Head 'OpenSSH server'
    Skip 'not requested (pass -EnableSsh)'
}

# --- summary ----------------------------------------------------------------

Write-Head 'Summary'
if ($script:Changed.Count -eq 0) {
    Write-Host '  nothing changed - the host was already configured' -ForegroundColor Green
} else {
    foreach ($c in $script:Changed) { Write-Host "  + $c" -ForegroundColor Green }
}
Write-Host ''
Write-Host 'Verify current power settings with: powercfg /query SCHEME_CURRENT SUB_SLEEP' -ForegroundColor DarkGray
