# 13 — The Skills Map

The claude.ai skill bank attached to this studio's sessions holds **215 skills** (the
NVIDIA professional packs plus Anthropic's creative/document suites). This registry
maps every one to the studio — owner, phase, trigger — with the same discipline as the
module manifest: a skill is integrated when a department owns it, not when it exists.
Full categorization: eighth sweep, 2026-08-05 (one exhaustive pass, all 215 accounted).

## In-repo studio skills (ours, versioned here)

The studio's own workflows are packaged as project skills in `.claude/skills/` —
institutional knowledge as code:

| Skill | Wraps | Owning charter |
|---|---|---|
| `/film-assembly` | film manifest → conform → QC → mux | film-editor |
| `/seamless-chain` | frame-handoff contract → verify → stitch → seam QC | continuity-supervisor |
| `/studio-platform` | manifest ops, doctor, pins, install doctrine | pipeline-td |

Authored against the SKILL.md standard (`vendor/anthropics-skills` is the reference
corpus). pipeline-td owns this directory; new studio workflows that survive two
productions get packaged the same way (skill-creator assists).

## Adopted now — bank skills with a working owner (18)

CPU-only, no GPU infra, each mapped to one agent's charter:

| Skill | Owner | Use |
|---|---|---|
| canvas-design | key-art-director | thumbnails, film posters, key art as finished PNG/PDF |
| theme-factory | brand-designer | per-channel palette/type theme systems |
| brand-guidelines | brand-designer | worked template for encoding each show's brand as a forkable skill |
| algorithmic-art | motion-director | seeded p5.js generative motion beds under Remotion comps |
| slack-gif-creator | motion-director | quick looping GIF previs of hook/title animations |
| dataviz | motion-director | on-screen price-history charts legible at Shorts resolution |
| web-artifacts-builder | growth-analyst | interactive retention/CTR dashboards as artifacts |
| docx | line-producer | production paperwork (memos, licenses, releases) |
| xlsx | line-producer | budget/schedule/pipeline trackers |
| morning | line-producer | recurring weekday studio-standup brief |
| pptx | monetization-lead | sponsor media kits and pitch decks |
| pdf | archive-sourcer | text/table extraction from scanned catalogs and price lists |
| doc-coauthoring | story-showrunner | series bibles and treatments via structured co-authoring |
| internal-comms | strategy-lead | status updates, greenlight memos, post-mortems |
| skill-creator | pipeline-td | package studio conventions as skills for the other 27 agents |
| mcp-builder | pipeline-td | wrap studio tooling as MCP servers (the catalogued MCP seam) |
| data-designer | hook-writer | structured variant datasets for systematic hook A/B testing |
| nemotron-policy-generator | compliance-officer | author the content-safety policy taxonomy (pure CPU text output) — guardrail prompts ready if a safety model is ever hosted |

## GPU / cloud phase — real owners, explicit triggers (19 skills in 5 entries)

| Skill family | Owner | Trigger |
|---|---|---|
| vss-* (15) | post-supervisor | GPU host online AND the dailies/footage library outgrows manual review — VLM search, summarization, Q&A over rendered episodes |
| nemotron-speech (Riva ASR/TTS/NMT) | localization-director | localization needs NMT + multilingual TTS beyond whisperX/Kokoro's coverage |
| nemo-retriever | archive-sourcer | research corpus outgrows local pdf/grep extraction |
| tao-finetune-cosmos-embed | archive-sourcer | clip library needs embedding-based dedup/semantic retrieval on the 24GB host |
| tao-generate-video-reasoning-annotations | archive-sourcer | building the reasoning-annotated index behind that retrieval |

## Declined — 14 families, ~178 skills, with reasons (recorded so no sweep re-litigates)

