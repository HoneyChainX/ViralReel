# Installing ViralReel on a Windows 11 PC

Start here. `docs/15-windows-host.md` is the engineering guide; this page is the
short version for the person standing at the machine.

---

## First, what this is — and is not

**There is no `.exe`, and no portable folder like ComfyUI's.** ViralReel is not
one app. It is a studio: a codebase plus a toolchain of render engines, Python
environments and Node packages that together come to roughly 26 GB once
installed. Nobody has packaged that into a double-click installer, and pretending
otherwise would mean shipping something that breaks on the first machine that is
slightly different.

What you get instead is **two scripts that do the work for you**. You paste one
line, answer nothing, reboot once, and paste one more. That is the whole install.

It also does not put an icon on the desktop, because there is no window to open.
The studio has no GUI: you drive it from Claude, from anywhere — that is the
entire point of it living on this machine.

---

## What the PC needs

| | Minimum | Comfortable |
|---|---|---|
| Windows | 10 build 19041 | Windows 11 |
| RAM | 8 GB | 16 GB or more |
| Free disk | 20 GB | 80 GB or more |
| CPU | 4 cores | 8+ cores |
| Graphics card | none needed | any NVIDIA card makes rendering much faster |

Virtualization must be enabled in the BIOS. It usually already is; the check
below tells you if it is not.

---

## Step 1 — download and check (2 minutes)

On the PC, click Start, type **PowerShell**, right-click it and choose
**Run as administrator**. Paste this and press Enter:

```powershell
irm https://raw.githubusercontent.com/HoneyChainX/ViralReel/main/install/windows/get.ps1 | iex
```

This downloads the studio to `C:\ViralReel` and runs a read-only check of the
machine. It installs nothing yet. If the check says **PREFLIGHT FAILED**, fix
what it names and run it again — better to find out now than forty minutes in.

To put it somewhere else, set that first:

```powershell
$env:VIRALREEL_DIR = 'D:\ViralReel'
irm https://raw.githubusercontent.com/HoneyChainX/ViralReel/main/install/windows/get.ps1 | iex
```

---

## Step 2 — the Windows half (~15 minutes, then a reboot)

In the same administrator PowerShell:

```powershell
cd C:\ViralReel
powershell -ExecutionPolicy Bypass -File install\windows\bootstrap.ps1
```

It installs WSL2 and Ubuntu, sizes them to this machine, and stops the PC from
falling asleep mid-render. It will tell you to **reboot**. After the reboot, open
PowerShell as administrator again and run **the same two lines** — it picks up
where it left off.

---

## Step 3 — the Linux half (30–90 minutes, mostly unattended)

Open **Ubuntu** from the Start menu. Then:

```bash
git clone https://github.com/HoneyChainX/ViralReel.git ~/ViralReel
cd ~/ViralReel
bash install/wsl/bootstrap.sh --profile core --with-claude --with-services
```

Yes, this is a second copy, and that is deliberate: the studio *runs* from inside
Ubuntu, on the Linux filesystem, where it is many times faster and where file
permissions work properly. The Windows copy exists only to carry the installers.

This is the long step. It downloads the render engines. Leave it running.

When it finishes, check the machine:

```bash
make host
```

---

## Step 4 — connect it to Claude

Two ways in. They do different jobs, and you can have both.

### A. Full sessions at claude.ai/code

```bash
cd ~/ViralReel
claude
```

Type `/login`, sign in to your Claude account, accept the trust prompt. Then:

```bash
sudo systemctl start viralreel-remote-control
```

Now open **claude.ai/code** on your laptop. The PC appears in the sidebar with a
green dot. You get a full Claude Code session running on that machine — this is
what you want for real work: writing scenes, fixing renders, editing files.

### B. The studio's tools inside claude.ai chat and the phone app

```bash
server/.venv/bin/python server/studio_auth.py set-passphrase
bash install/tunnel/expose.sh --tailscale
make connector URL=https://<the-address-it-printed>
```

Then in Claude: **Settings > Connectors > Add custom connector**, and paste
`https://<that-address>/mcp`. Claude sends you to a page on your own machine
asking for the passphrase you just set. Type it once.

Now you can ask Claude "is the render finished?" from your phone, without opening
a session at all.

*(The `--tailscale` step needs Tailscale installed and signed in on the PC —
it is free, and it is what gives the machine a public address without opening
anything on the router.)*

---

## Using it

Renders take hours, so nothing runs "live". You queue work and it keeps going
whether or not anyone is connected — that is why the PC can be closed, your
laptop can sleep, and the render still finishes.

```bash
make host                                  # is the machine healthy?
make job JOB=film-render P=film=keeper     # queue a render, returns instantly
make jobs                                  # what is running
make logs ID=12                            # watch it
```

Finished films land in `releases/` and are shared as a GitHub link, exactly as
WILD, LIGHTHOUSE and THE KEEPER were.

---

## Two honest warnings

**The repository is public.** Anyone can read it. Nothing secret is in it and CI
blocks credentials from being committed, but do not put private material there.

**One part can fail quietly.** Microsoft provides no supported way to start WSL
automatically when nobody is logged in to the PC. We use a workaround, and it
needs proving on the actual machine. After everything is installed, **reboot the
PC and run this without logging into Ubuntu first**:

```powershell
powershell -ExecutionPolicy Bypass -File C:\ViralReel\install\windows\verify-host.ps1
```

If it says HOST VERIFIED, the machine comes back on its own after a power cut.
If not, `docs/15-windows-host.md` §7 has the fallback.

---

## If something goes wrong

| What you see | What to do |
|---|---|
| PREFLIGHT FAILED | fix what it names; usually disk space or virtualization in BIOS |
| WSL2 will not start | enable Intel VT-x / AMD-V in the BIOS |
| Ubuntu install stalls | it is downloading engines; give it time, then re-run the same command |
| Everything is slow | the repo must be in `~/ViralReel`, never under `/mnt/c` |
| No session at claude.ai/code | `systemctl status viralreel-remote-control` |
| Job queued but never runs | `systemctl status viralreel-jobd` |

Re-running any installer is safe. They all check what is already done and skip it.
