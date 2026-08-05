# LIGHTHOUSE (0:15) — the platform's first true-3D film

Proof that the 3D lane is real: rendered with **Blender 5 (bpy) + Cycles on CPU**,
fully procedural — one Python file (`make_film.py`) IS the film. No downloaded assets.

- **Three shots, one world, day → dusk**: wide orbit (afternoon), water-level push-in
  (sunset, dissolve = the honest time-jump), lamp close-up (dusk — the light wakes and
  sweeps as the sky dies). The film is about the moment a built thing takes over from
  the sky.
- **Render**: 360 frames, 1280×720, Cycles CPU 48 samples + OpenImageDenoise, AgX
  grade, ~23 s/frame via the bounded-chunk farm runner (`render_chunk.sh`) — the
  harness-safe resumable pattern that survived two detached-process reapings.
- **Conform QC honesty**: the scene detector could not see the afternoon→sunset cut at
  any threshold (sky-on-sky palettes) — the fix was craft, not force: a 0.5 s dissolve,
  which the time-jump legitimately earns. The dusk hard cut verified at 8.5 s.
- **Sound**: Lækjavik ocean ambience (CC-BY) under the whole film; Satie Gymnopédie
  No. 3 (Public Domain, Michael Laucke) enters with the lamp. −13.8 LUFS measured.
- **Blender 5 API ports made along the way** (recorded for the next 3D film):
  MULTIPLE_SCATTERING sky, slotted actions, EEVEE-era property guards, PNG-sequence
  rendering (pip bpy ships no video encoder — the farm assembles).

Deliverable: `releases/lighthouse-15s.mp4` (2.8 MB). Reports: `studio/film/lighthouse.report.json`.
