# Decision log

Standing decisions, each with its trigger for re-evaluation. A decision that lives only in a
chat thread doesn't exist — this file is where the studio's choices become findable and
reversible on purpose. (The habit exists because the no-TikTok call was made and then found
nowhere in the repo by the Fable-5 review.)

---

## D1 — Distribution is manual-first. yt-agent automation is phase 2.
**Decided:** 2026-08 (founder). **Status:** active.

The founder uploads via YouTube Studio, assisted by the Claude-for-Chrome briefs in
`handoffs/`. No OAuth client, no Gemini key, no walkthrough at launch — the entire credential
surface shrinks to one ElevenLabs key. Manual upload also makes compliance C10 literal: a
human watches every video before the public does. Every upload MUST end with
`scripts/log_publish.py` or the 2/day cap goes blind.

**Re-evaluate when:** manual uploading at 1/day is genuinely painful, or cadence rises, or
scheduling precision starts to matter. Phase-2 prerequisites live in `docs/07`.

## D2 — No TikTok cross-posting at launch.
**Decided:** 2026-08. **Status:** active.

Same 9:16 file, near-zero marginal effort — declined anyway: (1) Higgsfield's TikTok publish
billing is **unverified** (its schemas are silent on credit cost; treat as paid until proven
otherwise), and it requires Higgsfield-hosted upload; (2) the compliance gate's checks are
YouTube-shaped — nothing audits TikTok's disclosure or reuse rules; (3) one platform's
retention data is confounded enough at launch.

**Re-evaluate when:** 30+ episodes published AND YouTube retention is stable, or TikTok
publishing is confirmed credit-free via a manual-upload path (which would fit `handoffs/`).

## D3 — Font loading: the CC-sync plan is REVERSED for Linux render hosts.
**Decided:** 2026-08 (Fable-5 review, B1b). **Status:** active.

"Sync Acumin via the CC desktop app" cannot execute on Linux — no CC desktop app exists.
On a Linux render host (including the cloud session), renders fall back to **Liberation Sans**,
measured typographically safe (uniform digit widths, both weights) but a different face.
Options to ship in Acumin: render on a CC-synced macOS/Windows machine, or install separately
licensed OTFs into fontconfig. `doctor.sh` reports the host's state loudly; pilot renders may
ship in Liberation Sans **only as an explicit founder decision per batch**.

Also corrected: tabular figures never gated the odometer roll (fixed-width DigitWheels);
`tnum` matters at rest. The claim is fixed everywhere it appeared.

**Re-evaluate when:** a render host with Acumin exists, or the founder wants a permanently
self-hostable licensed family instead.

## D4 — C7 template-similarity threshold: 0.70 → 0.50.
**Decided:** 2026-08 (measured). **Status:** active; CI-pinned.

Measured distribution: legitimate on-beat scripts max **0.216** pairwise; a lazy noun-swap
**0.762**; nothing in between. 0.50 keeps zero measured false-positive risk and halves the
evasion margin. The mechanical check is a tripwire — a one-word-per-sentence pad scores 0.000,
so the compliance-officer's semantic review is load-bearing and named as such.

**Re-evaluate when:** 50+ real scripts exist to re-measure the distribution.

## D5 — Music generation is forbidden; music itself is nearly absent.
**Decided:** 2026-08 (review S4). **Status:** active; CI-pinned.

`ELEVENLABS_API_KEY` silently arms ElevenLabs-billed music generation inside the vendor's
assets stage — with no policy anywhere until now. Policy: `music.generation: forbidden`; the
format runs on VO and archival sound. If a bed is ever wanted: free sources only.

## D6 — The price database goes public early (ladder step 3a).
**Decided:** 2026-08 (review M2). **Status:** active, not yet built.

