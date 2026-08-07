# 15 — The Windows 11 host: installing the studio on a PC and driving it remotely

Everything before this document assumed the studio ran wherever you happened to
be sitting. This one puts it on a specific machine — a Windows 11 PC that is not
yours, in a room you are not in — and gives you a way to work it from a laptop
through claude.ai.

Read §1 before installing anything. The shape of the answer is not obvious, and
one part of it (§7) is genuinely fragile.

---

## 1. The shape of the answer

Three facts decide the whole design. All three were verified at source.

**You cannot register your own machine with claude.ai/code.** Every Claude Code
on the web session runs on an Anthropic-managed Ubuntu VM; environments are
configuration objects, not machine registrations, and there is no self-hosted
runner. What *does* exist, and is exactly the capability wanted here, is
**Remote Control**: you run `claude remote-control` on the PC, and the session
appears at claude.ai/code and in the mobile app while executing on that PC's
filesystem. It makes outbound HTTPS requests only and never opens an inbound
port — no router config, no public hostname, nothing exposed.

**The studio stack is POSIX.** Bash scripts, systemd units, Linux venvs, a
26 GB vendor tree of Linux builds. Porting it to native Windows would be a
rewrite with a large regression surface and no benefit, and native Windows also
cannot run Claude Code's sandboxed Bash tool. So the studio lives in **WSL2**,
which additionally gives the GPU lane (docs/14) a working CUDA path with a
Windows-side driver.

**Nothing remote may hold a render open.** This is the constraint that shapes
the code, and it arrives from three independent directions:

| Boundary | Limit | Source |
|---|---|---|
| Remote Control session offline | ends after ~10 min, process exits | Claude Code docs |
| claude.ai tool call | 300 s, ~150k character result | Anthropic connector docs |
| Cloudflare tunnel proxy read | 125 s, then HTTP 524 | Cloudflare docs |

A twelve-hour Cycles render fits inside none of them. So the studio does not run
work on request — it **queues** it:

```
   your laptop  ──►  claude.ai/code  ──►  Remote Control session (on the PC)
                                                 │
                                                 │ enqueue, poll  (MCP tools)
                                                 ▼
                                          jobd  ──►  systemd worker  ──►  render
                                          (SQLite queue; survives everything above)
```

The session is a steering wheel. The queue is the engine, and it keeps turning
when the steering wheel disconnects.

---

## 2. What the PC needs

Run the read-only preflight first — it changes nothing and takes seconds:

```powershell
powershell -ExecutionPolicy Bypass -File install\windows\preflight.ps1
```

| | Floor | Comfortable |
|---|---|---|
| Windows | 10 build 19041 (WSL2) | Windows 11 22H2+ (mirrored networking) |
| RAM | 8 GB | 16–32 GB (WSL2 takes a slice) |
| Free disk | 20 GB (tools only) | 80 GB+ (vendor tree is ~26 GB before a single frame) |
| CPU | 4 logical cores | 8+; CPU Cycles is the slow path |
| GPU | none needed | any NVIDIA — unlocks docs/14 |

Hardware virtualization must be on in firmware, or WSL2 will not start.

Two dependencies are worth knowing before you start, because both fail quietly
rather than loudly:

- **CPython 3.11.** `bpy` publishes cp311 wheels and nothing else. Ubuntu 24.04
  ships 3.12, so on a stock host `pip install bpy` fails and the whole 3D lane
  goes with it. The bootstrap installs 3.11 explicitly and exports
  `VIRALREEL_PY311`; `make host` warns if it is absent.
- **Liberation fonts.** Every composition here asks for Liberation Sans. A host
  with only DejaVu does not error — it substitutes, and the render comes out in
  different metrics. That is the exact failure DECISIONS D3 exists to prevent,
  so the bootstrap installs `fonts-liberation` and verifies with `fc-list`.

