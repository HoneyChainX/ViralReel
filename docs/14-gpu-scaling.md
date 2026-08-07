# 14 — GPU Scaling Blueprint (sixteenth sweep, 2026-08-06)

Four-researcher fleet, everything verified at source (licenses read from LICENSE files;
two aggregator lies caught). This is the plan for the day a GPU host exists.

## A. The 4090 speed stack — day-1 order of operations

Assembly point: **kijai/ComfyUI-WanVideoWrapper** (Apache) — every lever below is a
toggle inside it. Pin commits per doctrine.

| Lever | Gain | Notes |
|---|---|---|
| lightx2v **Wan2.2-Lightning** 4-step LoRAs | ~20× (4 steps, no CFG) | THE default Wan fast path; verify LoRA repo license at adoption |
| **LTX distilled** 8-step + FP8 | ~6× vs base | ltxv-13b-distilled; LTX-2 22B via distilled+offload (Community License: fine under $10M revenue — re-check at scale) |
| **SageAttention2** (Apache, sm89 OK) | 2-5× attention | biggest post-distill win; known fp8_e4m3fn black-frame bug → use fp8_scaled weights |
| **TeaCache** (Apache, via kijai nodes) | 1.5-2× | full-step quality tier only (useless at 4 steps); tune threshold, verify last-frame fidelity in seam checks |
| FP8 quantized checkpoints | ~2×, −40% VRAM | Ada-native. **CORRECTION to docs/11 §6: the "3× NVFP4" claim is Blackwell-only — a 4090 has no FP4 tensor cores** |
| Generate ≤720p → **Real-ESRGAN** upscale | ~2-4× | MovieGen's cascaded doctrine, codified: never native-1080p diffuse on 24GB. SeedVR2-3B (Apache) trialed as premium upscaler |
| Low-fps gen + **RIFE** interpolation | ~1.5-2× | 16fps→24fps; MIT; works TODAY on CPU too. Seam-protection rule: interpolate inside segments, never across chain joins |
| **Nunchaku/SVDQuant** INT4 (stage 2) | 3× keyframes | image models only today — speeds the FLF2V keyframe lane; watch for video support |

**Declined with reasons:** ParaAttention (source-available with no-hosted-service clause
+ license keys — aggregators mislabel it open; TeaCache covers the capability),
FlashAttention-3 (Hopper-only, never runs on a 4090), xDiT (multi-GPU sequence
parallelism — our chain shape prefers embarrassingly-parallel segment fan-out),
Cosmos WFM (wrong domain, non-Apache weights).

**The realtime line landed:** Self-Forcing (Apache, NeurIPS spotlight) runs Wan-1.3B in
realtime ON A 4090 → stage-2 previz/draft lane (drafts of every segment before the slow
pass). Rolling Forcing's anti-drift attention sink maps directly onto our chain-drift
failure mode → trial (verify its license first). FastVideo/FastWan (Apache, >50×
sparse-distill claims, explicit 4090 support) is the candidate to replace the draft
tier entirely at stage 2.

## B. Where to run — verified pricing, honest verdicts

