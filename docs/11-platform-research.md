# 11 — Platform Research

The evidence behind docs/10. Three sweeps, run 2026-08-03: (1) exact identification of the
founder's requested repos, (2) department-by-department search for the best open studio
tooling, (3) how top-tier studios staff productions + the Ralph loop technique. Recorded so
future decisions argue with the research, not with memories of it.

---

## 1. The requested repos, resolved

The founder's list arrived as spoken names; several were fuzzy. What each actually is:

| As requested | Resolves to | License | Verdict |
|---|---|---|---|
| "open Higgsfield ai" | `Anil-matcha/Open-Generative-AI` (renamed from *Open-Higgsfield-AI*, 25.5k★) — a frontend whose generation calls bill the Muapi **cloud API**. Higgsfield-the-company has open-sourced **no models**; its official repos (`higgsfield-ai/skills`, `/cli`) are thin clients over its paid API | MIT (app) | Catalogued as `cost: paid`, **disabled**. "Open" in the name doesn't move the GPU |
| "ltx2.5" | `Lightricks/LTX-2` — current open weights are **LTX-2.3** (22B, joint audio+video, native 4K). No 2.5 exists | LTX-2 custom (open weights, commercial OK, non-OSI) | **Adopted** (genai) — flagship engine |
| "comfy ui" | `Comfy-Org/ComfyUI` (123k★) — node-graph engine; REST `/prompt` + WebSocket | GPL-3.0 | **Adopted** (genai) — the automation backbone |
| "wan video" | `Wan-Video/Wan2.2` — last **open-weights** Wan (2.5/2.6/2.7 are API-only) | Apache-2.0 | **Adopted** (genai) — the permissive counterweight |
| "pinokio" | `pinokiocomputer/pinokio` — desktop AI-app launcher | MIT | Catalogued (desktop, disabled) — founder convenience, not a pipeline part |
| "Open Toonz" | `opentoonz/opentoonz` — pro 2D animation suite; `tcomposer` is its one headless edge | BSD-3 (mod.) | **Adopted** (animation, desktop) with a tcomposer adapter |
| "drama claw" | `dramaclaw/dramaclaw` (3k★, 2026) — script→finished-film AIGC engine; Docker + FastAPI; inference via configurable OpenAI-compatible gateway | Elastic-2.0 | **Adopted** (genai) — gateway unset = $0; never resold as a service |
| "toon flow" | `HBAI-Ltd/Toonflow-app` (13.3k★) — novel/script→animated-short-drama Electron workstation | Apache-2.0 | **Adopted** (animation, desktop) |
| "video-shotcraft" | `Vincentwei1021/video-shotcraft` (3.4k★) — agent skill: 106 shot recipes, 161 motion previews, Remotion template | Apache-2.0 | **Adopted** (core) — feeds previs + motion |
| "vox director" | **Does not exist** — only empty 0-star stubs on GitHub. Closest real project for the implied role: `OpenBMB/VoxCPM` (promptable voice design TTS) | VoxCPM: Apache-2.0 | VoxCPM **adopted** (voice) as the honest substitute |
| "open montage" | `calesthio/OpenMontage` (44.9k★) — confirmed; already the production spine | AGPL-3.0 | Already core |

## 2. Department picks (second sweep)

Adopted into the manifest — selection bias: permissive license, maintained, headless-drivable:

