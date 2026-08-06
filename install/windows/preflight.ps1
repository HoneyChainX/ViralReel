<#
.SYNOPSIS
    Read-only check that this Windows 11 PC can host the ViralReel studio.

.DESCRIPTION
    Run this FIRST, before installing anything. It changes nothing - it only
    reports whether the machine clears the bars that matter, so a problem shows
    up in thirty seconds rather than forty minutes into a vendor build.

    No Administrator rights are needed.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File install\windows\preflight.ps1
#>
# Write-Host is deliberate throughout: this script's entire purpose is a
# coloured report for a human standing at the machine, not pipeline output.
[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSAvoidUsingWriteHost', '',
    Justification = 'Interactive installer report intended for a console reader')]
[CmdletBinding()]
param(
    # Skip the vendor-tree disk bar if only the tools are being installed.
    [switch]$ToolsOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:Blocking = @()
$script:Warnings = @()

function Write-Head([string]$Text) {
    Write-Host ''
    Write-Host "== $Text" -ForegroundColor Cyan
}
function Write-Ok([string]$Text)   { Write-Host "  OK    $Text" -ForegroundColor Green }
function Write-Warn([string]$Text) { Write-Host "  WARN  $Text" -ForegroundColor Yellow; $script:Warnings += $Text }
function Write-Bad([string]$Text)  { Write-Host "  FAIL  $Text" -ForegroundColor Red;   $script:Blocking += $Text }

# Windows-only cmdlets are wrapped so this file still parses and lints on any
# platform - the CI that checks it does not run on Windows.
function Get-CimSafe([string]$ClassName) {
    try { return Get-CimInstance -ClassName $ClassName -ErrorAction Stop }
    catch { return $null }
}

Write-Host 'ViralReel - Windows 11 host preflight' -ForegroundColor White
Write-Host 'Read-only. Nothing is installed or changed.' -ForegroundColor DarkGray

# --- operating system -----------------------------------------------------

Write-Head 'Windows'
$os = Get-CimSafe 'Win32_OperatingSystem'
if ($null -eq $os) {
    Write-Bad 'not running on Windows - run this on the PC that will host the studio'
} else {
    $build = [int]$os.BuildNumber
    Write-Host "  $($os.Caption)  build $build"

    # WSL2 needs 19041+. Windows 11 is 22000+; mirrored networking wants 22621+.
    if ($build -lt 19041) {
        Write-Bad "build $build is too old for WSL2 (needs 19041+). Run Windows Update."
    } elseif ($build -lt 22000) {
        Write-Warn "build $build is Windows 10. WSL2 works, but this pack is written and tested against Windows 11."
    } else {
        Write-Ok "build $build supports WSL2"
    }

    $arch = $env:PROCESSOR_ARCHITECTURE
    if ($arch -eq 'AMD64') { Write-Ok 'x64 processor' }
    elseif ($arch -eq 'ARM64') { Write-Warn 'ARM64 - Blender/ffmpeg builds we vendor are x64; expect gaps' }
    else { Write-Warn "unrecognised architecture: $arch" }
}

# --- virtualization -------------------------------------------------------

Write-Head 'Virtualization (required by WSL2)'
$cpu = Get-CimSafe 'Win32_Processor'
if ($null -ne $cpu) {
    $c = @($cpu)[0]
    $vmx = $false
    try { $vmx = [bool]$c.VirtualizationFirmwareEnabled } catch { $vmx = $false }
    $ext = $false
    try { $ext = [bool]$c.VMMonitorModeExtensions } catch { $ext = $false }

    if ($vmx -or $ext) {
        Write-Ok 'hardware virtualization is enabled'
    } else {
        # Hyper-V being already on makes the CIM flags read false, so this is a
        # warning with a way to settle it, not a hard failure.
        Write-Warn 'firmware virtualization reported off. If WSL2 fails to start, enable Intel VT-x / AMD-V in BIOS. (If Hyper-V is already running, this flag reads false and can be ignored.)'
    }
    Write-Host "  $($c.Name)"
    Write-Host "  cores: $($c.NumberOfCores)  logical: $($c.NumberOfLogicalProcessors)"
    if ([int]$c.NumberOfLogicalProcessors -lt 4) {
        Write-Warn "$($c.NumberOfLogicalProcessors) logical processors - CPU renders will be very slow"
    }
}

# --- memory and disk ------------------------------------------------------

Write-Head 'Memory and disk'
if ($null -ne $os) {
    $ramGb = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
    Write-Host "  RAM: $ramGb GB"
    if ($ramGb -lt 8) {
        Write-Bad "$ramGb GB RAM is below the 8 GB floor for 1080p work"
    } elseif ($ramGb -lt 16) {
        Write-Warn "$ramGb GB RAM - WSL2 takes a slice of this; 16 GB+ is comfortable"
    } else {
        Write-Ok "$ramGb GB RAM"
    }
}

$sys = $env:SystemDrive
if (-not $sys) { $sys = 'C:' }
$drive = Get-PSDrive -Name $sys.TrimEnd(':') -ErrorAction SilentlyContinue
if ($null -ne $drive) {
    $freeGb = [math]::Round($drive.Free / 1GB, 1)
    Write-Host "  $sys free: $freeGb GB"
    # WSL2's virtual disk grows on demand and lives on the system drive; the
    # vendor tree alone is ~26 GB before a single frame is rendered.
    $need = if ($ToolsOnly) { 20 } else { 80 }
    if ($freeGb -lt 20) {
        Write-Bad "$freeGb GB free on $sys - not enough for WSL2 plus a working tree"
    } elseif ($freeGb -lt $need) {
        Write-Warn "$freeGb GB free on $sys - a full vendor tree plus renders wants ${need} GB"
    } else {
        Write-Ok "$freeGb GB free on $sys"
    }
}

# --- gpu ------------------------------------------------------------------

Write-Head 'GPU'
$video = Get-CimSafe 'Win32_VideoController'
if ($null -eq $video) {
    Write-Warn 'could not enumerate display adapters'
} else {
    $nvidia = @($video | Where-Object { $_.Name -match 'NVIDIA' })
    foreach ($v in @($video)) { Write-Host "  $($v.Name)  driver $($v.DriverVersion)" }
    if ($nvidia.Count -gt 0) {
        Write-Ok "NVIDIA adapter present - the GPU lane (docs/14) is reachable from WSL2"
        Write-Host '        Keep the driver current on WINDOWS; do not install a driver inside WSL.' -ForegroundColor DarkGray
    } else {
        Write-Warn 'no NVIDIA adapter - CPU-only rendering, which is supported but slow (docs/14)'
    }
}

# --- wsl ------------------------------------------------------------------

Write-Head 'WSL'
$wsl = Get-Command wsl.exe -ErrorAction SilentlyContinue
if ($null -eq $wsl) {
    Write-Warn 'wsl.exe not found - bootstrap.ps1 will install it (a reboot is required)'
} else {
    Write-Ok 'wsl.exe present'
    try {
        # WSL writes UTF-16 to the console; decode so the text is greppable.
        $prev = [Console]::OutputEncoding
        [Console]::OutputEncoding = [System.Text.Encoding]::Unicode
        $status = (& wsl.exe --status 2>&1 | Out-String)
        $listed = (& wsl.exe --list --quiet 2>&1 | Out-String)
        [Console]::OutputEncoding = $prev

        $distros = @($listed -split "`r?`n" | Where-Object { $_.Trim() -ne '' })
        if ($distros.Count -gt 0) {
            Write-Ok "installed distributions: $($distros -join ', ')"
        } else {
            Write-Warn 'WSL is present but no distribution is installed yet'
        }
        if ($status -match '2') { Write-Host '  (wsl --status reported a default version)' -ForegroundColor DarkGray }
    } catch {
        Write-Warn "could not query WSL: $($_.Exception.Message)"
    }
}

# --- tooling --------------------------------------------------------------

Write-Head 'Tooling'
foreach ($tool in @('winget', 'git', 'claude')) {
    $cmd = Get-Command $tool -ErrorAction SilentlyContinue
    if ($null -ne $cmd) { Write-Ok "$tool present" }
    elseif ($tool -eq 'claude') { Write-Warn 'claude CLI not installed - needed for Remote Control (bootstrap installs it)' }
    else { Write-Warn "$tool not found" }
}

# --- power ----------------------------------------------------------------

Write-Head 'Power (a render server must not sleep)'
try {
    $scheme = (& powercfg /getactivescheme 2>&1 | Out-String).Trim()
    Write-Host "  $scheme"
    Write-Warn 'sleep/hibernate settings are not verified here - host-config.ps1 disables them'
} catch {
    Write-Warn 'powercfg unavailable'
}

# --- verdict --------------------------------------------------------------

Write-Host ''
if ($script:Blocking.Count -eq 0) {
    Write-Host 'PREFLIGHT PASSED' -ForegroundColor Green
    Write-Host 'Next: run install\windows\bootstrap.ps1 from an Administrator PowerShell.'
} else {
    Write-Host 'PREFLIGHT FAILED' -ForegroundColor Red
    foreach ($b in $script:Blocking) { Write-Host "  - $b" -ForegroundColor Red }
}
if ($script:Warnings.Count -gt 0) {
    Write-Host ''
    Write-Host 'Warnings (not blocking):' -ForegroundColor Yellow
    foreach ($w in $script:Warnings) { Write-Host "  - $w" -ForegroundColor Yellow }
}

exit ($(if ($script:Blocking.Count -gt 0) { 1 } else { 0 }))
