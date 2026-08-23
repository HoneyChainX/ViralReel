<#
.SYNOPSIS
    One-line entry point: download the studio onto a Windows 11 PC and check it.

.DESCRIPTION
    This is the "download link". There is no installer .exe - the studio is a
    codebase plus a large toolchain, not a packaged app - so this script fetches
    the repository, unpacks it, and runs the read-only preflight so you know in
    thirty seconds whether the machine can host it.

    It installs NOTHING except the files. The actual install is bootstrap.ps1,
    which this script prints as the next step rather than running for you.

    Paste into PowerShell (Run as administrator):

        irm https://raw.githubusercontent.com/HoneyChainX/ViralReel/main/install/windows/get.ps1 | iex

    Settings come from environment variables, because a script piped into iex
    cannot take parameters:

        $env:VIRALREEL_DIR = 'D:\ViralReel'    # where to put it (default C:\ViralReel)
        $env:VIRALREEL_REF = 'main'            # branch or tag to download
#>
# Write-Host is deliberate: this is a console report for a person at the machine.
[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSAvoidUsingWriteHost', '',
    Justification = 'Interactive installer report intended for a console reader')]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Repo    = 'HoneyChainX/ViralReel'
$Ref     = if ($env:VIRALREEL_REF) { $env:VIRALREEL_REF } else { 'main' }
$Target  = if ($env:VIRALREEL_DIR) { $env:VIRALREEL_DIR } else { 'C:\ViralReel' }
# Longest path inside the repository archive, measured by CI so this number
# cannot drift silently. Used to warn before Windows' 260-character limit.
$LongestPathInArchive = 173

function Say([string]$T)  { Write-Host $T }
function Head([string]$T) { Write-Host ''; Write-Host "== $T" -ForegroundColor Cyan }
function Ok([string]$T)   { Write-Host "  OK    $T" -ForegroundColor Green }
function Warn([string]$T) { Write-Host "  WARN  $T" -ForegroundColor Yellow }
function Bad([string]$T)  { Write-Host "  FAIL  $T" -ForegroundColor Red }

Write-Host ''
Write-Host 'ViralReel - studio downloader' -ForegroundColor White
Say "  repository : $Repo ($Ref)"
Say "  destination: $Target"
Say ''
Say '  This downloads files and checks the machine. It installs nothing yet.'

# --- sanity ------------------------------------------------------------------

Head 'Checking Windows'
# Windows PowerShell 5.1 - still what `powershell.exe` is on Windows 11 - has no
# $IsWindows; that variable arrived in PowerShell 6. Set-StrictMode above turns
# reading an unset variable into a terminating error, so the name is never
# written directly: Get-Variable asks the question instead, and its finding
# nothing on 5.1 is itself proof this is Windows.
if ($PSVersionTable.PSVersion.Major -lt 6) {
    $onWindows = $true          # Windows PowerShell only ever ran on Windows.
} else {
    $onWindows = [bool](Get-Variable -Name IsWindows -ValueOnly -ErrorAction SilentlyContinue)
}
if (-not $onWindows) {
    Bad 'this is the Windows half of the install - run it on the PC that will host the studio'
    exit 1
}
$build = 0
try {
    $build = [int](Get-CimInstance Win32_OperatingSystem).BuildNumber
} catch {
    # Not fatal: preflight reports the build properly a moment later, and
    # refusing to download because WMI was grumpy would help nobody.
    Warn "could not read the Windows build number ($($_.Exception.Message))"
}
if ($build -and $build -lt 19041) {
    Bad "Windows build $build is too old for WSL2 (needs 19041+). Run Windows Update first."
    exit 1
}
Ok "Windows build $build"

# --- download ----------------------------------------------------------------

Head 'Downloading'
if (Test-Path $Target) {
    $existing = Get-ChildItem -Path $Target -Force -ErrorAction SilentlyContinue
    if ($existing) {
        Warn "$Target already exists and is not empty."
        Say  '        Delete it, or set $env:VIRALREEL_DIR to somewhere else, and re-run.'
        Say  '        (If the studio is already there, skip straight to bootstrap.ps1.)'
        exit 1
    }
}

$zipUrl = "https://codeload.github.com/$Repo/zip/refs/heads/$Ref"
$tmpZip = Join-Path $env:TEMP "viralreel-$([System.IO.Path]::GetRandomFileName()).zip"
$tmpDir = Join-Path $env:TEMP "viralreel-x-$([System.IO.Path]::GetRandomFileName())"

