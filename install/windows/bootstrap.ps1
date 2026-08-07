<#
.SYNOPSIS
    Install WSL2 and prepare a Windows 11 PC to host the ViralReel studio.

.DESCRIPTION
    Runs in two phases because installing the WSL runtime needs a reboot.
    Re-run the same command after restarting and it picks up where it stopped -
    it decides which phase it is in by inspecting the machine, not by trusting a
    flag, so an interrupted run recovers on its own.

        Phase 1  WSL2 runtime + host settings  ->  REBOOT
        Phase 2  Ubuntu, .wslconfig, /etc/wsl.conf, optional boot task

    Nothing here installs the studio itself. That is install/wsl/bootstrap.sh,
    run inside Ubuntu once this finishes - see docs/15-windows-host.md SS3.3.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File install\windows\bootstrap.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File install\windows\bootstrap.ps1 -InstallBootTask
#>
# Write-Host is deliberate: this is an installer report for a human at the console.
[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSAvoidUsingWriteHost', '',
    Justification = 'Interactive installer report intended for a console reader')]
[CmdletBinding()]
param(
    [string]$Distro = 'Ubuntu-24.04',

    # The Linux account created inside the distro.
    [string]$LinuxUser = 'render',

    # Register the at-boot task that keeps WSL running with nobody logged in.
    # Read docs/15 SS7 first - this is the fragile part of the design.
    [switch]$InstallBootTask,

    # Passed through to host-config.ps1.
    [switch]$DefenderExclusions,
    [switch]$EnableSsh,

    # Stop after phase 1 even if a reboot is not strictly needed.
    [switch]$RuntimeOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

function Write-Head([string]$Text) { Write-Host ''; Write-Host "== $Text" -ForegroundColor Cyan }
function Note([string]$T) { Write-Host "  $T" }
function Did([string]$T)  { Write-Host "  OK    $T" -ForegroundColor Green }
function Warn([string]$T) { Write-Host "  WARN  $T" -ForegroundColor Yellow }
function Fail([string]$T) { Write-Host "  FAIL  $T" -ForegroundColor Red }

function Test-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    (New-Object Security.Principal.WindowsPrincipal($id)).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Admin)) {
    Fail 'Administrator PowerShell required. Right-click PowerShell > Run as administrator.'
    exit 1
}

Write-Host 'ViralReel - Windows 11 host bootstrap' -ForegroundColor White
Note "repo:   $RepoRoot"
Note "distro: $Distro"

# --- phase detection --------------------------------------------------------
# WSL prints UTF-16; without this its output is unmatchable by -match.

function Get-WslOutput([string[]]$WslArgs) {
    $prev = [Console]::OutputEncoding
    try {
        [Console]::OutputEncoding = [System.Text.Encoding]::Unicode
        return (& wsl.exe @WslArgs 2>&1 | Out-String)
    } catch {
        return ''
    } finally {
        [Console]::OutputEncoding = $prev
    }
}

$wslPresent = $null -ne (Get-Command wsl.exe -ErrorAction SilentlyContinue)
$installedDistros = @()
if ($wslPresent) {
    $listing = Get-WslOutput @('--list', '--quiet')
    $installedDistros = @($listing -split "`r?`n" |
        ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' })
}
$distroReady = $installedDistros -contains $Distro

Write-Head 'State'
Note "wsl.exe present:    $wslPresent"
Note "distros installed:  $(if ($installedDistros.Count) { $installedDistros -join ', ' } else { '(none)' })"
Note "target distro ready: $distroReady"

# --- phase 1: runtime -------------------------------------------------------

if (-not $wslPresent) {
    Write-Head 'Phase 1 - installing the WSL2 runtime'
    # --no-distribution installs only the runtime, so the cloud-init user file
    # can be staged before a distro ever launches (which is what makes the
    # account creation non-interactive).
    & wsl.exe --install --no-distribution
    if ($LASTEXITCODE -ne 0) {
        Fail "wsl --install failed with exit code $LASTEXITCODE"
        Note 'If virtualization is disabled in firmware, enable Intel VT-x / AMD-V and retry.'
        exit 1
    }
    Did 'WSL2 runtime installed'

    Write-Head 'Host settings'
    & powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'host-config.ps1') `
        @(if ($DefenderExclusions) { '-DefenderExclusions' }) `
        @(if ($EnableSsh) { '-EnableSsh' })

    Write-Host ''
    Write-Host 'REBOOT REQUIRED.' -ForegroundColor Yellow
    Write-Host 'Restart Windows, then run this exact command again to continue.' -ForegroundColor Yellow
    exit 0
}

