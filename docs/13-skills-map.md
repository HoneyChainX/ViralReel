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
