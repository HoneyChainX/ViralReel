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