| Family | Count | Reason |
|---|---|---|
| mcore-*/nemo-mbridge-*/nemo-automodel-*/nemo-rl-*/launch-nemo-rl/nemotron-customize/nemotron-retrieval-recipes/nemo-evaluator-plugin | 37 | LLM training/RL infra for GPU clusters; the studio consumes hosted models, never trains its own |
| tao-* training/platform (except the 2 above) | 50 | CV model training + launcher scaffolding; the studio makes videos, not vision models |
| jetson-* | 33 | a 24GB GPU points to a discrete x86 workstation (ComfyUI/Blender), not a Jetson Thor; BSP/pinmux work is embedded engineering — revisit only jetson-llm-serve if a Thor is actually purchased |
| cuopt-* | 11 | gaffer-canary for tools: render scheduling on one host is a priority queue, not a MILP |
| holoscan-*/hsb-* | 10 | medical/sensor edge hardware the studio doesn't own (hsb-* are the newest arrivals — same verdict) |
| dicom-*/digital-health-*/nv-generate-ct-rflow | 8 | medical imaging/clinical ASR — outside the domain |
| earth2studio-* | 7 | weather forecasting — no charter maps |
| tilegym-* | 7 | custom CUDA kernels — nothing in the stack needs them |
| deepstream-* | 5 | real-time RTSP/Kafka analytics; our processing is offline batch, and GPU-phase video understanding is vss-*'s lane |
| cupynumeric-* | 4 | HPC array compute — no such workloads |
| dynamo-* | 4 | K8s LLM inference serving — no cluster exists or is planned |
| dali-dynamic-mode | 1 | training data loading — no training |
| nemo-data-designer-plugin | 1 | exact duplicate of adopted data-designer; both = routing ambiguity |
| nemoclaw-user-guide | 1 | docs pointer for an unrelated product |

## Doctrine

Skills follow module rules: adopted means an agent's charter can name it; declined
means a recorded reason, not silence; GPU-phase means a trigger, not a vibe. The
duplicate rule (data-designer) and the canary rule (cuopt) apply to skills exactly as
they apply to seats and modules.

---

## Ninth sweep (2026-08-05): the creative-production wave — 188 repo-vendored skills

The founder installed 11 skill packs via the skills CLI; they now live **in-repo** at
`.agents/skills/` (with `.claude/skills/` symlinks), versioned like our own three studio
skills — every future session loads them natively. 31 MB of markdown, invocable as
`/<name>`.

### Adopted into lanes (free to run, CPU-fine)

| Pack | Skills | Owner | Why it matters here |
|---|---|---|---|
| **Remotion official** (remotion-dev/skills) | 12 | motion-director | docs-grade skills for our primary render engine — best-practices, create, render, captions (that one also serves localization-director), multimedia, upgrade |
| **Three.js** (cloudai-x) | 10 | 3d-supervisor + motion-director | a SECOND 3D path: three.js inside Remotion (@remotion/three) renders browser-3D on CPU via headless Chromium — complements the bpy/Cycles lane |
| **GSAP official** (greensock) | 8 | motion-director | timeline/easing craft; also HyperFrames' default runtime |
| **HyperFrames** (heygen-com) | 25 | motion-director + film-editor | an entire second production lane: HTML/GSAP compositions with a local CLI (init/lint/preview/render). Its motion-doctrine ("a multi-scene video should feel like ONE continuous camera move", the Seam Gate, the ban on idle wobble) independently converges on our chaining/continuity philosophy — continuity-supervisor should read it. embedded-captions + talking-head-recut serve localization-director/post-supervisor |
| **Genjutsu** (AThevon) | 2 + 15 internal | brand-designer / key-art-director / motion-director | creative-coding orchestrators (/cast for motion, /paint for graphics); sub-skills load automatically, never invoked directly |
| **design-dna** (zanwei) | 1 | brand-designer | reference images/URLs → structured design-profile JSON → generation from profile |
| **motion-design** (lottiefiles) | 1 | motion-director | motion principles + Lottie assets in Remotion |
| **visual-skills** (smixs) | 2 | gen-supervisor | image/video prompt craft reference |

### Paid-generation fleets — installed, founder-gated (D8: paid is per-project, never default)

| Pack | Skills | Notes |
|---|---|---|
| **Pexo** (pexoai) | 20 | cloud AI-video service (Seedance/Kling/Veo/Sora routing). EXCEPTION adopted free: seedance-2.0-prompter + veo-3.2-prompter are prompt-craft knowledge → gen-supervisor's reference shelf |
| **Higgsfield** (higgsfield-ai) | 9 | paid credits (MCP connected). Aligned pairs worth noting when a project buys in: soul-id ↔ gen-supervisor's casting sheets, higgsfield-youtube-thumbnail ↔ key-art-director's lab |
| **inference.sh** (inference-sh) | 86 | the pack is far larger than its listing — a full cloud-model CLI (FLUX/Veo/GPT-Image/ElevenLabs/music/avatar). Execution skills are founder-gated; the ~20 knowledge-only skills ride free (storyboard-creation → previs-director, youtube-thumbnail-design + og-image-design → key-art-director, character-design-sheet → gen-supervisor, video-ad-specs + prompt-engineering → gen-supervisor, logo-design-guide → brand-designer, data-visualization → motion-director) |

### Honesty notes

