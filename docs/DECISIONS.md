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

## D8 — Reels ops: hybrid pipeline first; paid virality/restyle tools deferred on evidence.
**Decided:** 2026-08-03 (founder handoff + measured tool state). **Status:** active.

Founder handed over a reels plan naming Higgsfield (`shorts_studio`, `reframe`,
`virality_predictor`), Adobe video tools, Postiz, Canva, n8n and Adspirer against three gaps:
volume, cross-post cadence, feedback loop. Measured reality (`docs/11-reels-ops.md`):

- **Higgsfield balance is 0 credits (free plan).** `shorts_studio` 45s = 135 credits; `reframe`
  to 9:16 @1080p = 419 credits. Nothing executable. Funding it reverses
  `paid_generators_enabled: false` and the $0.00/video guarantee.
- **`shorts_studio` is the wrong shape for Gap 1** regardless of funding — it restyles an
  existing video, it does not build a reel from a script. **`reframe` is redundant**: we render
  native 1080×1920.
- **Postiz and Adspirer plugins are enabled but expose no callable surface in this Claude Code
  session** (they are claude.ai-chat plugins). Founder- or chat-side actions.
- **Canva is already toggled on in chat; it needs authorization, not a toggle.** **n8n is the one
  genuinely toggled off.** Both are founder-only settings actions.

**Decision:** close Gap 1 with the **hybrid pipeline** — founder generates the 4 Firefly hero
clips (their taste, from `adobe-master-prompt.md`), the studio automates assembly, real-data
overlays, captions, odometer, stamp, loudness, QC and gate. $0. Close Gap 3 with the
already-built analytics handoff (real retention beats a pre-publish prediction, and costs
nothing). Defer Higgsfield credits until ~10 published episodes give retention data to validate
whether `virality_predictor` correlates with our actual curves. Defer Adspirer until a winner
exists.

**Re-evaluate when:** (a) 10+ episodes published with retention data — then price
`virality_predictor` against a known signal; (b) founder decides the $0 guarantee is worth
trading for batch throughput, as an explicit strategy change with the RPM math re-run.