| Dept | Adopted | Why |
|---|---|---|
| Story | `vilcans/screenplain` (MIT) | Fountain plain text as canonical script substrate; pure CLI |
| Previs | video-shotcraft + Blender Storypencil | shot vocabulary + real 3D blocking; no good standalone "AI storyboard" OSS exists |
| Edit | `WyattBlue/auto-editor` (Unlicense) | automatable rough-cut with timeline export; active Aug 2026 |
| Pipeline | `AcademySoftwareFoundation/OpenTimelineIO` (Apache) | cuts move as .otio, not prose |
| 3D/anim | `blender/blender` (GPL) + `ahujasid/blender-mcp` (MIT) | the irreplaceable backbone + the agent seam |
| Speech | `m-bain/whisperX` (BSD-2) · `hexgrad/kokoro` (Apache) · `resemble-ai/chatterbox` (MIT) | alignment-grade captions · CPU-viable permissive TTS (Piper successor) · local expressive cloning |
| Sound | `hkchengrex/MMAudio` (MIT) · `ace-step/ACE-Step` (Apache) | the missing foley dept · permissive full-song music |
| Restore | `hzwer/Practical-RIFE` (MIT) | standard interpolation; SeedVR2 noted below as too heavy for now |
| Distribution | `gitroomhq/postiz-app` (AGPL) | 30+ platforms, public API — catalogued **disabled** under D1/D2 |

Evaluated, **not** adopted (the declines matter as much as the picks):

- **Video models:** CogVideoX (Apache, diffusers-native — first candidate if a third engine
  is ever needed); HunyuanVideo (best open quality, but territory/MAU license caps);
  SkyReels-V2 (MIT, infinite-length, slowing); Mochi/Open-Sora (frozen).
- **Lip-sync bench (for when a project needs it):** LatentSync (Apache, best quality),
  MuseTalk (MIT, real-time), LivePortrait (MIT but its InsightFace dep is non-commercial),
  EchoMimic-v2 (Apache). SadTalker is superseded.
- **License traps, kept out mechanically:** FLUX.1-dev weights non-commercial (schnell is
  Apache); F5-TTS / Fish Speech / AudioCraft weights non-commercial; XTTS-v2 dead+CPML;
  Stable Audio Open capped under $1M revenue; MovieAgent/Anim-Director ship no license.
- **Agent film crews:** `HKUDS/ViMax` (11.6k★, MIT) and `HITsz-TMG/VideoClaw` (FilmAgent
  lineage, MIT) are the state of the art — and duplicating an org chart we already have.
  Reference, not runtime.
- **Studio tracking:** Kitsu/Zou + AYON are the real-studio pairing (TACTIC is dead);
  adopt at 3+ concurrent productions.
- **Farm:** SaladTechnologies/comfyui-api catalogued disabled (enable at >1 GPU worker);
  Flamenco for a future Blender farm; OpenCue only past both.
- **Editing engines:** MLT (`melt`) noted as the headless-NLE reserve; MoviePy for
  utility composition; stable-ts as whisperX alternative.
- **Restoration:** SeedVR2 (Apache, SOTA) wants H100-class hardware — re-evaluate when a
  restoration project justifies the iron.

## 3. Studio staffing research → agent roster

Sweep across three archetypes — feature animation (Pixar/Ghibli-lineage pipelines), VFX/post
houses (ScreenSkills career map), creator/AI-native studios (MrBeast production handbook,
Corridor-scale ops, 2025-26 AI-studio titles). ~60 roles catalogued; they cluster into four
automation bands, and the bands drove the roster:

1. **Machine-ops (fully automatable):** render wrangler, pipeline TD, conform, channel
   ops, production tracking → became `pipeline-td`, `render-wrangler`; channel-ops was
   already `seo-packager`/`growth-analyst`.
2. **High-volume pattern work:** roto/matchmove, shorts cutting, thumbnail variants,
   retention analysis → already covered (growth dept) or arrives with future projects.
3. **Generative first-pass:** boards, layout, look-dev, hooks, scripts, temp sound →
   became `previs-director`, `gen-supervisor`, `animation-director`, `story-showrunner`,
   `sound-designer`; hooks/scripts were already staffed.
4. **Taste & accountability (stays human):** director, showrunner's final cut, VFX-sup
   client trust, the on-camera face, publish. The platform's human gates (hook choice,
   publish) sit exactly on this band — that boundary was already right and research
   confirmed it.

Supervisor roles (CG sup, comp sup, supervising animator) map to *reviewer agents with
human escalation* — which is why `gen-supervisor` and `animation-director` are written as
reviewers with quality bars, not as generators.