| Option | Price | Verdict |
|---|---|---|
| **RunPod Secure 4090 pod + 150-200GB network volume** | $0.69/hr + ~$10.50/mo | **ADOPT — home base.** Volume holds weights+nodes (~40-60GB); boot-to-first-frame in minutes. Caveat found: network volumes need Secure Cloud — the $0.34 community price can't mount them |
| Vast.ai interruptible 4090 | ~$0.13-0.31/hr | ADOPT as cheap-burst overflow — our per-clip checkpointing absorbs pauses; bid ~20% over floor |
| RunPod spot | ~$0.14-0.20/hr | TRIAL in chunk-runner (5s SIGTERM = lose at most one clip) |
| Modal free tier | $30/mo credits | ADOPT as zero-cost QC/audio lane (cc-video-toolkit recipes already vendored) |
| RunPod serverless | $1.10/hr flex | DECLINE for film renders (long stateful sessions ≠ request-shaped); revisit for future API products |
| NVIDIA Brev | A10/L4 classes | DECLINE — no 4090s, storage dies with instance |
| build.nvidia.com | NIM APIs + ~1000 free credits | DECLINE as host (API catalog, can't run our stack); free NIM key noted as spare LLM endpoint |
| DGX Cloud | enterprise contracts | DECLINE — a month of our renders costs less than one DGX hour-block. Question closed |
| Colab Pro / Kaggle | $9.99/mo / free | DECLINE / smoke-test lane only |

## C. Cost per 1-minute film (planning estimates — sprint-1 benchmarks replace these)

- Optimized stack on cheap 4090s: **$0.11–0.35 per film**
- Unoptimized baseline: $0.68–1.38 (Wan TI2V-5B's own claim: ~9 min per 5s 720p clip
  → ~1.8 GPU-hours per film before the stack)
- Steady state at projected output: **~$10–25/month** (batch-and-idle; always-on pod
  declined until >350 GPU-hr/mo demonstrated — founder gate recorded)

## D. Build backlog (the doc's actionable half — pipeline-td + render-wrangler)

1. `gpu-runpod` platform profile + bootstrap: official RunPod PyTorch/ComfyUI base
   image as Docker FROM (third-party mystery templates declined), then OUR manifest
   installer — the GPU host is a new profile, not a new system.
2. Volume layout: `/workspace/models` (shared store, symlinked via
   extra_model_paths.yaml), `/workspace/vendor`, `/workspace/out`.
3. Doctor GPU extensions: nvidia-smi identity, torch.cuda + bf16/fp8 sanity, weights
   present, one 5-frame smoke render — before any paid minute renders.
4. Chunk-runner `--gpu` backend: same resumable contract; spot-safe per-clip
   checkpoints; pod lifecycle (spin → render queue → sync → terminate) owned by the
   ralph harness.
5. Sprint-1 deliverable: the real benchmark table (per-engine s/clip and $/film on the
   actual card) replacing every estimate above.

Sources of record: per-finding evidence URLs live in the sweep-16 workflow journal;
key upstream claims re-verified at Lightricks/Wan/NVIDIA/RunPod/thu-ml/ali-vilab repos.

---

## E. The GPU tier ladder (sweep-16 addendum — the 4090 was the anchor, not the answer)

What each card class unlocks for THIS pipeline, with verified ballpark pricing:

| Tier | Cards | ~$/hr (cheapest verified) | What changes for us |
|---|---|---|---|
| 16GB | A4000/A4500, L4 | $0.17–0.35 (RunPod/Vast); L4 spot on GCP ~$0.20–0.28 | The split-lane engines: LTX distilled, SDXL keyframes, SAM2, MMAudio, ACE-Step, upscalers. Cheapest per-clip for everything except Wan-720p |
| 24GB | 4090, 3090, A5000, L4(24) | $0.13–0.69 | The blueprint's anchor: Wan TI2V-5B 720p + full stack (sections A-D). L4 is 24GB but ~1/3 a 4090's throughput — price it per-clip, not per-hour |
| 32GB | RTX 5090 (Blackwell) | ~$0.89–1.20 | **NVFP4 unlocks** — the real 3× path (docs/11 correction inverts back); FP4 tensor cores + headroom for A14B-offload |
| 48GB | L40S, RTX 6000 Ada, A6000, A40 | $0.79–1.20 | Often the best perf/$ for video DiT: Wan A14B with light offload, LTX-2 22B near-native, **VOID at FP8 becomes realistic**, LongLive comfortable |
| 80GB | A100, H100 | A100 spot ~$1.10 (GCP) / ~$1.6-2.6 market; H100 ~$1.99–3.35 market | VOID raw (40GB+), A14B native, FA3 (H100 only), lowest single-segment latency. Rent by the job, never idle |
| Multi-GPU | N× any | linear | xDiT re-enters for single-segment latency; but our chain shape prefers N cheap cards fanning out segments — no framework needed |

Doctrine: **rent the tier the job needs, not the biggest card** — the manifest's
per-engine VRAM table (cost sweep) is the router. A film might use a 16GB card for
keyframes/audio and a 24-48GB card for the video pass, sequentially.

## F. Brev (brev.nvidia.com) revisited — datacenter tiers, not 4090s

The earlier decline was 4090-scoped. As a **CSP broker** (AWS/GCP/Crusoe/Lambda/
Nebius/Hyperstack/Oracle under one CLI/UI, full VM control), Brev is legitimate for
the L40S/A100/H100 tiers: our stack installs unchanged (it's a normal VM). The tax:
**storage dies with the instance** — the 40-60GB weights cache re-downloads each
session unless we bake weights into a custom container image pushed to a registry
(one-time build, then Brev sessions boot warm). Verdict upgraded: **VIABLE for
datacenter-tier bursts and NVIDIA-ecosystem work (NIM containers, Launchables);
RunPod/Vast still win on price for consumer cards.** Pricing is pass-through — check
per-provider at deploy time.

## G. Google Cloud GPU instances — verified 2026 pricing, honest verdict

| Card | On-demand | Spot |
|---|---|---|
| L4 24GB | ~$0.70/hr | ~$0.20–0.28/hr |
| A100 40GB | ~$3.67/hr | ~$1.10/hr |
| A100 80GB | ~$5.07/hr | — |
| H100 80GB | ~$10.98/hr | ~$3.69/hr |

Plus VM cost, persistent disk (~$0.17/GB/mo — real persistence, unlike Brev), egress
fees, and GPU quota-approval friction. **Verdict: GCP is 3-10× marketplace prices on
big cards — DECLINE for routine renders. Two real niches: (1) L4 SPOT for the 16GB
split-lane at enterprise reliability, (2) A100-40 spot (~$1.10) when a VOID/A14B-class
job needs 40GB+ with a disk that survives.** New-account $300 credits are a free
first-sprint benchmark budget. The general rule across E-G: consumer marketplaces
(RunPod/Vast) for consumer cards, CSPs only where their reliability or big-VRAM spot
prices earn the premium.
