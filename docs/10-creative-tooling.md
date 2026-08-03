# 10 — Creative Tooling Evaluation

> Nine tools the founder suggested as creativity boosters, each verified against its actual
> GitHub/product page on 2026-08-03. Constraints applied: this container has **no GPU and
> 4 CPU cores**, the channel runs a **$0 production model**, and **Rule 6**
> (docs/05-compliance.md) bans generated *photoreal* material in the archive layer while
> permitting generated *abstract/graphic* support motion (kinetic type, animated charts,
> stylised transitions) as designed support.

## Verdicts

| Founder's name | Actual project | What it is | License | Needs | Verdict |
|---|---|---|---|---|---|
| "open Higgsfield ai" | [sunnychase/open-higgsfield-ai](https://github.com/sunnychase/open-higgsfield-ai) | Self-hosted web frontend replicating Higgsfield's image "cinema studio"; routes generation to 20+ hosted models | MIT (frontend) | Muapi.ai API key — **paid credits**; no local GPU | **LATER** — needs Muapi credits; and it makes *photoreal* images, which Rule 6 bans in the archive layer anyway. (Note: `higgsfield-ai/higgsfield` on GitHub is an unrelated multi-GPU LLM-training framework — not this.) |
| "ltx2.5" | [Lightricks/LTX-2](https://github.com/Lightricks/LTX-2) (no "2.5" found; a Lightricks/LTX-2.3 model page exists on Hugging Face) | Open-weights audio+video generative model (22B), official inference + LoRA trainer | LTX-2 Community License Agreement (repo LICENSE, dated 2026-01-05) — *not* plain Apache | ~24 GB VRAM min (quantized), 48 GB+ for 4K; CUDA GPU | **LATER** — needs a rented GPU (≥24 GB VRAM). Usable then only for abstract/stylised support motion, never archive-layer footage. |
| "comfy ui" | [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI) | Node-graph engine for diffusion workflows (image/video/audio) | GPL-3.0 | GPU for practical use; `--cpu` mode exists but README calls it "(slow)" — diffusion on 4 cores is not production-viable | **LATER** — technically installs today at $0, but real throughput needs a GPU machine. The natural host for Wan/LTX when one exists. |
| "wan video" | [Wan-Video/Wan2.2](https://github.com/Wan-Video/Wan2.2) | Alibaba's open MoE video model (T2V/I2V; TI2V-5B runs "on a GPU with at least 24GB VRAM (e.g, RTX 4090)") | Apache 2.0 | ≥24 GB VRAM consumer GPU | **LATER** — $0 in licenses, blocked on hardware. Same Rule 6 boundary as LTX-2. |
| "pinokio" | [pinokiocomputer/pinokio](https://github.com/pinokiocomputer/pinokio) | Electron desktop "1-click launcher" that installs/runs open-source AI apps via vetted scripts | MIT | A desktop OS with GUI; the apps it launches mostly need GPUs | **LATER** — the launcher is free, but it's a desktop GUI app and this container is headless; its payload apps are the GPU tools above. Belongs on the founder's own machine, not in the pipeline. |
| "drama claw" | [dramaclaw/dramaclaw](https://github.com/dramaclaw/dramaclaw) | Script-to-finished-film AIGC pipeline (dramas, ads, product video); all inference via a remote OpenAI-compatible gateway | Elastic License 2.0 (no reselling as hosted service) | DC key from its gateway or bring-your-own model endpoint — **paid API inference**; no local GPU (2 vCPU/4GB ok) | **LATER** — runs on this box, but every frame it makes costs gateway credits, and its output is narrative/photoreal-leaning video: off-format and Rule 6-risky for us. |
| "toon flow" | [HBAI-Ltd/Toonflow-app](https://github.com/HBAI-Ltd/Toonflow-app) | Open-source novel/script → animated short-drama orchestrator (AI scriptwriting, storyboarding, character + video gen), all via remote model APIs | Apache-2.0 with supplementary commercial terms (internal use ≤5 entities free) | LLM + image-gen + video-gen API keys (Claude/GPT, "Nano Banana Pro", Sora-class video) — **paid**; Node 23+, Docker | **LATER** — orchestrator is free and CPU-friendly, but the generation it orchestrates is all metered third-party APIs. Stylised-animation output could pass Rule 6 as designed support if we ever fund it. |
| "video-shotcraft" | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | Agent skill for Claude Code/Codex: cinematic motion-design videos via Remotion — 100+ shot recipe cards, 161 motion previews, production template; renders locally with Node + headless Chrome | Apache-2.0 | Node 22, Remotion, chrome-headless-shell; **no GPU, no API keys, no cloud**; docs cover low-core/headless CI (concurrency 1) | **ADOPT-NOW** — $0, CPU-only, built for exactly the Rule 6-legitimate layer: kinetic type, chart moves, stylised transitions as code. |
| "vox director" | [Alisa0808/vox-director](https://github.com/Alisa0808/vox-director) | Agent skill: one topic → finished Vox-style paper-collage explainer (script, collage keyframes, motion, VO, music, captions) via Atlas Cloud API + local ffmpeg | MIT | **Atlas Cloud API key (paid)**; Python 3 + Pillow, ffmpeg/ffprobe | **LATER** — the skill is free and its collage aesthetic is squarely "designed support," but every keyframe/voice/music call bills Atlas Cloud credits. Worth a look if a credit budget ever opens. |

**Not found as named:** nothing was a total miss, but two names were imprecise: there is no
"LTX 2.5" (the fetched pages show LTX-2, with an LTX-2.3 successor listed on Hugging Face), and
"open Higgsfield ai" resolves to a community MIT clone of Higgsfield's UI, not an official
open-source Higgsfield generator.

## Recommendation

**Adopt video-shotcraft now; treat everything else as a parked list.** It is the only tool of
the nine that clears all three of our gates simultaneously: it costs nothing (Apache-2.0, no API
keys, no credits), it runs on this exact container (Node + Remotion + chrome-headless-shell, with
documented low-core headless settings), and it lives entirely on the legal side of Rule 6 — it
produces *designed* motion (typographic shots, camera moves over real captures, beat-synced
transitions) rather than synthesised footage. Concretely, its shot-recipe vocabulary is a direct
upgrade path for our price-reveal frames, citation chips, and chart animations: same evidence,
better choreography. The one caution is aesthetic, not compliance: its default "product promo"
gloss should be tuned to the bible's archival look, and anything it renders still goes through the
normal gate like every other frame.

The remaining eight all fail on money or hardware, and the generative-video cluster fails on
purpose as well. LTX-2, Wan2.2, and ComfyUI form a coherent *future* stack — Apache-2.0 Wan2.2 on
ComfyUI is the obvious first experiment the day we have a ≥24 GB-VRAM machine — but even then Rule
6 confines them to abstract/stylised support motion; they must never touch the archive layer, and
photoreal output has no home on this channel at any budget. DramaClaw, Toonflow, vox-director, and
open-higgsfield-ai are "free software, metered inference": each would quietly convert the $0 model
into an API bill, so they stay parked until there is a deliberate credit budget — and the same
discipline already applies to the connected Higgsfield MCP, which bills per generation. If the
founder wants one of these for personal experimentation, Pinokio on their own desktop is the right
sandbox; the production repo stays $0 and evidence-real.
