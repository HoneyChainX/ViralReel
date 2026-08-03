# 10 — The Studio Platform

ViralReel began as one channel's pipeline. This document describes the layer that turns it
into a **studio platform**: one manifest of integrated open-source tools, one team of agents
modeled on top-tier studio roles, one loop harness that does the unattended work — able to
run Price Archaeology exactly as before *and* to stand up scripted, animated, or generative
projects without inheriting a single rule that doesn't apply to them.

The research behind every choice here — repo identification, department-by-department tool
picks, real studio org charts, the Ralph technique — is in
[`docs/11-platform-research.md`](11-platform-research.md).

---

## The one idea

**Capability is universal; permission is per-project.** The platform integrates generative
video engines, drama pipelines, animation suites, and foley models — and Price Archaeology
still cannot use most of them, because its format's rules (docs/05) are project law and the
platform never overrides project law. A studio that can do everything, everywhere, all at
once is a studio with no formats; this one has formats.

That resolves the apparent contradiction between docs/04 ("we deliberately do not use
generators") and this document (which installs three of them): docs/04 is Price
Archaeology's doctrine, and it stands. The platform exists so the *next* project — a drama
serial, an animated short — starts from an installed, verified, license-audited stack
instead of from zero.

## Topology

```
                 ┌───────────────────────────────────────────────────┐
                 │  ViralReel — THE STUDIO                           │
                 │  21 agents · gate · ralph loops · manifest        │
                 └──────┬──────────────┬──────────────┬──────────────┘
                        │              │              │
             ┌──────────▼───────┐ ┌────▼──────────┐ ┌─▼──────────────────┐
             │ PRODUCTION       │ │ GENERATION    │ │ AUTHORING (human)  │
             │ (core, $0, CPU)  │ │ (genai, GPU)  │ │ (desktop tools)    │
             ├──────────────────┤ ├───────────────┤ ├────────────────────┤
             │ OpenMontage      │ │ ComfyUI ◀─────┼─┼─ every model runs  │
             │ Remotion+FFmpeg  │ │  ├ LTX-2.3    │ │  as a graph        │
             │ video-shotcraft  │ │  ├ Wan2.2     │ │ OpenToonz          │
             │ screenplain      │ │  └ RIFE       │ │ Blender(+MCP,     │
             │ auto-editor      │ │ DramaClaw     │ │   Storypencil)     │
             │ OpenTimelineIO   │ │ VoxCPM/       │ │ Toonflow           │
             │ whisperX/kokoro  │ │  chatterbox   │ │ Pinokio (launcher) │
             │                  │ │ MMAudio/      │ │                    │
             │                  │ │  ACE-Step     │ │                    │
             └────────┬─────────┘ └──────┬────────┘ └────────┬───────────┘
                      │                  │                   │
                      │        studio/adapters/*.py          │ authored scenes,
                      │        (the only sanctioned seams)   │ batch-rendered
                      ▼                  ▼                   ▼
             ┌────────────────────────────────────────────────────────┐
             │  COMPLIANCE GATE (unchanged, untouchable)              │
             └───────────────────────────┬────────────────────────────┘
                                         ▼
             ┌────────────────────────────────────────────────────────┐
             │  DISTRIBUTION — manual-first (D1) · yt-agent installed │
             │  · Postiz catalogued for the multi-platform future     │
             └────────────────────────────────────────────────────────┘
```

## The four pieces

### 1. The manifest — `config/platform.yaml`

26 modules across six profiles (`core`, `distribution`, `genai`, `animation`, `voice`,
`audio`), each with pinned repo, license, cost class, GPU floor, headless-drivability, and
declarative doctor checks. Managed by `scripts/studio/platform.py`:

```bash
python3 scripts/studio/platform.py list   --profile all
bash    scripts/studio/install.sh         --profile core     # or genai/animation/…
bash    scripts/studio/doctor.sh          --profile core     # exit 1 on any red check
```

Three mechanical invariants, enforced by the loader itself:
- `cost: paid` ⇒ `enabled: false`. The manifest **cannot load** with a paid module enabled.
  Enabling one is a founder edit, made per project, on purpose.
- Desktop authoring tools (`install: desktop`) are human-installed; the installer skips
  them and the doctor never gates on them.
- Vendors are cloned to `vendor/<id>`, never forked. Verified installs get their SHA pinned.

### 2. The seams — `studio/adapters/`

Agents never poke vendored engines directly; they go through small, stdlib-only, honest
adapters, each with a `--selftest`:

| Adapter | Seam |
|---|---|
| `comfyui_client.py` | POST workflow JSON to ComfyUI `/prompt`, wait, collect outputs — the entire generative lane rides this |
| `tcomposer.py` | OpenToonz's one automatable edge: authored `.tnz` scenes in, frames out |
| `dramaclaw_client.py` | health/report for the self-hosted script→film engine; deliberately refuses to configure its billing gateway |

Approved generative looks live as committed ComfyUI graphs in `studio/workflows/` —
reproducible artifacts, not prompt folklore.

### 3. The staff — seven new agents on real studio roles

Mapped from how animation houses, VFX/post houses, and creator studios actually staff
(research: docs/11 §3): `pipeline-td`, `render-wrangler` (platform engineering — the
"fully automatable band" of real studios), `previs-director`, `gen-supervisor`,
`animation-director`, `story-showrunner` (picture), `sound-designer` (sound). Charters in
`.claude/agents/`, org chart in docs/03. The taste-and-accountability band — director,
final cut, publish — stays human, exactly as it does at the studios these roles come from.

### 4. The loops — `ralph/`

Bounded autonomous work loops (the Ralph technique — stateless `claude -p`, file-based
memory, one backlog item per iteration; see `ralph/README.md`): `platform-install`,
`episode-factory`, `integration-qa`, `research-slate`. Guardrails are mechanical: iteration
budgets, gate paths reverted-and-killed on contact, human gates end loops, $0 doctrine
enforced. `make ralph JOB=<job>` to run one.

## What was deliberately not adopted

Catalogued in docs/11 with reasons, but the short version — a platform earns more trust by
what it declines:

- **ViMax / VideoClaw (agent film crews):** excellent projects; *we already are the crew.*
  Adopting a second orchestrator inside an agent studio duplicates the org chart. We take
  their stage designs as reference, not their runtime.
- **Kitsu/AYON (studio tracking):** real-studio-grade, and overkill until there are
  multiple simultaneous productions. The episode-folder + SLATE.md system is the tracker
  at current scale. Revisit at 3+ concurrent projects.
- **Open-Generative-AI ("open Higgsfield") and Higgsfield's official skills:** catalogued
  as `cost: paid`, disabled. Higgsfield has open-sourced no models; both routes bill
  credits per call. Nothing about "open" in a repo name changes where the GPU lives.
- **HunyuanVideo, FLUX-dev, F5-TTS, AudioCraft weights:** license traps (territory/MAU
  caps, non-commercial weights) documented in docs/11 — kept out of the manifest so no
  loop ever installs them by accident.
- **OpenCue/Flamenco farm infrastructure:** noted as the growth path in render-wrangler's
  charter; not built before there's a farm.

## Doctrine (recorded as DECISIONS D8)

1. Project law outranks platform capability, always. The gate is untouchable by every
   platform component, mechanically.
2. $0 marginal cost is the platform default; paid is per-project, founder-enabled, and
   impossible to enable silently.
3. Catalog, don't hoard: a module enters the manifest when a department owns it; everything
   else stays research.
4. Loops are bounded, auditable, and end at human gates.
