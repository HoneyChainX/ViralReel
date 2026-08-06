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
