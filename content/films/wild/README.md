# WILD — a nature documentary (3:00)

The platform's first complete film, produced end-to-end on a CPU-only host at $0 marginal
cost, exercising every layer built in this integration:

- **Picture:** six 30s chapters (savanna dawn, old forest, river, mountains, ocean, night),
  each ONE continuous camera move produced as **3 independently rendered segments** chained
  by the frame-handoff contract — 18 separate videos → 6 seamless shots → 1 film.
  Stylized 2.5D "soft-Pixar" look: parallax depth, DOF blur, volumetric shafts,
  hand-animated creatures (giraffe, elephant, deer, heron, jumping fish, eagle, whale, owl).
- **Chains:** 12 joins verified — SSIM 0.994–0.998, zero visible seams
  (`studio/film/wild-ch*.chain.report.json`).
- **Conform:** exactly 180.000s (5,400 frames), all 5 chapter cuts detected at
  30/60/90/120/150s (`studio/film/wild.report.json`); OTIO timeline alongside.
- **Sound:** Kokoro narration (bm_george, 12 lines), Satie Gymnopédies No.1→No.3
  (Public Domain, Michael Laucke recordings), per-chapter ambience (PD garden birds,
  CC-BY Gravity Sound forest/wind, CC-BY Dordogne pond, CC-BY Icelandic waves) —
  20-stream mix, measured −14.0 LUFS. Full attribution: `audio/sources.json`.
- **Deliverable:** `releases/wild-3min.mp4` (1920×1080@30, H.264 high + AAC, 24.3 MB).

Production honesty: the first conform attempt FAILED its own QC — chained 1-frame xfades
collapsed the filter graph (30s video in a 180s container) and the soft-palette chapter
cuts sat below the scene detector's default threshold. Both fixes are permanent platform
improvements (concat-for-cuts stitch; per-film `qc_cut_threshold`), which is the QC layer
doing exactly its job.