if ($RuntimeOnly) {
    Did 'runtime present; stopping here as requested (-RuntimeOnly)'
    exit 0
}

# --- phase 2: distro --------------------------------------------------------

Write-Head 'Phase 2 - WSL update'
& wsl.exe --update 2>&1 | Out-String | Write-Host
& wsl.exe --set-default-version 2 2>&1 | Out-Null
Did 'WSL updated and default version set to 2'

if (-not $distroReady) {
    Write-Head "Staging non-interactive first boot for $Distro"
    # Ubuntu images read cloud-init from here on FIRST launch only. Writing it
    # now is what avoids the interactive "enter a new UNIX username" prompt -
    # which matters because an installer that blocks on a prompt is an installer
    # that cannot be finished from another room.
    $cloudInitDir = Join-Path $env:USERPROFILE '.cloud-init'
    New-Item -ItemType Directory -Path $cloudInitDir -Force | Out-Null
    $userData = Join-Path $cloudInitDir "$Distro.user-data"

    $wslConfContent = @"
[boot]
systemd=true

[user]
default=$LinuxUser

[automount]
enabled=true
options="metadata,umask=22,fmask=11"

[interop]
enabled=true
appendWindowsPath=false

[gpu]
enabled=true
"@

    $cloudInit = @"
#cloud-config
users:
- name: $LinuxUser
  gecos: ViralReel render agent
  groups: [adm, sudo]
  sudo: ALL=(ALL) NOPASSWD:ALL
  shell: /bin/bash
write_files:
- path: /etc/wsl.conf
  content: |
$([string]::Join("`n", ($wslConfContent -split "`r?`n" | ForEach-Object { "    $_" })))
"@
    Set-Content -Path $userData -Value $cloudInit -Encoding UTF8
    Did "wrote $userData"

    Write-Head "Installing $Distro"
    & wsl.exe --install -d $Distro --no-launch
    if ($LASTEXITCODE -ne 0) {
        Fail "wsl --install -d $Distro failed ($LASTEXITCODE)"
        Note 'List available names with: wsl --list --online'
        exit 1
    }
    & wsl.exe --set-default $Distro 2>&1 | Out-Null
    Did "$Distro installed and set as default"
} else {
    Did "$Distro already installed"
}

# --- .wslconfig -------------------------------------------------------------

Write-Head 'WSL resource limits (.wslconfig)'
$os = Get-CimInstance Win32_OperatingSystem
$totalGb = [math]::Round($os.TotalVisibleMemorySize / 1MB)
$logical = [int]$env:NUMBER_OF_PROCESSORS

# Leave Windows a real slice. This is somebody's actual PC: a render that
# starves the host makes the machine unusable for the person sitting at it, and
# the WSL defaults (half the RAM, every core) do exactly that under load.
$wslMemGb = [math]::Max(4, [math]::Floor($totalGb * 0.65))
$wslCpus  = [math]::Max(2, $logical - 2)
$swapGb   = [math]::Max(4, [math]::Floor($wslMemGb / 4))

$template = Join-Path $PSScriptRoot 'wslconfig.template'
$target = Join-Path $env:USERPROFILE '.wslconfig'
if (Test-Path $template) {
    $content = (Get-Content $template -Raw).
        Replace('__MEMORY__', "${wslMemGb}GB").
        Replace('__PROCESSORS__', "$wslCpus").
        Replace('__SWAP__', "${swapGb}GB")
    if (Test-Path $target) {
        Copy-Item $target "$target.bak" -Force
        Note "existing .wslconfig backed up to $target.bak"
    }
    Set-Content -Path $target -Value $content -Encoding ASCII
    Did "wrote $target (memory=${wslMemGb}GB processors=$wslCpus swap=${swapGb}GB of ${totalGb}GB/$logical cores)"
} else {
    Warn "template not found at $template - skipping .wslconfig"
}

