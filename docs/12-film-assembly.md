# 12 — Film Assembly: from storyboards to one complete film

The platform's scene lanes (sourced footage, Remotion animation, generative engines,
2D animation) each produce *a video*. This document defines how the studio turns many of
them into *a film* — storyboards → scene flow → parallel scene production → conform.
Research basis: docs/11-platform-research.md §5 (assembly sweep).

---

## The pipeline

```
   script (Fountain, screenplain)             story-showrunner / script-editor
        │
   shot & scene plan (shot_plan.json)         previs-director
        │   per scene: intent, framing, source lane, duration, recipe refs
        │   boards where ambiguity lives (Storypencil / recipe previews)
        ▼
   SCENE PRODUCTION — parallel, any lane      gen-supervisor · animation-director ·
        │   each scene → an ordinary video     motion-director · archive-sourcer ·
        │   file + its own licenses/QC         render-wrangler
        ▼
   film manifest (studio/film/<slug>.yaml)    film-editor
        │   order · trims · transitions · delivery spec — the cut, versioned as YAML
        ▼
   conform (scripts/studio/conform.py)        film-editor + render-wrangler
        │   validate → OTIO timeline → normalize scenes → stitch → loudness → QC report
        ▼
   out/<slug>.mp4 + <slug>.report.json  →  compliance gate (if publishing) → delivery
```

## The three artifacts that make it work

1. **The film manifest** (`studio/film/<slug>.yaml`) — the cut as reviewable text: scene
   order, `in`/`out` trims, `transition_out` per scene, one delivery spec (`fit: crop|pad`
   decided consciously per film). If it isn't in the manifest, it isn't in the film.
2. **The OTIO timeline** (`conform.py timeline` → `<slug>.otio`) — the interchange
   artifact. OpenTimelineIO (ASWF, Pixar lineage) is what carries the cut into any real
   NLE (Resolve, kdenlive/MLT, Blender VSE) the day a human editor wants it. Interchange,
   not render path.
3. **The QC report** (`<slug>.report.json`) — measured duration vs expected, delivery
   spec, integrated loudness. Written on every render; a red report blocks delivery.

## Why manifest + ffmpeg is the spine (a decision, not a default)

- **Agents and humans share it.** YAML cut lists are diffable, reviewable in a PR, and
  editable by every agent in the studio. NLE project files are none of those.
- **Scenes stay heterogeneous.** The normalize step conforms any lane's output (resolution,
  fps, missing audio → synthesized silence) *before* the stitch, so a sourced 16:9 clip, a
  Remotion vertical, and a GPU-generated shot coexist in one film.
- **One uniform stitch graph.** Cuts are 1-frame xfades — one code path, no special cases;
  invisible at 30fps and documented in `conform.py` rather than hidden.
- OTIO remains the escape hatch to professional editorial, so choosing the simple spine
  costs nothing later.

## Scene-to-scene continuity (the generative lanes)

Linking scenes is an editorial problem *and* a continuity problem. For generative films:
- **Character consistency:** pinned reference images / character sheets per project;
  workflows in `studio/workflows/` carry the reference inputs so every scene's shots use
  the same identity (gen-supervisor's charter).
- **Visual continuity across scene joins:** **Wan 2.2 FLF2V** (first+last-frame
  conditioning) where controlled joins matter — generate boundary keyframes first,
  interpolate video between them; last-frame chaining
  (`ffmpeg -sseof -0.05 -i sceneN.mp4 -frames:v 1 last.png` → I2V init for scene N+1) as
  the cheap fallback, accepting drift over many hops; a deliberate cut where a new scene
  should read as new.
- **Sound continuity:** conform normalizes loudness mechanically; *texture* across joins
  (VO into silence, ambience handoffs) is film-editor judgment, fixed by trims or by
  sending a scene back for a tail bed.

## Proven in this repo

`studio/film/showcase-reel.yaml` links the two platform test videos — the sourced-footage
lane's desert-sea piece and the programmatic-animation lane's kids cartoon — into one
74.4s film: validate ✓, `.otio` written ✓, conform QC green (duration exact, 1080×1920@30,
−14.0 LUFS measured). The engine is the same at 2 scenes or 40.

## Division of labour

| Concern | Owner |
|---|---|
| What scenes exist, their order and rhythm | `film-editor` (manifest) |
| What's inside each scene | the producing lane's agents |
| Boards, shot flow, scene continuity plan | `previs-director` |
| Character/look continuity across scenes | `gen-supervisor` |
| Running the conform render + farm mechanics | `render-wrangler` |
| Final assembly QC bar | `film-editor` (report) + gate if publishing |

---

## Seamless chaining — the long-video fix

Engines generate short segments; films are long. The platform's answer is a dedicated
layer (`scripts/studio/seamless.py` + `studio/film/*.chain.yaml`, owned by
`continuity-supervisor`) built on one contract:

> **The last frame of segment N is exactly the first frame of segment N+1.**

With the contract held, N independent 5-second videos butt-join into one continuous shot:
the duplicated boundary frame is dropped at stitch, no transition exists at the join, and
seamlessness is *measured*, not hoped for:

- `verify` — SSIM between every segment's last frame and its successor's first frame
  (contract threshold, default ≥ 0.97; deterministic renders score ≈ 1.0).
- `stitch` — dedupe overlaps, concat, then the **inverted cut-check**: PySceneDetect must
  find NO boundary at any join time. A conform QC asserts cuts exist; a chain QC asserts
  they don't. Both are the same honesty pointed in opposite directions.

How boundary frames are produced per lane: deterministic renders overlap frame ranges by
one; generative segments condition on the previous last frame (`seamless.py handoff` →
I2V init), or — strongest — plan **keyframe-first with Wan FLF2V**: author all boundary
frames before any video, then fill each segment between its pinned ends, so joins cannot
drift. Splitting doctrine (motion valleys, drift budgets, re-anchoring) lives in the
continuity-supervisor charter.

Chains deliver picture only; audio is laid over the whole continuous shot at film level.
A chain's output enters a film manifest as one ordinary scene — film-editor cuts between
scenes, continuity-supervisor makes the inside of a scene continuous.

Proven in-repo: `studio/film/cami-chain-demo.chain.yaml` — five independently rendered
5-second videos of the cartoon, chained by 1-frame overlap, stitched to one 25-second
continuous shot with per-join SSIM and a clean seam check (report committed alongside).
