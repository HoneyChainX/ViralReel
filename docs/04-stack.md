# 04 — The Stack

**Design constraint: $0 marginal cost per video.** No paid video models, no image credits, no
per-generation billing. The only paid component is your existing ElevenLabs subscription, and
the pipeline degrades gracefully to free Piper TTS without it.

---

## Why this stack, specifically

The obvious 2026 approach is to generate everything with a paid video model. For this channel
that would be *worse as well as more expensive*:

1. **Archival footage is the product.** Price Archaeology is about real 2016. Real 2016 footage
   from Archive.org is more persuasive than any generated approximation, and it is free.
2. **Generated b-roll is what the slop crackdown targets.** Real sourced footage + original
   research is the opposite signal.
3. **Every dollar of marginal cost is a dollar of risk** on a channel whose Shorts ad revenue
   is structurally capped at cents.

The paid path is both the expensive option and the strategically weaker one. That's rare, and
it's the whole reason this stack looks the way it does.

---

## Topology

```
                    ┌─────────────────────────────────────┐
                    │   ViralReel  (this repo)            │
                    │   agents · config · scripts · gate  │
                    └──────┬────────────────────┬─────────┘
                           │                    │
              ┌────────────▼──────────┐  ┌──────▼──────────────────┐
              │   OpenMontage         │  │ youtube-automation-agent│
              │   PRODUCTION          │  │ DISTRIBUTION            │
              ├───────────────────────┤  ├─────────────────────────┤
              │ hybrid pipeline       │  │ SEO optimizer           │
              │ Archive.org/Wikimedia │  │ Publishing + scheduling │
              │ Remotion compose      │  │ Analytics collection    │
              │ FFmpeg encode 9:16    │  │ Dashboard :3456         │
              │ ElevenLabs / Piper TTS│  │ SQLite store            │
              └───────────┬───────────┘  └──────────┬──────────────┘
                          │                         │
                     out/<slug>.mp4  ──────────────▶│──▶ YouTube
```

**Division of labour:** OpenMontage makes the video. youtube-automation-agent moves it. ViralReel
decides what gets made and whether it's allowed out. Neither external repo is forked or
modified — both are pinned as cloned dependencies so upstream fixes flow in cleanly.

---

## Component decisions

| Need | Choice | Why not the alternative |
|---|---|---|
| Pipeline | OpenMontage **`hybrid`** | Built for "source footage + designed support assets" with quality gates for source/support balance and overlay density — literally archive-on-the-bottom, data-on-the-top. `stability: production`. See the correction note below |
| Footage | Archive.org, Wikimedia Commons | Free, period-accurate, public domain. Pexels as filler only |
| Composition | Remotion | React; the `<PriceOdometer>` signature move needs programmatic control that a template editor cannot give |
| Narration | ElevenLabs (yours) → Piper fallback | Voice consistency is channel branding; Piper keeps cost at zero if the sub lapses |
| Encode | FFmpeg | Bundled |
| Publish/SEO/analytics | youtube-automation-agent | Solves OAuth, quota, scheduling, and the analytics loop — all boring, all already done |
| LLM for that agent | Gemini free tier | It supports a free pipeline end-to-end; Claude does the creative work upstream where it matters |

### What we deliberately do not use
Veo, Kling, Runway, Higgsfield, Suno, FLUX, GPT Image — every paid generator. Not because
they're bad, but because generated b-roll actively weakens a provenance channel *and* costs
money. If we ever need motion we can't source, `motion-director` builds it in Remotion from
data. Data-driven motion is on-brand; synthetic footage is not.

---

## Install

```bash
make setup
```

Which does:

```bash
mkdir -p vendor
git clone https://github.com/calesthio/OpenMontage.git        vendor/openmontage
git clone https://github.com/darkzOGx/youtube-automation-agent.git vendor/yt-agent

# OpenMontage
cd vendor/openmontage && make setup        # venv, requirements, remotion npm, piper
cp .env.example .env

# youtube-automation-agent
cd vendor/yt-agent && npm install && npm run walkthrough   # interactive OAuth + keys
```

**Prerequisites:** Python 3.10+, Node.js 18+ (22+ if you use HyperFrames), FFmpeg, git.
`make doctor` verifies all of them and tells you exactly what's missing.

---

## Configuration

Two `.env` files, one per vendor. `make setup` templates both from `config/env.template`.

**`vendor/openmontage/.env`** — production
```bash
ELEVENLABS_API_KEY=          # your subscription — the only paid key
PEXELS_API_KEY=              # free tier, optional filler footage
VIDEO_GEN_LOCAL_ENABLED=false
# Deliberately unset: FAL_KEY, RUNWAY_API_KEY, KLING_API_KEY, XAI_API_KEY,
# SUNO_API_KEY, OPENAI_API_KEY — leaving these empty is a cost control,
# not an oversight. OpenMontage's provider selection cannot bill what it cannot see.
```