- **License hygiene is thin**: only one pack ships a LICENSE file at skill depth. These
  are published instruction repos and we use them as instructions (low risk), but the
  gap is recorded — pipeline-td checks licenses before any pack's code/assets (not just
  prose) enters a deliverable.
- **Duplicate-routing risk**: the wave brings overlaps (ai-podcast vs ai-podcast-creation,
  data-visualization vs the environment dataviz skill, three caption skills across
  packs). Owners disambiguate: the lane's charter names which skill wins per task.
- **Provenance law unchanged**: none of the generation fleets touch Price Archaeology's
  archival layer; the gate outranks every skill, and generated imagery in thumbnails
  stays banned for archival-evidence episodes.

---

## Tenth sweep (2026-08-05): the "Adobe/Disney/NVIDIA skills" verification pass

The founder supplied a listicle of seven named skills (Palmier Pro Timeline Editor,
Smart Silence Remover, Automated Color Finish Agent, Disney 12 Principles Guide, USD
Orchestrator, RTX Spark Compute Router, Render Farm Cost Optimizer) sourced from
aggregator articles. Verification against the skills registry — the same discipline
that caught SEO-fabricated model releases in sweep 4 — found the exact names mostly
fictional or unvetted, but REAL equivalents exist for every genuine capability:

| Listicle claim | Verdict | What we actually integrated |
|---|---|---|
| "Palmier Pro Timeline Editor" | exists as a 1-install personal-repo clone — SKIPPED (supply-chain hygiene; skills run with full agent permissions) | `premiere-pro-mcp` (412 installs) + `flue@premiere`/`@adobe` (1.8K — shell→ExtendScript control of Adobe apps, no MCP server needed) → film-editor/post-supervisor at DESKTOP phase; our OTIO layer remains the timeline interchange |
| "Smart Silence Remover" | capability ALREADY OURS since sweep 1 (auto-editor, vendored+pinned) | added `auto-editor-export` — from auto-editor's own author — exporting cuts to Premiere/Resolve/FCP timelines; plus `raw-video-processing` (2.8K installs, ffmpeg silence-cut) |
| "Automated Color Finish Agent" | capability ALREADY OURS (colorist chair, sweep 6: OCIO + colour-science + lut3d) | added `ffmpeg-color-grading-chromakey` (CPU, colorist's implementation grammar) + `video-color-grading` (each::sense AI — PAID, founder-gated per D8) |
| "Disney 12 Principles Guide" | registry copy failed to install (1.3M-file host repo hit disk) — and one page of doctrine shouldn't cost a giant dependency | AUTHORED in-repo: `/animation-principles` — the twelve as a diagnostic review rubric wired to the creative constitution's critique contract → animation-director |
| "USD Orchestrator" | no such skill; capability partially ours (usd-core, sweep 7) | added `omniverse-usd-performance-tuning` (NVIDIA official, 1.9K installs) → 3d-supervisor; isaac-sim USD skills noted robotics-only, catalogued |
| "RTX Spark / Blackwell Compute Router" | FICTION as an installable skill (registry: crypto/CAD noise) | the described capability IS render-wrangler's charter (VRAM budgeting by arithmetic) — activates with the GPU host, no skill needed |
| "Render Farm Cost Optimizer" | FICTION as an installable skill | capability = our bounded-chunk runner's frame-time logs + Flamenco (catalogued, sweep 7); a log-analyzer script joins render-wrangler's backlog when farm scale exists |

Security note: all newly installed packs grep-scanned for exec/exfil patterns (clean);
the skip-on-1-install rule and read-before-trust discipline are now precedent.

---

## Eleventh sweep (2026-08-05): the "Agentic Council" listicle — deep-dive verification

Second founder-supplied listicle, same genre as the tenth. Most of it re-describes what
this platform already runs — the "Agentic Council" (creative-director/DOP/technical-
director agents) IS the 28-agent roster with sharper charters; "Open Montage" has been
the vendored production backbone since sweep 1; the Palmier/12-principles/RTX/
Threadripper items carry tenth-sweep verdicts. The four NEW checkable claims, verified
at source:

| Claim | Verdict |
|---|---|
| JossBen/mcp-video-editing-assistant | REAL but embryonic (MIT, 2 commits, 1★, Resolve 17+ behavior-tracking MCP) — skip-on-1-install precedent applies; the mature Resolve path remains Resolve's own Python scripting API at desktop phase |
| digitalsamba/claude-code-video-toolkit | REAL AND ADOPTED (MIT, 1.9k★, active): a sibling platform that independently converged on our architecture (Remotion + LTX + ACE-Step + skills). Vendored as `cc-video-toolkit` reference module. Its Modal cloud-GPU path (~$0.23/clip) is a founder-gated option to activate the genai lane BEFORE local GPU hardware — recorded, not enabled (D8) |
| Sonix Transcription MCP | real product, paid SaaS — skipped; whisperX covers transcription at $0 |
| Montreal Forced Aligner | REAL (MIT, Kaldi-based, conda, CPU, 900+ commits, active) — CATALOGUED with trigger: adopt when phoneme-grade alignment is needed (lip-sync for dubbing, animation mouth-shapes) beyond whisperX's word-level timing → localization-director/animation-director |

"Dynamic Light-Rig Scripter" (Hydra): no such skill exists; the capability is bpy
lighting scripting, already 3d-supervisor's lane. A USD broken-reference auditor script
(pxr-based) joins 3d-supervisor's backlog — small, real, buildable on usd-core.

---

## Twelfth sweep (2026-08-05): character bibles + the Netflix Vera/VOID verification

Third founder-supplied playbook. Verdicts:

**Adopted and built — `/character-bible`** (in-repo skill #6): the structured
asset-seed pattern is genuinely good prompt engineering and is exactly the operational
form of gen-supervisor's casting-sheet charter (sweep 6 amendment). Now packaged:
permanent CHARACTER_IDs, JSON casting sheets under `studio/casting/` with canon-phrase
locking (micro-details as drift anchors), the 5-part scene-composer frame, and spatial
separation + shared-anchor for multi-character shots (anti prompt-bleeding, two-character
ceiling with cut-around guidance). Locks at previs like voice IDs; chains inherit it.

**Verified REAL — Netflix's pair, catalogued with triggers:**
- **VOID** (Video Object & Interaction Deletion): open-sourced 2026-04, Apache-2.0,
  netflix/void-model on HF — physics-aware object removal on CogVideoX, using SAM2
  (already vendored) for segmentation; beat Runway 64.8% vs 18.4% in preference study.
  Trigger: GPU host + a real removal need; ~40GB VRAM raw means FP8/offload work on a
  24GB card → render-wrangler + film-editor. The listicle's Python API sample remains
  unverified paste — integrate from the actual repo docs, not the article.
- **Vera** (layered diffusion, content-preserving edits — edit layer + alpha matte,
  MoT architecture): research + papers published 2026-06, no released weights found.
  Watchlist: if weights ship, it's the surgical-edit tool for film-editor's lane.

**Recycled/fluff, already covered**: Agentic Council (the roster), MFA + Sonix (sweep
11 verdicts), "SSS locks"/"Kelvin templates" (colorist + cinematography bible),
"taste vectors" (creative constitution + growth-analyst), "sonic identity" (sound-
designer's charter), montage/pacing agents (film-editor + conform).

---

## Thirteenth sweep (2026-08-05): Google/OpenAI/Netflix ecosystem listicle — verified

**Mechanically actionable finding:** Netflix **VMAF is already inside our vendored
ffmpeg** (`libvmaf` filter confirmed present) — post-supervisor's sweep-6 encode-QC duty
(per-format encode recipe + minimum VMAF score vs render master) is now activatable
with zero installs.

**Verified real, catalogued with gates:**
- **google-marketing-solutions/gen-v** (official, Apache, active): Veo ad-video toolkit —
  Vertex-billed, founder-gated; key-art/marketing lane reference if a Google-stack
  project ever appears.
- **nolanx-ai/nolanx.ai** (MIT, 1.6k★, young): "agentic director" stretching short-clip
  generators to 5–60 min films over paid APIs (OpenRouter/FAL/ReelMind) — architecture
  overlaps our chains+film-editor stack; reference-read for continuity-supervisor,
  usage founder-gated.
- **0xsline/StoryGen-Atelier** (real; Gemini+Veo+ffmpeg): its "Interpolation Chain"
  (sliding-window adjacent-shot pairs) is an independent convergence on our
  keyframe-first FLF2V chain strategy — third external validation of the chaining
  doctrine. Vertex-billed, catalog.
- **anil-matcha/open-generative-ai** (MIT, 25.7k★): hybrid local(sd.cpp)/cloud(Muapi)
  generation studio — CAUTION: "no content filters" philosophy conflicts with the
  gate doctrine; if ever touched, it is founder-gated AND compliance-reviewed per use.
- **hpcaitech/Open-Sora** (Apache): the open Sora-replication line — genai GPU-phase
  catalog beside LTX-2/Wan.
- **Google ADK + A2A protocol** (real, open): ADK gets the LangGraph precedent — no
  second orchestrator, catalogued; A2A watchlisted as the cross-vendor interop seam if
  this studio ever federates with external agents. Google-hosted MCP servers: real,
  Google-Cloud-tenant infra we don't run.

**Covered by existing charters:** YouTube transcript/SEO/watchdog skills (seo-packager,
trend-archaeologist, growth-analyst + the morning brief); skill.md spec (our standard
since sweep 8); SoraWebui (UI over a paid API we don't hold). **Correction recorded:**
Manus is a proprietary product, not open-source — listicle error.

---

## Fourteenth sweep (2026-08-05): CPU-generation listicle — the one that fits the doctrine

This batch targets our exact constraint ($0, CPU-first). Verified at source:

| Item | Verdict |
|---|---|
| **rupeshs/fastsdcpu** (MIT, 2.1k★, active Jul 2026) | **ADOPTED** as the genai lane's first CPU-native engine: LCM/SDXS OpenVINO int8 images in seconds-to-a-minute on this 4-core host → gen-supervisor (concept stills, casting-sheet references) + key-art-director (art elements). Honesty: FLUX-int4 needs ~30GB RAM; this host has 15GB — LCM/SDXS is the lane, FLUX is not |
| **pierotofy/OpenSplat** (AGPL, 2.1k★) | REAL, truly CPU-capable (~100x slower — fine for small offline jobs, same economics as our Cycles renders). CATALOGUED with trigger: first project needing real-location 3D capture; pairs with colmap's CPU-viable sparse SfM (already catalogued) → 3d-supervisor |
| MrSecant/diff-gaussian-rasterization + Numba-JIT paper | niche research forks — recorded as the 3DGS-on-CPU evidence base, no adoption |
| vladmandic/sdnext | real and large, but redundant: a second webui when ComfyUI is already vendored (and has its own --cpu flag) — the duplicate-routing rule applies |
| freddyjose/ComfyUI-CPU | redundant fork — official ComfyUI --cpu covers it |
| "GGUF video generation on CPU" (Wan2GP etc.) | OVERSTATED: Wan2GP targets low-VRAM GPUs, not no-GPU; CPU video diffusion runs minutes per frame — the video-generation-is-GPU-phase verdict stands |

---

## Fifteenth sweep (2026-08-06): Gemini "AI-native studio" batch

Mostly re-treads of sweeps 11-14 (digitalsamba toolkit already vendored — the batch's
"Fixie-AI/digisamba" attribution is garbled; NolanX and the 1-star JossBen MCP carry
sweep-11/13 verdicts — this batch inflates JossBen to "the official MCP bridge", which
it is not; OpenSplat/FastSD adopted in sweep 14; the SKILL.md scaffolding advice
describes a structure this repo already exceeds with six authored skills). New verdicts:

| Item | Verdict |
|---|---|
| Fable "Showrunner/Showrunner" repo | NOT open-source — SHOW-1 is a research paper + the commercial showrunner.xyz platform; no code repo exists. Its script/director/asset multi-agent architecture is third-party validation of this roster's design. Correction recorded |
| PKU-YuanGroup/Open-Sora-Plan (Apache) | real, well-known — genai GPU catalog beside hpcaitech/Open-Sora (sweep 13) |
| Vchitect/Latte (Apache) | real video-DiT research lineage — catalog-note only; its "fine-tune your own model" pitch is off-doctrine (this studio consumes models, never trains) |
| suno-ai/bark (MIT) | real — CATALOGUED with trigger: nonverbal audio cues ([sighs], [laughs], throat-clears) for scripted character dialogue, the one niche Kokoro/VibeVoice don't cover → voice-director; CPU-slow but offline-job economics |

---

## Sixteenth sweep (2026-08-06): GPU scaling fleet → docs/14

Four-researcher workflow (gen-scaling tech, big-co speed blueprints, RunPod/build.nvidia
deployment, cost engineering) — full blueprint in **docs/14-gpu-scaling.md**. Headlines:
the 4090 day-1 speed stack (Lightning 4-step + LTX distilled FP8 + SageAttention2 +
TeaCache + cascaded upscale + RIFE) takes a 1-min film from ~1.8 GPU-hours to minutes
and ~$0.11-0.35; RunPod Secure pod + network volume is home base; two aggregator lies
caught (ParaAttention "open source" — actually no-hosted-service source-available;
NVFP4 "3x on any RTX" — Blackwell-only, docs/11 corrected); Self-Forcing's realtime
4090 weights open a previz lane; DGX Cloud/Brev/serverless declined with reasons.
