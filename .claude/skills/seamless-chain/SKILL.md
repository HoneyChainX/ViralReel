---
name: seamless-chain
description: Make multiple short clips play as ONE continuous shot via the studio's frame-handoff contract (last frame of segment N ≡ first frame of segment N+1), with SSIM join verification and inverted seam QC. Use when a shot is longer than one segment any engine can produce, or the user asks to chain/stitch clips seamlessly, or invokes /seamless-chain. The continuity-supervisor agent's workflow, packaged.
---

You are running the studio's seamless-chaining workflow (docs/12, continuity-supervisor
charter). The contract: **the last frame of segment N is exactly the first frame of
segment N+1** — so stitching is a butt-join dropping the duplicate frame, and
seamlessness is testable, not aspirational.

## Steps

1. **Plan the chain** — split at motion valleys, never mid-action. For 3+ segments,
   go keyframe-first: produce ALL boundary frames before any segment.
2. **Produce segments** by lane:
   - Deterministic (Remotion/bpy): overlap frame ranges by exactly 1 frame — e.g.
     segments `0-150`, `150-300`, `300-449` (the last one stops before the next scene).
   - Generative I2V: `python3 scripts/studio/seamless.py handoff segN.mp4 init.png`
     → next segment's init image. Wan FLF2V pins BOTH ends (strongest joins).
3. **Write the chain manifest** — `studio/film/<slug>.chain.yaml`:
   ```yaml
   chain:
     slug: my-shot
     delivery: { width: 1920, height: 1080, fps: 30 }
     handoff: { mode: exact, overlap_frames: 1, ssim_min: 0.97 }
   segments:
     - { id: s1, source: out/seg-0-150.mp4 }
     - { id: s2, source: out/seg-150-300.mp4 }
     - { id: s3, source: out/seg-300-449.mp4 }
   ```
4. **Verify then stitch**:
   ```
   python3 scripts/studio/seamless.py verify studio/film/<slug>.chain.yaml
   python3 scripts/studio/seamless.py stitch studio/film/<slug>.chain.yaml
   ```
   Stitch re-verifies, joins, then runs the INVERTED cut check: PySceneDetect must NOT
   find a boundary at any join. Read `studio/film/<slug>.chain.report.json` —
   `visible_seams` must be empty and every join SSIM ≥ ssim_min.

## Rules
- A failed join means REGENERATE the offending boundary — never lower `ssim_min`, never
  hide it with a crossfade (that's a dissolve pretending to be a shot).
- Chains deliver picture only; audio is laid over the whole continuous shot at film
  level (a sound restart every 5s is an audible seam).
- Drift budget: beyond ~4–5 last-frame hops, re-anchor with a pinned keyframe or hand
  the join to film-editor as an honest cut.
- The chain output enters a film manifest as ONE scene (see /film-assembly).