**`vendor/yt-agent/.env`** — distribution
```bash
GEMINI_API_KEY=              # free tier
API_KEY=                     # protects the local dashboard's mutating endpoints
PRIVACY_STATUS=private       # every upload lands private; a human flips it public
```

> **`PRIVACY_STATUS=private` is not a default we inherited — it is a decision.** Nothing this
> studio produces goes public without a human looking at it. It is the cheapest insurance
> available against the one risk that can end the channel.

Real secrets live only in the vendor `.env` files, which are gitignored. Nothing in this repo
ever contains a key.

---

## Correction: what the smoke test found

`make setup` was run against the real upstream repos and two things in this document's first
draft were wrong. Both are recorded here rather than quietly fixed, because "verified against
the installed thing" and "read off a README" are different confidence levels and the
difference should be visible.

**1. The pipeline was misnamed and mischosen.** The file is `documentary-montage.yaml`
(hyphens, not underscores) — but more importantly it was the wrong pipeline. It is a
music-synced, CLIP-retrieval *tone poem* pipeline in the Adam Curtis mould, and `stability:
beta`. The right one is **`hybrid`**: "videos that combine source footage with designed or
generated support assets… montage edits with support inserts," with quality gates for
**source/support balance** and **overlay density**, at `stability: production`. Its own stage
notes require that "generated inserts do not eclipse source truth" — our compliance posture,
in upstream's words — and that Remotion composes "source footage and React support overlays
in one pass," which is exactly `<PriceOdometer>` over archival footage.

**2. There is no `python -m pipeline run` CLI.** That command was inferred from the README and
does not exist — there is no `pipeline` module. OpenMontage is **agent-driven**: stage-director
skills under `skills/pipelines/hybrid/` tell the agent how to run each stage using `tools/`.
`python -m backlot open` opens the live production board. `.claude/agents/post-supervisor.md`
now describes the real model.

Confirmed working in the same run: `tools/video/stock_sources/archive_org.py` and
`wikimedia.py` are shared across pipelines, so `hybrid` retrieves the same free archival
footage; and OpenMontage's own `youtube_shorts` profile is 1080×1920, matching gate check C9
exactly.

## Making an episode

```bash
make episode SLUG=airpods-159
```

| # | Stage | Owner | Artifact |
|---|---|---|---|
| 1 | Research | `trend-archaeologist` | `content/episodes/<slug>/evidence.json` |
| 2 | Format check | `head-of-format` | segment + beat assignment |
| 3 | Hooks (12) | `hook-writer` | `hooks.md` → **human picks** |
| 4 | Script | `script-editor` | `script.md` (95–130 words) |
| 5 | Assets | `archive-sourcer` | `assets/` + `licenses.json` |
| 6 | Scene plan | `motion-director` | `scene_plan.json` |
| 7 | VO | `voice-director` | `vo.mp3` (ElevenLabs) |
| 8 | Compose | `post-supervisor` | `out/<slug>.mp4` via OpenMontage |
| 9 | **Gate** | `compliance-officer` | `gate.json` — **PASS required** |
| 10 | Package | `seo-packager` | `packaging.json` |
| 11 | Publish | yt-agent | private upload → human flips public |

Stages 1–8 run unattended. Stages 3 and 11 stop for a human. That split is intentional: taste
and liability get eyes, everything else gets automated.

---

## Cost model

| Item | Marginal | Fixed |
|---|---|---|
| Research, writing, orchestration | $0 | Claude Code sub |
| Archival footage | $0 | — |
| Narration (ElevenLabs) | $0 | your existing sub |
| Compose + encode | $0 | electricity |
| Publish, SEO, analytics | $0 | — |
| **Per video** | **$0.00** | — |

For comparison, the AI-shorts market average runs $50–300 per video. At one video per day
that's a $18k–110k annual production line we are not buying — against Shorts ad revenue that
is capped at cents per thousand views. This is the arithmetic that makes the channel viable at
all, and it is worth defending against every future temptation to "just add one paid model."

---

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Render is a slideshow | Not enough motion assets | OpenMontage slideshow-risk scorer catches it; `archive-sourcer` sources more clips |
| VO sounds flat | Default ElevenLabs settings | `voice-director` owns settings + pacing marks; never ship defaults |
| Publish fails silently | OAuth token expired | `make doctor`; re-run yt-agent walkthrough |
| Gate always fails | Missing sources in evidence pack | Correct — that's the gate working. Fix the research |
| Costs appeared | A paid provider key got set | Audit both `.env`s; unset it. `make doctor` warns on paid keys |
