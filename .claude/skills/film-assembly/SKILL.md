---
name: film-assembly
description: Assemble multiple scene videos into one finished film through the studio's conform pipeline — film manifest, validate, OTIO timeline, render with mechanical QC (duration, cuts, delivery spec). Use when the user asks to combine scenes/shots/chapters into a film or episode, or invokes /film-assembly. The film-editor agent's workflow, packaged.
---

You are running the studio's film-assembly workflow (docs/12-film-assembly.md). The
film manifest is the source of truth; conform renders and QCs it mechanically.

## Steps

1. **Write the film manifest** — `studio/film/<slug>.yaml`:
   ```yaml
   slug: my-film
   title: "MY FILM"
   delivery: { width: 1920, height: 1080, fps: 30, lufs: -14, fit: crop }
   qc_cut_threshold: 12        # lower for soft/similar-palette cuts (LIGHTHOUSE used 3)
   scenes:
     - { id: scene-1, source: out/scene-1.mp4 }
     - id: scene-2
       source: out/scene-2.mp4
       transition_out: { type: xfade, dur: 0.5 }   # only when the cut EARNS it
     - { id: scene-3, source: out/scene-3.mp4 }
   ```
   Every scene source must exist (two-source rule: check with ffprobe, never assume).

2. **Conform**: from repo root:
   ```
   python3 scripts/studio/conform.py validate studio/film/<slug>.yaml
   python3 scripts/studio/conform.py timeline studio/film/<slug>.yaml   # writes .otio
   python3 scripts/studio/conform.py render   studio/film/<slug>.yaml   # writes out/<slug>.mp4 + report
   ```

3. **Read the QC report** (`studio/film/<slug>.report.json`) — duration_ok, delivery_ok,
   and cut_check.ok must all be true. A missed expected cut means the detector can't see
   it: first ask whether the cut should be a dissolve (craft), only then lower
   `qc_cut_threshold` (force). Never delete the expectation.

4. **Audio**: conform outputs picture with silence. Mix the soundtrack separately
   (VO/music/ambience at the film's timeline positions), loudnorm to the manifest's
   LUFS, then mux: `ffmpeg -i out/<slug>.mp4 -i mix.m4a -map 0:v -map 1:a -c copy
   -shortest -movflags +faststart out/<slug>-final.mp4`. Verify loudness with ebur128.

## Rules
- Scenes come from their owning lanes; weak scenes go BACK to their lane — nothing is
  patched inside the stitch.
- Chains (continuous shots from segments) enter as ONE scene — see /seamless-chain.
- ffmpeg/ffprobe live at `vendor/ffbin/bin` (export PATH first).
- Deliverables ship from `releases/` (the one gitignore-exempt home for tracked media).