One more on disk: a CPU-only host does not need CUDA wheels, but pip drags them
in anyway. On this repo that was measured at 8.7 GB — `whisperx` had re-resolved
to a CUDA torch despite the CPU-index pre-step, and `argos-translate` carried
3.4 GB of cuda-toolkit reached through a dependency torch never touches. The
bootstrap runs `scripts/studio/prune-cuda.sh --all` afterwards, which swaps the
torch build, uninstalls the wheels, sweeps the ~400 MB of orphaned files pip
leaves behind, and re-imports each module to prove the prune was safe. It does
nothing at all on a GPU host.

---

## 3. Install

### 3.1 Windows side (Administrator PowerShell, once)

```powershell
cd <repo>
powershell -ExecutionPolicy Bypass -File install\windows\preflight.ps1
powershell -ExecutionPolicy Bypass -File install\windows\bootstrap.ps1
```

It installs WSL2 and Ubuntu, writes `%UserProfile%\.wslconfig` with limits
computed from this machine, applies the always-on host settings (§3.2), and
registers the boot task (§7). **A reboot is required** partway through; re-run
the same command afterwards and it picks up where it stopped.

### 3.2 Host settings the bootstrap applies

A desktop PC is configured to be a good desktop, which is the opposite of a good
server. `install\windows\host-config.ps1` runs standalone too:

- sleep, hibernate and disk timeout disabled while on AC power
- Defender exclusions for the WSL disk and the render tree (real-time scanning
  of a thousand PNG frames is a measurable tax)
- long-path support enabled — `node_modules` and frame sequences exceed 260
  characters routinely
- Windows Update active hours widened so a restart does not land mid-render
- OpenSSH Server enabled (optional, for §6.3)

### 3.3 Linux side (inside Ubuntu)

```bash
git clone <this repo> ~/ViralReel && cd ~/ViralReel
bash install/wsl/bootstrap.sh --profile core --with-claude --with-services
```

Keep the repo on the **Linux** filesystem (`~/ViralReel`), never under `/mnt/c`.
The bootstrap refuses the latter: the 9p mount is dramatically slower and does
not preserve the file modes that venvs and git depend on.

Flags: `--profile none` for tools only, `--profile all` for every vendor
(hours, ~26 GB), `--with-claude` to install the Claude Code CLI,
`--with-services` to install the systemd units.

### 3.4 Log in once, interactively

Remote Control needs a real claude.ai login and **rejects API keys**. This is
the one step that cannot be scripted:

```bash
cd ~/ViralReel && claude      # then: /login, and accept the trust prompt
sudo systemctl start viralreel-remote-control
```

If `ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL`, `DISABLE_TELEMETRY` or
`DO_NOT_TRACK` are set in the shell, Remote Control will refuse to start. The
systemd unit clears all of them, so a stray line in a shell profile cannot break
the box while nobody is watching.

### 3.5 Confirm

```bash
make host          # host profile and a go/no-go verdict
make job JOB=doctor
make jobs
```

---

## 4. Operating it

Long work goes through the queue. This is not a style preference — a render
started with `&` dies with the session that started it.

```bash
make host                                  # is the machine healthy?
make job JOB=film-render P=film=keeper     # queue a render, returns immediately
make jobs                                  # what is running or waiting
make logs ID=12 TAIL=100                   # watch it
python3 scripts/studio/jobd.py cancel 12   # stop it
python3 scripts/studio/jobd.py recipes     # everything that can be run
```

Or, from a Claude session on the box (including a Remote Control one), the same
capabilities are MCP tools — `studio_status`, `enqueue`, `job_status`,
`job_logs`, `list_films`, `list_releases`, `cancel_job` — wired in by the
repo's `.mcp.json`.

**Delivery is unchanged.** A finished film is committed to `releases/` and
shared as a GitHub raw URL, exactly as WILD, LIGHTHOUSE and THE KEEPER were.
Do not serve video through a tunnel: Cloudflare's service-specific terms
reserve the right to limit accounts serving video or a disproportionate share
of large files on the free CDN, and that applies to a free zone with a named
tunnel as much as to a quick tunnel.

---

## 5. What runs, and what cannot