# --- /etc/wsl.conf for an already-existing distro ---------------------------

if ($distroReady) {
    Write-Head 'Ensuring systemd is enabled in the distro'
    # cloud-init only applies on first boot, so a distro that already existed
    # needs this written directly. Without systemd there is no job worker.
    $script = "grep -q '^systemd=true' /etc/wsl.conf 2>/dev/null || " +
              "printf '[boot]\nsystemd=true\n' >> /etc/wsl.conf"
    & wsl.exe -d $Distro -u root -- bash -lc $script 2>&1 | Out-String | Write-Host
    Did 'systemd=true present in /etc/wsl.conf'
}

Write-Head 'Restarting WSL to apply configuration'
& wsl.exe --shutdown
Start-Sleep -Seconds 8
Did 'wsl --shutdown issued'

# Sparse disk matters more here than anywhere else: WSL's virtual disk grows on
# demand and never gives space back without it, and this box writes and deletes
# thousands of PNG frames.
& wsl.exe --manage $Distro --set-sparse true 2>&1 | Out-String | Write-Host
if ($LASTEXITCODE -eq 0) { Did 'sparse VHD enabled (freed space returns to Windows)' }
else { Warn 'could not enable sparse VHD - needs WSL 2.0.0+; check with: wsl --version' }

# --- host settings ----------------------------------------------------------

Write-Head 'Host settings'
& powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'host-config.ps1') `
    @(if ($DefenderExclusions) { '-DefenderExclusions' }) `
    @(if ($EnableSsh) { '-EnableSsh' })

# --- boot task --------------------------------------------------------------

if ($InstallBootTask) {
    Write-Head 'At-boot task (read docs/15 SS7 before relying on this)'
    Warn 'Microsoft documents no supported way to start a WSL distro at boot with'
    Warn 'nobody logged in. This task is the practical workaround, and it must be'
    Warn 'verified by actually rebooting the machine.'

    $taskName = 'ViralReel WSL keepalive'
    # A long-lived foreground process is what holds the WSL VM up; systemd
    # inside the distro does not keep the distro itself alive.
    $action = New-ScheduledTaskAction -Execute 'wsl.exe' `
        -Argument "-d $Distro -u root -e /bin/sh -c `"exec sleep infinity`""
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit ([TimeSpan]::Zero)

    Note 'The task needs the password of an account that can log on, because the'
    Note 'password-less (S4U) mode has no network access - which would leave the'
    Note 'box unable to reach claude.ai.'
    $cred = Get-Credential -Message 'Windows account to run the WSL keepalive task as'

    try {
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
            -Settings $settings -User $cred.UserName `
            -Password $cred.GetNetworkCredential().Password `
            -RunLevel Highest -Force | Out-Null
        Did "registered scheduled task '$taskName'"
        Note 'Verify by REBOOTING and then running install\windows\verify-host.ps1'
    } catch {
        Fail "could not register the task: $($_.Exception.Message)"
        Note 'Fallback: enable auto-login for this account and use a logon task instead (docs/15 SS7).'
    }
} else {
    Write-Head 'At-boot task'
    Note 'not requested (pass -InstallBootTask). Without it, WSL and therefore the'
    Note 'render worker only run while someone is logged in.'
}

# --- next steps -------------------------------------------------------------

Write-Head 'Done - the Windows side is ready'
Write-Host @"
  Next, inside Ubuntu (open it from the Start menu, or run: wsl -d $Distro):

    git clone <this repo> ~/ViralReel && cd ~/ViralReel
    bash install/wsl/bootstrap.sh --profile core --with-claude --with-services

  Keep the repo on the LINUX filesystem (~/ViralReel), never under /mnt/c.

  Then log in to Claude once, interactively - Remote Control needs a real
  claude.ai login and rejects API keys:

    cd ~/ViralReel && claude        # then /login, and accept the trust prompt

  Full guide: docs/15-windows-host.md
"@