## 4. The Ralph loop (technique notes)

Geoffrey Huntley's pattern (ghuntley.com/ralph): `while :; do cat PROMPT.md | claude ; done`
— the LLM as a **stateless function**, all memory in files and git. Production practice
(canonical `ghuntley/how-to-ralph-wiggum`, `snarktank/ralph`, Anthropic's ralph-wiggum
plugin):

- **One task per iteration**, absolute; small diffs, commit every lap.
- File layout: standing PROMPT + `AGENT.md` (operational notes only, ~60 lines) +
  `fix_plan.md` (regenerable backlog) — exactly what `ralph/` implements.
- **Search before assuming** — the known Achilles' heel is wrongly concluding code is
  missing and building duplicates.
- **No placeholder implementations** — placeholder rot is a named failure mode.
- **Backpressure = correctness**: tests/lints must pass before commit.
- **Always bound iterations** (unbounded loops are a cost incident, $50–100+ per long run);
  sentinel promises are unreliable as the *sole* stop — belt and braces.
- Known failure modes: duplicate implementations, overbaking ("baked with unspecified
  latent behaviours"), spec drift, broken-tree wakeups (fix: commit-per-lap + reset).
- Best fit: open-ended *verifiable* work (installs, QA, migrations, stocked backlogs).
  Poor fit: ambiguous requirements, architecture, security-sensitive code — which is why
  the gate and its tests are hard-fenced off from every loop in this repo.

Our deviations from canon, on purpose: `--permission-mode acceptEdits` instead of
`--dangerously-skip-permissions` (loops here run on real machines, not throwaway
sandboxes), a protected-path tripwire that reverts-and-kills, and human gates as loop
terminators.

---

*Primary sources are linked in the research transcripts; headline references:
ghuntley.com/ralph · github.com/ghuntley/how-to-ralph-wiggum · github.com/snarktank/ralph ·
ScreenSkills VFX career map · Simon Willison's MrBeast-handbook summary · the GitHub repos
named above, each verified via API on 2026-08-03.*

---

## 5. Film-assembly research (third sweep, 2026-08-03)

Question: how to make storyboards, scene flow, montage, and the linking of many scene-videos
into one film — and which top-studio open repos to adopt. Two parallel deep sweeps
(assembly tooling; studio/expert repos). Verdicts:

**The spine decision, independently confirmed:** a plain film manifest + ffmpeg as the
default conform renderer; OTIO as the *derived* interchange projection (it describes
timelines, it does not render them — there is no official otio-ffmpeg render adapter);
MLT XML via `otio-mlt-adapter` → `melt` as the escape hatch for complex timelines.
Implemented as `studio/film/*.yaml` + `scripts/studio/conform.py`.

**Adopted from the sweep:**
- `Breakthrough/PySceneDetect` (BSD-3) — cut verification in conform QC: every manifest
  hard cut must exist in the stitched film (±0.5s); catches dropped scenes/double-joins.
- `OpenTimelineIO-Plugins` + `apetrynet/otio-mlt-adapter` (Apache/MIT) — EDL/AAF/FCPXML
  export and the write-only OTIO→MLT bridge, added to the otio module.
- **VMAF is already available**: the pinned static ffmpeg build ships `libvmaf`
  (Netflix, BSD+Patent; 2026 "VMAF v1" models add banding/color awareness) — stitched-vs-
  mezzanine scoring needs no new module, only kept scene mezzanines.

**Continuity practice for generative multi-scene films (recorded for the GPU host):**
keyframe-first planning; **Wan 2.2 FLF2V** (first+last frame conditioning) is the best
open-weights tool for controlled scene joins; last-frame chaining
(`ffmpeg -sseof -0.05 -i sceneN.mp4 -frames:v 1 last.png` → I2V init for scene N+1) is the
cheap universal fallback with drift over many hops; identity: character LoRA (kohya
sd-scripts) > reference adapters (IP-Adapter/PuLID — note IPAdapter_plus is
maintenance-only since Apr 2025) > StoryDiffusion (code CC BY-NC — unusable commercially).

**Studied, not adopted (architecture references):** ViMax (MIT — its Screenwriter→Director→
Producer→Generator loop with dependency-aware continuity is the best current reference;
MIT permits lifting logic), VideoClaw (six-stage pipeline with reviewable intermediates;
**license discrepancy between sweeps — verify before any adoption**), MovieAgent (no
license), ShortGPT's "Editing Markup Language" (edit-decision-as-LLM-output precedent),
editly (manifest→ffmpeg precedent, drifting), MoneyPrinterTurbo (service-pattern reference).

**Studio-repo verdicts:** usd-core (pip, Modified Apache) — cheap bet on structured scene
description, adopt when a department actually uses it (D8 rule 3); raven — build-once OTIO
viewer for humans; Flamenco — the render-queue growth path (already in render-wrangler's
charter); **MoonRay honestly skipped** (real and CPU-first, but Rocky-9-centric multi-hour
build + RDL2/USD authoring buys nothing over headless Blender at this scale); OpenAssetIO
premature; photon wrong target.

**License landmines added to the map:** Remotion is source-available with a paid company
license (free for individuals/small teams) — fine today, budget for it at company scale;
StoryDiffusion code CC BY-NC; MovieAgent unlicensed; VideoClaw unverified.

---

## 6. Big-company open tools, skills & blueprints (fourth sweep, 2026-08-03)

Three parallel sweeps: NVIDIA · US/EU big tech · Chinese labs + the skills/blueprints
wave. Full verdict tables in the research transcripts; what matters:

**Adopted into the manifest (verified repos, owned by a department):**
- `NVlabs/LongLive` (Apache) — Wan-lineage autoregressive long video, 240s+, KV-recache
  on prompt switches — the in-model counterpart of our seamless-chaining contract.
  GPU-phase; continuity-supervisor compares it against seamless.py stitching per chain.
- `aigc-apps/VideoX-Fun` (Apache) — Wan-Fun InP first/last-frame weights; the mature
  FLF2V engine for keyframe-first chains.
- `facebookresearch/sam2` (Apache) — roto/masking; tiny models CPU-viable. (SAM 3.x is
  stronger but under the more restrictive SAM License — 2.1 stays the default.)
- `microsoft/VibeVoice` (MIT code+weights) — cleanest-rights voice stack in the bench;
  BitNet ASR runs real-time on 3 CPU threads.
- `google-ai-edge/mediapipe` (Apache, CPU-native) — per-frame QC eyes for post/editorial.
- `Comfy-Org/workflow_templates` — the canonical "blueprints" corpus for ComfyUI graphs.

**NVIDIA notebook (catalog):** VSS blueprint (video→text agents; its `vss-*` agent skills
are literally available in this session — future automated dailies-review/QC); Cosmos
Predict2.5 video-extension conditioning (limited-maintenance, watch Cosmos 3); NeMo
Parakeet ASR (CC-BY) for caption QC; `mudler/magpie-tts.cpp` (MIT, pure-CPU TTS, 63×
reference speed) as a Piper-class fallback candidate; TensorRT **Model-Optimizer**
(Apache) — the tooling behind official LTX-2 NVFP4/FP8 releases (3× faster, −60% VRAM on
RTX 50) — first thing to apply when the GPU host lands; Audio2Face-3D (open, Apache
training framework) for a future avatar format. Maxine: proprietary, skip. DALI: skip
(ffmpeg owns production I/O).

**US/EU notebook:** VMAF v1 models (Jun 2026) add banding/color awareness — refresh the
QC gate when packaging; DINOv3 embeddings as continuity/drift metrics for chains
(attribution clause); VideoPrism (Apache/CC-BY) for video retrieval-QC; Magenta RealTime
open music gen; Stable Audio 3 (<$1M community license); FLUX.2 Klein (Apache 4B/9B) as
GPU keyframe engine — repo name unverified at sweep time, verify before manifesting;
Intel OpenVINO as CPU inference runtime (has an LTX-Video pipeline). License watchlist:
CC-BY-NC blocks AudioCraft weights/CoTracker/ImageBind/FLUX.2-dev from the commercial
path; Adobe ships nothing real (catalog C2PA/contentauth for provenance tooling).

**China notebook:** the open/closed split hardened — Seedance/Kling closed, Alibaba's
open line froze at Wan2.2, Tencent open-but-encumbered. Long video is an
autoregressive-distillation story: Self-Forcing → Rolling Forcing (real-time, ckpt
released; licenses need verification) — the watchlist for our chaining layer, alongside
SkyReels-V3 V2V extension and KlingAI Research's MemFlow/ShotStream papers, all of which
validate the plan-then-refine + frame-handoff architecture. FramePack (Apache, 6 GB VRAM)
is the low-VRAM long-video tier. FunASR/CosyVoice3 catalogued (whisperX/Kokoro already
hold those seats). **Territory-clause traps found:** HunyuanVideo-1.5 (no EU/UK/KR, MAU
cap), MiniMax-H3 (excludes US/EU/UK/KR), SongGeneration (non-commercial) — manifest
entries must carry verified license AND territory before adoption; SEO farms are
fabricating "open" releases (a fake "Wan 2.7 open weights" among them).

**Skills wave:** HeyGen HyperFrames (open, agent-native motion graphics — its MCP is
connected to this session), Wan-skills, ComfyUI-Agent-Kit. Anthropic ships no official
video skills — this repo's studio-skill work remains differentiated.

---

## 7. Agent-expertise sweep via Gemini, cross-verified (fifth sweep, 2026-08-03)

The founder ran our authored deep-research prompt through Gemini (doc on file); this
section is the Fable verification-and-integration pass over its results. Headline: the
report named only real, well-known projects — and still contained three citation defects
and one license error, which is exactly why the verify pass exists:

**Corrections to Gemini's record (verified against GitHub 2026-08-03):**
- Instructor lives at `567-labs/instructor` (not jxnl/), MIT, active, 13.7k★.
- Outlines lives at `dottxt-ai/outlines` (not outlines-dev/), Apache, active, 15.5k★.
- The SKILL.md standard is `anthropics/skills` (166k★), not anthropics/courses.
- Wan2.2 flagged "HIGH RISK possibly non-commercial" — **wrong**: Apache-2.0, verified
  at source in sweep 1. (LTX-2's custom-but-commercial-OK license was already recorded.)

**Adopted:**
- `danielmiessler/Fabric` (MIT, 43k★, v1.4.447) — patterns corpus as a reference shelf;
  the creative department mines it for critique rubrics.
- `anthropics/skills` — the canonical SKILL.md reference for authoring studio skills.
- **The pattern layer, built in-repo** (Gemini's best content was patterns, not tools):
  `studio/rubrics/creative-constitution.md` (8 articles + a bounded Self-Refine loop
  contract for critique-and-revise) and `studio/rubrics/style-rules.yaml` +
  `scripts/studio/style_gate.py` — the mechanical banned-cliché/AI-tell checker with a
  selftest. Its five "techniques without tools" all validate practices this platform
  already runs (file-based Ralph memory, two-source verification, error-injected
  retries, mechanical pre-render QC) — independent confirmation, recorded as such.

**Declined, with reasons (doctrine over fashion):**
- LangGraph as "the structural backbone" — our backbone is Claude Code subagents +
  file handoffs + bounded ralph loops, chosen deliberately; adopting a second
  orchestrator repeats the ViMax decision. Catalogued for a future standalone service.
- Mem0 / managed memory layers — file-based memory IS the studio's doctrine, and
  Gemini's own techniques section endorses exactly that. No.
- Instructor/Pydantic/DSPy as runtime deps — our agents are Claude Code (schema
  enforcement already happens at the tool-call layer and in manifest validators); the
  *pattern* (schema + bounded retry at every boundary) is adopted, the libraries wait
  for a component that makes raw LLM API calls.
- Outlines — GPU-phase constrained decoding for locally hosted LLMs; catalogued until
  a local LLM exists.
- Promptfoo / DeepEval — the honest "next infrastructure" for prompt-regression CI;
  catalogued with a trigger: adopt when agent charters change often enough that manual
  review misses regressions (e.g., at a second production channel).
- CrewAI / MetaGPT / AutoGPT / BabyAGI / ChatDev — agreed with Gemini's own
  catalog/decline calls; recorded so no future sweep re-litigates them.

---

## 8. The missing-roles sweep: Netflix/Pixar/Disney org charts vs the roster (sixth sweep, 2026-08-04)

Three parallel researchers: the Pixar/Disney/DreamWorks feature pipeline (24 roles, from
studio job postings and Animation Guild classifications), Netflix + creator-studio roles
(17 roles, from the Netflix Tech Blog, Partner Help specs, and the MrBeast onboarding
doc), and live GitHub verification of tools for the candidate chairs (17 repos, licenses
read from source).

**Net assessment:** the 23-agent roster mapped the studio org well — editorial's design
(film-editor + continuity-supervisor) matches how feature animation actually staffs
continuity, growth-analyst is "genuinely MrBeast-grade", and compliance-officer is a
properly S&P-shaped gate. Four chairs were real gaps; all four are now staffed:

| New agent | Studio precedent | Tools adopted |
|---|---|---|
| line-producer | Pixar PM/line producer — "the most real gap in the roster" | file ledgers now; cgwire/gazu (LGPL, pip) installed as the Kitsu/Zou bridge |
| colorist | Netflix color-managed DI mandate; grade mismatch = the AI tell | OpenColorIO (BSD-3, pip) + colour-science (BSD-3, pip) |
| localization-director | Netflix Timed Text guides; MrBeast dubbed channels | argos-translate (MIT, pip, CTranslate2 CPU) + whisperX (already ours) |
| key-art-director | Netflix AVA artwork pipeline; thumbnail-half-the-video culture | OpenImageIO (Apache, pip); dedicated thumbnail repos surveyed and SKIPPED (nothing worth vendoring) |

Plus beets (MIT, pip) as sound-designer's music-supervision backbone (cue-sheet ledger).

**Folded, not staffed** (recorded so no future sweep re-litigates): story supervisor →
story-showrunner; story artist + virtual DP → previs-director (cinematography bible
amendment); character designer/casting → gen-supervisor (casting-sheet amendment);
animatic-first editorial → film-editor amendment; music supervision → sound-designer
amendment; per-title encode recipes + VMAF gate → render-wrangler/post-supervisor duty;
production coordinator → line-producer (two management agents for one founder is
over-staffing). **Correctly missing, do not staff:** character TDs/rigging, FX TDs,
lighting TDs (no rig, no sim, no 3D lighting stage exists — revisit only with a Blender
render stage), and the gaffer — the canary role: any proposed agent whose whole job is
applying another agent's spec with no judgment of its own is a checklist, not a seat.

**Catalogued with triggers:** cgwire/kitsu + cgwire/zou (AGPL, fine internally) when a
human team joins; ynput/AYON declined for now (FSL-1.1 backend — not OSI open source
until its 2-year conversion — and aimed at multi-DCC studios); OpenRV (mature) over
xStudio if a desktop dailies player is ever wanted; usd-core (pip) when a 3D
layout/sets role appears; libplacebo at GPU phase for HDR/tone-map finishing;
ComfyUI_IPAdapter_plus (GPL — isolate inside ComfyUI runtime; maintainer-hiatus, pin a
commit) for character identity at GPU phase; Freesound API client when a CC-vetting
policy exists; Helsinki-NLP/Opus-MT credited as Argos's model source and fallback.

---

## 9. The 3D lane: from "correctly missing" to live (seventh sweep, 2026-08-04)

Founder direction: don't exclude 3D. §8's "no 3D stage exists" was a self-fulfilling
verdict — the stage didn't exist because nothing had built it. Two research agents (one
running EMPIRICAL tests on this host, one auditing Blender Studio's shipped pipeline)
plus an internal audit of prior dev closed it:

**Audit of previous dev:** 3D was doctrine-present, mechanically absent — Blender named
in five charters, blender-mcp/Flamenco/usd-core catalogued, but the `blender` module was
desktop-only/disabled and nothing 3D was installed or proven.

**Now live (verified by running it):**
- `blender-headless` (pip bpy wheel, GPL) — full Blender headless; Cycles CPU renders
  confirmed on this host (~20–25s/frame at 720p stylized); Rigify generates production
  rigs headless (empirically: 159-bone human metarig → rig in 4.5s, no display).
- `usd-core` (Pixar, TOST-1.0 permissive) — USD authoring verified; no GPU imaging in
  the wheel (UsdImagingGL ImportError confirmed — that's expected and fine).
- **LIGHTHOUSE**: first true-3D production — 15s, 3 shots, fully procedural Cycles film.
- Version intelligence: cp311 wheels live on the bpy 4.5 LTS line (monthly releases);
  5.1+ is cp313-only. We run 5.0.1/cp311 (proven); revisit at python upgrade.
- Blender 5 API breaks handled in production: NISHITA→MULTIPLE_SCATTERING sky, slotted
  actions (Action.fcurves gone), EEVEE blend_method removed, no ffmpeg encoder in the
  pip wheel (PNG frames + vendored ffmpeg assembly — the farm shape anyway).

**Engine ruling (decide-now, verified):** EEVEE — including EEVEE-Next — is a GPU
rasterizer (GL 4.3+/Vulkan required) and cannot render on this host. Cycles CPU with
bounded samples + OpenImageDenoise is the committed final-frame engine; EEVEE previews
are a future Flamenco GPU-worker job.

**Catalogued with triggers (all verified active, licenses read):**
- Flamenco (Blender Studio, GPL-3.0, Go manager+worker, v3.9.3, single-machine
  supported) — adopt when renders outgrow render_all.sh's resumable-runner pattern.
- CloudRig (studio rigger-maintained, GPL, tracks Blender 5.0 with a 4.5 tag) — first
  component-rigged character project. Rigify meanwhile ships inside bpy: adopted.
- blender-studio-tools (GPL): blender_kitsu, asset_pipeline, naming/folder conventions
  (copy the docs verbatim when the 3D lane scales), lighting_overrider.
- Storypencil: alive but thin bus factor — treat boards as GP3 scenes + VSE conventions
  scripted directly; Storypencil is optional human convenience.
- Grease Pencil 3: the 2D-in-3D system (geometry-nodes capable) — adopt for hybrid
  2D/3D formats when one appears.
- ahujasid/blender-mcp (MIT, active) — the agent-drives-desktop-Blender seam for
  human+agent co-authoring sessions.
- Poly Haven API (assets CC0, keyless, verified reachable) — the house 3D asset source.
  Objaverse (ODC-By dataset, per-object licenses) and Sketchfab (CC filterable, token
  for downloads) require per-object vetting — catalogued behind license policy.
- glTF-Validator (Khronos, Apache) — asset QC CLI when external models enter scenes.
- colmap (BSD-3): sparse SfM is CPU-viable today; dense reconstruction at GPU phase.
  Meshroom: CUDA-gated full pipeline → desktop/GPU catalog.
- GPU-phase generation: TRELLIS (MIT, 16GB — audit two vendored submodule licenses at
  adoption), TripoSR (MIT, 6GB), UniRig (MIT, 8GB auto-rig). shap-e: dormant, SKIP.

**Roles:** one consolidated `3d-supervisor` chair (layout+lighting+rigging+sets
policy) — Blender Studio's ~10-artist open movies show which TD chairs carry judgment
at small scale; the split TD roles arrive with the GPU farm, if ever. §8's gaffer-canary
rule applied to 3D: farm execution stays render-wrangler's checklist, not a new seat.