`config/jobs.yaml` is the **entire** list of things this machine will do on
request. It is the security boundary, not a convenience index.

A caller never sends a command. It names a recipe and fills the parameter slots
that recipe declares; each slot is checked against its own regex, and the result
is executed as an argv list with **no shell**. `argv[0]` must be a literal, so
the command itself can never come from a parameter. `tests/test_jobd.py` asserts
these properties against the shipped file, including that every declared pattern
rejects traversal and injection strings — widening a regex for convenience fails
CI rather than opening a shell to the internet.

No recipe pushes, publishes or uploads. Distribution stays manual-first
(DECISIONS D1) and remote operation does not change that.

---

## 6. Reaching it from your laptop

### 6.1 Remote Control — the way in (recommended)

On the PC (the systemd unit does this for you):

```bash
claude remote-control --name "renderbox" --spawn worktree --capacity 8
```

Then open **claude.ai/code** on your laptop or phone; the session appears in the
sidebar with a computer icon and a green dot. You get a full Claude Code session
executing on that PC.

Two things to know. The session ends after roughly ten minutes offline and the
process exits — which is why the unit sets `Restart=always`, and why real work
belongs in the queue. And a few commands are terminal-only from the browser
(`/plugin`, `/resume`); `/model`, `/effort` and friends need their value as an
argument.

### 6.2 A custom connector in claude.ai chat — possible, but gated

You may want the studio tools in ordinary claude.ai chat, without a Claude Code
session. It is a real feature, but the auth requirement is the catch: Claude
supports OAuth (DCR or CIMD) or an entirely authless server, while a plain
bearer token is a beta you must be granted. Authless is not an option — anyone
who learned the URL could queue jobs on someone else's PC.

So this path costs you an OAuth 2.1 authorization server in front of the
endpoint. We have **not** built one. If you want it later, the pieces are: a
public HTTPS endpoint (Cloudflare Tunnel with a domain, or Tailscale Funnel on
port 443), Streamable HTTP at `/mcp`, protected-resource metadata per RFC 9728,
and PKCE S256 with `https://claude.ai/api/mcp/auth_callback` as the redirect.
Cloudflare Access's Managed OAuth can supply the authorization server.

Until then, Remote Control gives you strictly more capability with strictly less
attack surface, because it opens nothing.

### 6.3 A terminal, when you need one

Tailscale plus the in-box OpenSSH server. Note that **Tailscale SSH does not
support Windows hosts** — its server component is Linux/macOS only, so use
Windows OpenSSH over the tailnet:

```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Get-Service sshd | Set-Service -StartupType Automatic
Start-Service sshd
tailscale up --unattended     # without this the PC drops off the tailnet after every reboot
```

Then from your laptop: `ssh user@renderbox.<tailnet>.ts.net`, and
`wsl` to drop into the distro. Also disable key expiry on that node in the
Tailscale admin console, or it silently deauthenticates in ~180 days.

---

## 7. The fragile part, stated plainly

**Microsoft documents no supported way to start a WSL distro at Windows boot
without a logged-in user.** Distros are registered per Windows user, WSL
instances are terminated at logoff, and the docs still carry a known issue about
session-zero launches. systemd inside the distro does not keep the distro alive.

The mechanism matters for understanding the fix. Microsoft documents that the
WSL utility VM shuts down once no WSL processes remain — release notes put it at
about 15 seconds after the last one exits — and states plainly that "systemd
services will NOT keep your WSL instance alive." So the distro needs something
holding a handle open from the Windows side; systemd inside it cannot do that
for itself.

What the bootstrap does about it: registers a Task Scheduler `ONSTART` task,
configured to run whether the user is logged on or not, whose action is a
long-lived `sleep infinity` inside WSL — that process is the handle. It also
sets `vmIdleTimeout=-1` in `.wslconfig` so the VM is not reaped between renders.
The task uses a stored password rather than the password-less (S4U) mode,
because S4U tasks get no network access, which would leave the box unable to
reach claude.ai at all.

