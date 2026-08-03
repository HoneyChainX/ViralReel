# Episode 001 — Adobe master prompt (single paste)

Two formats below. **Use PROMPT A alone** if your Adobe tool accepts a full creative brief
(Adobe Express "generate", Firefly Boards, an agentic Adobe assistant). **Use PROMPT B (4 clips)**
if you are in Firefly *Generate Video*, which produces ~5-second clips from one prompt and
therefore cannot make a 45-second multi-scene reel from a single generation.

Every figure below is verified against `evidence.json`. Do not edit the numbers.

---

## PROMPT A — the whole reel, one paste

> Create a 45-second vertical 9:16 (1080×1920) social video titled "A 55-inch 4K TV: 2016 vs 2026".
>
> **VISUAL STYLE — hold this identically for every shot.** Premium editorial retro-tech
> still-life. Near-black background (#0A0A0A). Cinematic studio lighting with a split colour
> grammar: warm amber light (#C8964B) whenever the subject represents 2016, hard cyan light
> (#00E5FF) whenever it represents 2026. Soft volumetric haze, shallow depth of field, slow
> deliberate camera moves, fine film grain, subtle vignette. Museum-artifact mood — objects
> presented like exhibits, not adverts. Generic unbranded consumer electronics only.
>
> **DO NOT** generate any text, numbers, captions, logos, brand marks, or user interfaces inside
> the imagery — all text is added afterwards as overlays. **DO NOT** imitate archival footage,
> news footage, security-camera footage, or home video. **DO NOT** include human faces.
>
> **NARRATION** (generate or import as voiceover; calm, measured, documentary register — a
> museum curator who is quietly furious about your rent; roughly 140 words per minute with full
> pauses where marked):
>
> "Twenty sixteen. April. A wall of brand-new four-K TVs. [pause] VIZIO's cheapest four-K
> fifty-five inch: nine sixty-seven fifty-eight dollars, in today's money. Watch it fall. [pause]
> Three nineteen ninety-six. [pause] Same size. Same resolution. Same tier. Almost everything got
> more expensive. This didn't. [pause] Why? One reason: panel factories outbuilt the market. The
> glut ran so deep, Korean panel makers left the business. Our receipts: down sixty-six point nine
> percent, after inflation. BLS's television index: sixty-seven point one. [pause] Two methods.
> Point two apart. Verdict: [pause] still cheap. One catch. [pause] Why it's this cheap costs you
> something else. Next dig."
>
> **SHOT SEQUENCE with on-screen text overlays:**
>
> **0:00–0:06 — THE ARTIFACT.** A single flat-screen television standing alone on a dark
> reflective surface, lit from the left in warm amber, dust motes drifting through the beam. Slow
> push in.
> *Overlay:* large amber number **$967.58**, small line beneath: "55-inch 4K TV, April 2016 — in
> July 2026 dollars". Small grey citation bottom-left: "VIZIO press release, 19 Apr 2016 · BLS
> CPI-U CUUR0000SA0".
>
> **0:06–0:12 — THE FALL.** The same television, now lit from the right in cold cyan; the amber
> light drains away across the shot. Slow lateral drift.
> *Overlay:* the number counts down mechanically from **$967.58** to **$319.96**, changing colour
> amber→cyan as it falls, then holds. Citation bottom-left: "P.C. Richard & Son, live listing,
> 3 Aug 2026 · $319.96 · also us.tcl.com $319.99".
>
> **0:12–0:18 — THE COMPARISON.** Two identical televisions side by side on the dark surface, one
> lit amber, one lit cyan, perfectly symmetrical. Static camera, slow breathing light.
> *Overlay:* "Same size. Same resolution. Same tier." then "ALMOST EVERYTHING +38.2%" in amber
> above "TELEVISIONS −67.1%" in cyan. Citation: "BLS CPI-U all items · BLS CUUR0000SERA01".
>
> **0:18–0:30 — THE CAUSE.** Interior of a vast, silent, empty electronics factory — long rows of
> idle machinery receding into darkness, cold cyan pools of light, deep shadow. Slow forward
> tracking move down the aisle. Then: an endless stack of identical unbranded flat panels
> stretching into the dark. Slow crane up.
> *Overlay:* "Panel factories outbuilt the market." then "The glut ran so deep, Korean panel makers
> left the business." Citation: "VIZIO Holding Corp. Form 10-K FY2023 (SEC) · TrendForce, 3 Jan 2024".
>
> **0:30–0:37 — THE PROOF.** Hold on a clean full-screen data chart (supplied separately as
> `price-chart-2016-2026.png` — do not generate it). Slow gentle zoom out.
> *Overlay:* "Our receipts: −66.9%" / "BLS index: −67.1%" / "Two methods. Point two apart."
>
> **0:37–0:42 — THE VERDICT.** The cyan-lit television alone in the dark, calm and still. Camera
> locked off.
> *Overlay:* the stamp graphic (supplied separately as `stamp-still-cheap.png`) slams in rotated
> 4°, with a 2-pixel shake on impact.
>
> **0:42–0:45 — THE HANDOFF.** Slow fade toward black; a single television glowing faintly in the
> distance.
> *Overlay:* "Why it's this cheap costs you something else." then "Next dig."
>
> **CAPTIONS:** burn in the narration as captions, centred, white, positioned in the upper-middle
> third so they clear the platform's bottom interface. **AUDIO:** narration only, no music bed, or
> a very quiet low drone at least 12 dB under the voice.

---

## PROMPT B — four clips for Firefly *Generate Video*

Generate each as a separate ~5-second clip, then assemble in Premiere or Express and add the
overlays listed in PROMPT A. Each prompt below is self-contained — the style block is repeated
deliberately so you can paste any one of them cold.

### B1 — the artifact (covers 0:00–0:12)
> A single unbranded flat-screen television standing alone on a dark reflective floor in an
> otherwise empty black space. Warm amber key light from the left, dust motes drifting through the
> beam, deep shadow, soft volumetric haze. Slow cinematic push-in. Premium editorial still-life,
> museum-artifact mood, near-black background, shallow depth of field, fine film grain, subtle
> vignette. Vertical 9:16. No text, no numbers, no logos, no brand marks, no user interface, no
> people, no faces. Not archival footage, not news footage, not home video.

### B2 — the comparison (covers 0:12–0:18)
> Two identical unbranded flat-screen televisions standing side by side on a dark reflective floor
> in an empty black space, perfectly symmetrical. The left one lit in warm amber, the right one lit
> in cold cyan, the two colours meeting in the middle. Static locked-off camera, slowly breathing
> light. Premium editorial still-life, museum-artifact mood, near-black background, shallow depth
> of field, fine film grain, subtle vignette. Vertical 9:16. No text, no numbers, no logos, no
> brand marks, no user interface, no people, no faces. Not archival footage, not news footage.

### B3 — the cause (covers 0:18–0:30)
> Interior of a vast, silent, abandoned electronics factory. Long rows of idle machinery receding
> into darkness, cold cyan pools of light spilling across a wet concrete floor, deep shadow, haze
> in the air. Slow forward tracking move down the empty aisle. Premium editorial cinematic style,
> industrial melancholy, near-black background, shallow depth of field, fine film grain, subtle
> vignette. Vertical 9:16. No text, no numbers, no logos, no brand marks, no people, no faces.
> Not archival footage, not news footage, not security-camera footage.

### B4 — the verdict and handoff (covers 0:37–0:45)
> A single unbranded flat-screen television alone in a vast dark empty space, lit only by cold cyan
> light, calm and completely still, its glow slowly receding into the blackness as the camera holds
> locked off. Premium editorial still-life, museum-artifact mood, near-black background, shallow
> depth of field, fine film grain, heavy vignette. Vertical 9:16. No text, no numbers, no logos, no
> brand marks, no user interface, no people, no faces. Not archival footage, not news footage.

*(0:30–0:37, the proof beat, is not generated — it is the real chart PNG held full-screen.)*

---

## Assets to drop in (already supplied, do not generate)

| File | Use |
|---|---|
| `price-chart-2016-2026.png` | full-screen at 0:30–0:37 — the real receipt, 11 named models |
| `stamp-still-cheap.png` | transparent PNG, slams in at 0:37, rotated 4° |

## Before you upload

- Set the **altered/synthetic content disclosure to YES** — this is generated imagery.
- Upload **private**, watch it once, then flip public.
- Then run `make published SLUG=four-k-tv` so the 2-per-day cap stays real.
