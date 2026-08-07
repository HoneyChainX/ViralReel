# THE KEEPER (1:00) — the all-systems capstone

Every lane of the studio in one film, at the host's honest maximum:

- **One character, two engines**: KIP_001's casting sheet (canon phrases, palette hexes)
  executed as an SVG puppet in the 2.5D acts AND a low-poly Cycles figure in the finale —
  measured cross-engine continuity: 8.4 luma / 3.2 chroma-V delta at the lane crossing
  (grade report), the casting-sheet discipline holding between renderers.
- **Acts 1-2 (Remotion 2.5D)**: 8 chained segments → 2 continuous shots, zero visible
  seams (SSIM-verified). Cottage walk at golden hour; the rowboat crossing as the sun
  lets go.
- **Act 3 (true-3D Cycles)**: 384 frames at 1080p on CPU via the bounded-chunk runner;
  Kip's boat reaches the light as the lamp wakes.
- **Editorial**: a textbook MATCH CUT at 22s (land→sea, same dusk, same composition) —
  invisible to content detection BY DESIGN; the new `qc: manual` manifest feature
  records it as eye-verified instead of silently dropping the expectation. The act2→3
  lane crossing earns the film's one dissolve.
- **Sound**: Kip narrates himself (casting-sheet voice lock, 9 lines), Satie No.1
  under the crossing, birds and waves per act — 12 streams, −13.6 LUFS measured.
- **Finishing**: colorist grade report with per-act signalstats and a judgment verdict
  (no LUT — the luma falloff IS the evening); **VMAF 96.6** delivery encode; subtitles
  in en / en-SDH / es (Argos MT, disclosed); key art in both aspects.
- **Platform upgrades minted by this film's QC pressure**: the AVTB timebase pin in
  conform's stitch graph (mixed cut→dissolve orders now compose) and the `qc: manual`
  matched-cut feature.

Deliverables: `releases/keeper-60s.mp4` (+ .srt tracks), key art in `studio/keyart/keeper/`.
Reports: `studio/film/keeper.report.json`, `studio/color/keeper.grade-report.json`,
chain reports, `studio/production/keeper.ledger.yaml` (verdict: renew).