That combination is not documented by Microsoft for this purpose. **Verify it on
the actual machine** — reboot the PC, wait, and check from your laptop that the
Remote Control session comes back and `make jobs` answers. If it does not, the
reliable fallback is to enable auto-login for the render account and use a LOGON
task instead of ONSTART, accepting that an auto-login console is a physical
security tradeoff on a machine in somebody's home.

Treat this as the load-bearing risk of the whole design. Everything else here
either works or fails loudly; this one can fail quietly, three days later.

---

## 7a. Three limits you cannot configure away

**Windows 11 Home has no RDP host.** That is an edition capability, not a
setting. WSL2, CUDA-on-WSL and everything else here work fine on Home — only
graphical remoting is unavailable, and §6.3's SSH-over-Tailscale covers the
terminal case regardless of edition.

**Windows Update restarts can be deferred, not disabled**, on a consumer SKU.
Active hours cap at 18 hours. A long render is protected by being resumable —
our chunked renders restart by counting frames already on disk — not by trying
to block reboots outright.

**The venvs are not relocatable.** `pyvenv.cfg` and every `bin/` shebang carry
absolute paths, so moving the checkout after installing means re-running
`install/wsl/bootstrap.sh`, not copying the tree. Pick the final path first.

## 8. Untested on real hardware

Written and statically validated in a Linux container, never executed on
Windows. The PowerShell parses cleanly under PowerShell 7.5 and passes
PSScriptAnalyzer with no errors or warnings, and is ASCII-only because
`powershell.exe` on Windows 11 is still 5.1 and misreads unmarked UTF-8. That is
not the same as having been run.

Specifically unverified until someone runs it on the box:

- the boot task actually surviving a reboot (§7)
- `claude remote-control` running headless under systemd with no TTY — it is an
  interactive-leaning process, and if it refuses, the fallbacks are a Windows
  Scheduled Task or running it under `tmux`
- `vmIdleTimeout=-1`, which is widely used but absent from Microsoft Learn
- CUDA-in-WSL on the specific card, if there is one

`install/windows/verify-host.ps1` and `make host` exist to turn each of these
into a checked answer rather than an assumption.

---

## 9. Why not the alternatives

**Native Windows, no WSL.** Claude Code runs natively on Windows and this would
avoid §7 entirely — but the studio stack does not, and the sandboxed Bash tool
is unavailable there. A PowerShell port of the render pipeline is a rewrite we
have no reason to buy.

**Claude Managed Agents self-hosted sandboxes.** Real, and genuinely
self-hosted — orchestration stays with Anthropic while tools execute on your
hardware. Two disqualifiers: it requires a Linux host with `/bin/bash` at that
exact path (Windows is not supported), and it is driven by API key over REST/SSE
rather than from claude.ai, so it does not answer "use it from Claude web."

**Quick tunnels (trycloudflare.com).** Free and instant, but a new random
hostname on every restart, a 200 in-flight request cap, no SLA, and — decisively
— no Server-Sent Events, which Streamable HTTP needs.

---

## 10. When something is wrong

| Symptom | First move |
|---|---|
| Session missing from claude.ai/code | `systemctl status viralreel-remote-control`; ~10 min offline ends a session by design |
| Remote Control refuses to start | check for `ANTHROPIC_API_KEY` / `ANTHROPIC_BASE_URL` / telemetry opt-outs; it needs `/login`, not a key |
| Jobs queue but never run | `systemctl status viralreel-jobd`; without systemd there is no worker |
| Job died with no error | `make logs ID=<n>`; then `make host` — out-of-space looks exactly like an engine crash |
| Disk full, deleting did not help | sparse VHD off: `wsl --shutdown` then `wsl --manage <distro> --set-sparse true` |
| Everything is slow | repo under `/mnt/c`? move it to the Linux filesystem |
| MCP tools absent in the session | `server/.venv` missing — re-run `install/wsl/bootstrap.sh` |
| VMAF missing from delivery QC | system ffmpeg without libvmaf; `make host` names which build is in use |