The database is the declared moat and the off-platform hedge against the one Fatal risk —
keeping it private for six months hedged nothing. Step 3a: a free, public, read-only index of
**already-aired** price pairs (they're on screen anyway; publishing leaks nothing) from
~month 2, on the connected Cloudflare free tier, with email capture. Paid products stay at
months 6–12 (step 3b, unchanged).

## D7 — ElevenLabs is primary VO; Piper fallback is per-episode and never silent.
**Decided:** 2026-08 (review M4/S4). **Status:** active.

Measured runway: worst-case ~56, typical ~95–168 episodes on the current 124,926-credit
balance — one episode costs ~0.6% of the pool. Shipping Piper to "save credits" spends brand
recognition on a non-scarce resource. A dead key must degrade LOUDLY: fallback is a decision
recorded in the episode log, not an automatic swap.

## D8 — The studio platform: capability is universal, permission is per-project.
**Decided:** 2026-08 (platform integration). **Status:** active; CI-pinned (tests/test_platform.py).

The studio integrates generative engines, drama pipelines, animation suites and foley
models via `config/platform.yaml` (docs/10) — and none of that changes one rule of Price
Archaeology, whose doctrine (docs/04, docs/05) remains project law. Four standing terms:

1. **$0 default, mechanically.** `cost: paid` modules ship `enabled: false`; both the
   manifest loader and the test suite hard-fail otherwise. Enabling a paid module is a
   per-project founder edit. (This is why Open-Generative-AI and higgsfield-skills sit in
   the manifest disabled: catalogued so nobody mistakes them for free engines.)
2. **The gate is fenced off from automation.** `ralph/ralph.sh` reverts and kills any loop
   that touches `scripts/gate.py`, `tests/`, or `docs/05-compliance.md`.
3. **Catalog, don't hoard.** A module enters the manifest only when a department charter
   owns it; evaluated-and-declined tools are recorded in docs/11 with reasons.
4. **Loops are bounded and end at human gates.** Hook choice and publish remain human;
   no iteration budget is unbounded.

**Re-evaluate when:** a second production project actually launches (revisit Kitsu/AYON
tracking and the disabled farm/distribution modules), or a paid engine is proposed for a
specific project (that's a per-project decision, logged here as its own entry).

## D9 — Remote operation is a steering wheel, not a work queue.

The studio can now run on a machine you are not sitting at (docs/15). Three
independent limits decide how: a Claude Code Remote Control session ends after
~10 minutes offline, a claude.ai tool call is capped at 300 seconds, and a
Cloudflare tunnel returns 524 at 125. Nothing that takes hours can live inside
any of them.

So remote callers never execute work — they enqueue it. `scripts/studio/jobd.py`
holds the queue, systemd holds the worker, and the render survives the session,
the laptop lid and the network. A job started with `&` does not, which is why
there is no "just run it" path in the remote surface.

Three consequences worth stating, because each one closed off an easier option:

**The allowlist is the security boundary.** `config/jobs.yaml` is the entire set
of things the machine will do on request. A caller names a recipe and fills
declared slots; each slot is regex-checked, and the result runs as argv with no
shell. `argv[0]` must be literal, so the command can never come from a
parameter. Tests assert this against the shipped file — widening a pattern for
convenience fails CI.

**The claude.ai connector is OAuth or nothing.** Claude accepts a connector
that speaks OAuth or one with no authentication at all; a static bearer token is
a beta you must be granted. Authless would mean anyone who learned the URL could
queue jobs on someone else's PC, so the studio runs its own OAuth 2.1
authorization server (`server/studio_auth.py`).

Single-owner by design: one passphrase set at install, scrypt-hashed, constant-time
compared, locked out after repeated failures. There are no accounts because a
second user is not a requirement here, and every account system is one more thing
to be wrong on an unattended machine. `/authorize` never mints a code — it parks
the request and redirects to a consent page, so the passphrase is the only thing
that converts a connection attempt into a token. Refresh tokens rotate; codes and
tokens are stored as digests, so a stolen database is an inventory rather than a
key ring.

This is the one place in the repo that answers the public internet, so its tests
mostly assert refusal — no token, wrong passphrase, wrong PKCE verifier, replayed
code, spent refresh token, revoked token — and they run against a live server on
every CI build rather than mocking the flow.

**Delivery does not change.** Films still ship as a commit to `releases/` and a
GitHub raw link. Cloudflare's terms reserve the right to limit free accounts
serving video, and more to the point, a delivery path that already works should
not be replaced by one that depends on the host being awake.

The honest weak point is documented rather than hidden: Microsoft supports no
way to start a WSL distro at boot with nobody logged in. We use a Task Scheduler
ONSTART task and `vmIdleTimeout=-1`, neither documented for this purpose, and
ship `install/windows/verify-host.ps1` to turn "it should come back" into a
checked answer after a real reboot.