Say "  fetching $zipUrl"
try {
    # ~630 MB of repository. Progress rendering makes this several times slower
    # in PowerShell, so it is disabled for the transfer and restored after.
    $prevProgress = $ProgressPreference
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $zipUrl -OutFile $tmpZip -UseBasicParsing
    $ProgressPreference = $prevProgress
} catch {
    Bad "download failed: $($_.Exception.Message)"
    Say  "        Check the branch name. Tags and branches both work:"
    Say  "          `$env:VIRALREEL_REF = 'main'; irm .../get.ps1 | iex"
    exit 1
}
$sizeMb = [math]::Round((Get-Item $tmpZip).Length / 1MB, 1)
Ok "downloaded $sizeMb MB"

Head 'Unpacking'
# The archive contains paths ~230 characters long. Windows' MAX_PATH is 260 and
# Windows PowerShell 5.1's Expand-Archive cannot go past it, so extracting into
# %TEMP% under the archive's own wrapper folder overflowed before anything
# reached the destination: it died part-way through .agents\ and then its own
# rollback failed on the folder it had not finished creating.
#
# tar.exe - bsdtar, shipped in Windows since build 17063, well below the 19041
# this installer requires - has no such limit, and --strip-components=1 drops
# the wrapper folder so files land at their final depth in a single pass with
# no temp copy at all. Expand-Archive stays as a fallback.
$slack = 260 - $LongestPathInArchive
if ($Target.Length -gt $slack) {
    Warn "$Target is deep; some files inside the studio may pass the 260-character Windows path limit"
    Say  "        A short destination such as C:\ViralReel or G:\ViralReel avoids this."
}

New-Item -ItemType Directory -Path $Target -Force | Out-Null
$unpacked = $false
$tar = Get-Command tar.exe -ErrorAction SilentlyContinue
if ($tar) {
    & $tar.Source -xf $tmpZip -C $Target --strip-components=1
    if ($LASTEXITCODE -eq 0) { $unpacked = $true; Ok "unpacked to $Target" }
    else { Warn "tar could not unpack it (exit $LASTEXITCODE); falling back to Expand-Archive" }
} else {
    Warn 'tar.exe not found; falling back to Expand-Archive (may hit the 260-character path limit)'
}

if (-not $unpacked) {
    Expand-Archive -Path $tmpZip -DestinationPath $tmpDir -Force
    # GitHub wraps the tree in <repo>-<ref-with-slashes-as-dashes>; take whatever
    # single directory came out rather than guessing its name.
    $inner = Get-ChildItem -Path $tmpDir -Directory | Select-Object -First 1
    if (-not $inner) { Bad 'the archive did not contain a directory'; exit 1 }
    Move-Item -Path (Join-Path $inner.FullName '*') -Destination $Target -Force
    Ok "unpacked to $Target"
}
Remove-Item $tmpZip, $tmpDir -Recurse -Force -ErrorAction SilentlyContinue

if (-not (Test-Path (Join-Path $Target 'install\windows\bootstrap.ps1'))) {
    Bad "this copy has no install\windows\bootstrap.ps1 - the '$Ref' branch predates the installer."
    Say  "        Try a branch that has it:  `$env:VIRALREEL_REF = 'main'"
    exit 1
}

# --- preflight ---------------------------------------------------------------

Head 'Running the preflight check (read-only)'
Push-Location $Target
try {
    & powershell -ExecutionPolicy Bypass -File 'install\windows\preflight.ps1'
    $preflight = $LASTEXITCODE
} finally {
    Pop-Location
}

# --- what happens next -------------------------------------------------------

Write-Host ''
if ($preflight -ne 0) {
    Write-Host 'The machine did not pass preflight.' -ForegroundColor Red
    Write-Host 'Fix the FAIL lines above, then run the preflight again:' -ForegroundColor Red
    Write-Host "    cd $Target"
    Write-Host '    powershell -ExecutionPolicy Bypass -File install\windows\preflight.ps1'
    exit 1
}

Write-Host 'Downloaded and the machine looks capable.' -ForegroundColor Green
Write-Host @"

  NEXT - the actual install, in two halves. Budget an hour or two, mostly
  unattended, with one reboot in the middle.

  1. Windows half (this window, as administrator):

       cd $Target
       powershell -ExecutionPolicy Bypass -File install\windows\bootstrap.ps1

     It installs WSL2 and Ubuntu and configures the PC to stay awake. It will
     tell you to REBOOT, after which you run the exact same command again and
     it carries on from where it stopped.

  2. Linux half (open 'Ubuntu' from the Start menu afterwards):

       git clone https://github.com/$Repo.git ~/ViralReel
       cd ~/ViralReel
       bash install/wsl/bootstrap.sh --profile core --with-claude --with-services

     Yes, a second copy: the studio runs from inside Ubuntu, on the Linux
     filesystem, because that is where it is fast and where permissions work.
     The Windows copy exists only to carry these installers.

  Full guide, including how to drive it from your laptop:
      $Target\docs\15-windows-host.md
"@
