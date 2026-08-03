# four-k-tv — Adobe production pack (shot list v1, synced to script-v3.md)

**Pipeline:** Firefly text-to-image (9:16) → Firefly image-to-video (5s clips) → assemble in
Premiere/Express with REAL overlays. Generated layers are STYLIZED AND OBVIOUSLY NON-DOCUMENTARY
(docs/05-compliance.md Rule 6, adapted): cinematic/graphic/symbolic only — never imitation
archival, news, CCTV, home video, or a real 2016 storefront presented as a record. The RECEIPTS
stay real: every price, chip, the chart PNG and press-release stills are real screenshots/text
overlaid in edit. AI disclosure ON at upload.

**VO runtime:** ~44s (93 words @ ~140wpm + 7 pauses). Shot durations below sum to 0:44.

---

## THE STYLE — "DIMENSIONAL LEDGER" (locked for all 12 shots)

Premium editorial retro-tech: dimensional collage / cinematic 3D still-life of consumer
electronics floating in a near-black void (#0A0A0A). The frame is a museum vitrine, not a
memory: objects lit like artifacts, never like news footage. The channel's colour grammar is
built into the LIGHT — amber gel (#C8964B) always lights the 2016 side, cyan gel (#00E5FF)
always lights the 2026 side; when both eras share a frame, the light splits down the middle.
Soft volumetric haze, dust motes, shallow depth of field, generic unbranded hardware only.
NO text in generated images (all type is the real data layer, added in edit). NO real logos.
NO photoreal human faces. Never imitates archival/news/CCTV/home-video texture.

**STYLE TOKENS — paste at the end of every image prompt, verbatim:**
`premium editorial retro-tech, dimensional collage still-life, cinematic 3D render aesthetic, near-black background, split amber and cyan gel lighting, soft volumetric haze, dust motes, shallow depth of field, 9:16 vertical portrait, blank screens, unbranded generic hardware, no text, no logos, no people`

**NEGATIVE — paste on every generation, verbatim:**
`text, letters, numbers, captions, subtitles, watermarks, logos, brand names, UI, human faces, people, hands, archival film look, VHS, news broadcast look, CCTV, security camera, home video, documentary photograph, storefront signage`

**Framing rule:** keep the centre band of every image quiet (bottom ~15% and the vertical
centre) — hero numbers and citation chips land there in edit. Data layer stays flat, sharp,
white/amber/cyan, no glow (brand/tokens.css `.pa-data-layer`).

**Firefly workflow note:** generate stills at 9:16, upscale, then image-to-video with ONE move
per shot (directives below). Firefly clips run ~5s; trim to shot length in Premiere. If a move
comes back wobbly, regenerate — never speed up the odometer or the stamp to compensate.

---

## SHOT 1 — ARTIFACT (scene) · 0:00–0:04 · 4s
**VO:** "Twenty sixteen. April. A wall of brand-new four-K TVs."

**FIREFLY IMAGE PROMPT:** A monumental floating wall of dozens of identical slim flat-screen
televisions with blank dark glass screens, arranged in a perfect grid that recedes into black
space like a museum installation, every set unbranded and generic, the whole wall bathed in
warm amber gel light from the left with deep shadows between the rows, faint warm haze catching
the light, seen from a low three-quarter angle so the grid towers upward out of frame,
`premium editorial retro-tech, dimensional collage still-life, cinematic 3D render aesthetic, near-black background, split amber and cyan gel lighting, soft volumetric haze, dust motes, shallow depth of field, 9:16 vertical portrait, blank screens, unbranded generic hardware, no text, no logos, no people`
**NEGATIVE:** `text, letters, numbers, captions, subtitles, watermarks, logos, brand names, UI, human faces, people, hands, archival film look, VHS, news broadcast look, CCTV, security camera, home video, documentary photograph, storefront signage`

**FIREFLY VIDEO:** slow push-in toward the wall, dust motes drift through the amber beam, 5s.

**OVERLAY (Premiere/Express — REAL):**
- Eyebrow label, amber (#C8964B), 32px-scale: `2016 · APRIL`
- No price on screen yet → no citation chip required this shot.
- Caption line (from captions.json track): "2016. April. A wall of brand-new 4K TVs."

---

## SHOT 2 — ARTIFACT (the number lands) · 0:04–0:09 · 5s
**VO:** "VIZIO's cheapest four-K fifty-five inch: nine sixty-seven fifty-eight dollars, in today's money."

**FIREFLY IMAGE PROMPT:** A single slim generic flat-screen television presented like a museum
artifact on a dark plinth, blank dark screen, isolated in black space, dramatic warm amber gel
key light raking across it from the upper left, a soft amber pool of light on the plinth,
volumetric haze and slow dust, generous empty black space in the upper two thirds of the frame
for negative space, three-quarter hero angle, `premium editorial retro-tech, dimensional collage
still-life, cinematic 3D render aesthetic, near-black background, split amber and cyan gel
lighting, soft volumetric haze, dust motes, shallow depth of field, 9:16 vertical portrait,
blank screens, unbranded generic hardware, no text, no logos, no people`
**NEGATIVE:** `text, letters, numbers, captions, subtitles, watermarks, logos, brand names, UI, human faces, people, hands, archival film look, VHS, news broadcast look, CCTV, security camera, home video, documentary photograph, storefront signage`

**FIREFLY VIDEO:** slow orbital drift right around the TV, amber beam flares gently, 5s.

**OVERLAY (REAL):**
- HERO NUMBER, amber (#C8964B), tabular figures, 176px-scale: `$967.58` — lands right after
  the [PAUSE], on "nine sixty-seven".
- Sub-line, white body: `in today's money`
- CITATION CHIP (bottom-left, 14px, 60% opacity, verbatim):
  `VIZIO PRESS RELEASE (PR NEWSWIRE) · 19 APR 2016 · E55u-D0 MSRP $699.99 · × BLS CPI-U CUUR0000SA0 APR 2016→JUL 2026 = $967.58`
- Optional receipt flash (last ~1s): real still `assets/2016-press-release.png` as a small
  inset card, desaturated 40%, under the data layer — it is a real screenshot, allowed.

---

## SHOT 3 — GAP · **THE ODOMETER MOMENT** · 0:09–0:12 · 3s
**VO:** "Watch it fall. [PAUSE — odometer rolls INSIDE this pause] Three nineteen ninety-six."

**FIREFLY IMAGE PROMPT:** Two identical generic flat-screen televisions facing each other
across a narrow black gap, mirrored composition, the left set lit entirely in warm amber gel
light, the right set lit entirely in electric cyan gel light, a razor-thin vertical seam of
darkness dividing the frame exactly down the middle, haze on each side tinted by its own light,
symmetrical and still like a diptych in a gallery, wide empty black band across the centre of
the frame, `premium editorial retro-tech, dimensional collage still-life, cinematic 3D render
aesthetic, near-black background, split amber and cyan gel lighting, soft volumetric haze, dust
motes, shallow depth of field, 9:16 vertical portrait, blank screens, unbranded generic
hardware, no text, no logos, no people`
**NEGATIVE:** `text, letters, numbers, captions, subtitles, watermarks, logos, brand names, UI, human faces, people, hands, archival film look, VHS, news broadcast look, CCTV, security camera, home video, documentary photograph, storefront signage`

**FIREFLY VIDEO:** near-static hold, only the haze breathes and the cyan side slowly brightens,
5s. (The motion of this beat is the NUMBER, not the camera.)

**OVERLAY (REAL) — ⚡ ODOMETER, fires ONCE per episode, here only:**
- **Preferred: use studio asset** — the Remotion `<PriceOdometer>` (render_props.json /
  brand tokens: 800ms roll, ease-out cubic-bezier(0.16,1,0.3,1)), rolling `$967.58` → `$319.96`,
  colour crossfading amber → cyan as it rolls. Export as transparent-background ProRes 4444
  and drop on V3.
- **Premiere fallback (two text layers):** Layer A = `$967.58` in amber, tabular figures;
  Layer B = `$319.96` in cyan, identical position/size. At the start of the [PAUSE] after
  "Watch it fall.": cut Layer A out and Layer B in, bridged by an 0.8s roll fake — apply a
  20px vertical Position keyframe DOWN + fast blur-out on A and mirrored Position UP +
  blur-in on B (ease-out, no spring). Digits stay fixed-width so nothing jitters. Do NOT
  stretch the roll past ~0.8s.
- CITATION CHIP (verbatim, two lines — the first covers the $967.58 frames before the roll):
  `FROM: VIZIO PRESS RELEASE 19 APR 2016 ($699.99 MSRP) x BLS CPI-U CUUR0000SA0 = $967.58`
  `TO: P.C. RICHARD & SON · LIVE LISTING · 3 AUG 2026 · $319.96 · ALSO US.TCL.COM $319.99`

---

## SHOT 4 — GAP (held beat: same-same-same) · 0:12–0:16 · 4s
**VO:** "[PAUSE] Same size. Same resolution. Same tier."

**FIREFLY IMAGE PROMPT:** Extreme close-up of two television corners meeting edge to edge in
black space, one bezel edge rimmed in amber light and the other rimmed in cyan light, the two
panels almost touching, macro detail of matte plastic and dark glass, the seam between them
glowing faintly where amber haze meets cyan haze, abstract and geometric, large areas of pure
black around the subject, `premium editorial retro-tech, dimensional collage still-life,
cinematic 3D render aesthetic, near-black background, split amber and cyan gel lighting, soft
volumetric haze, dust motes, shallow depth of field, 9:16 vertical portrait, blank screens,
unbranded generic hardware, no text, no logos, no people`
**NEGATIVE:** `text, letters, numbers, captions, subtitles, watermarks, logos, brand names, UI, human faces, people, hands, archival film look, VHS, news broadcast look, CCTV, security camera, home video, documentary photograph, storefront signage`

**FIREFLY VIDEO:** lateral parallax left along the seam, macro depth shift, 5s.

**OVERLAY (REAL):**
- Three white body lines, entering one per spoken phrase: `55-INCH CLASS` / `3840 × 2160` /
  `ENTRY 4K LINE, BOTH YEARS` (spec_note's held axes; LED-backlit LCD both sides).
- **Honesty-concession chip (required by script v3 — the MSRP-vs-shelf asterisk lives under
  this GAP beat), bottom-left, verbatim:**
  `2016 = LAUNCH MSRP · 2026 = SHELF PRICE · STREET PRICES FELL INSIDE 2016 TOO (LG 55UH7700: $1,799 MSRP, LG 10 MAR 2016 → $999 STREET, TECHRADAR)`
- Both prices are referenced in the chip → chip stays the full shot.

---

## SHOT 5 — EXCAVATION (the wrong-direction turn) · 0:16–0:20 · 4s
**VO:** "Almost everything got more expensive. [EMPHASIS] This didn't. [PAUSE] Why?"

**FIREFLY IMAGE PROMPT:** A surreal dimensional collage of everyday consumer goods — a milk
carton, a sneaker, a coffee cup, a house key, all generic and unlabeled — drifting slowly
upward through warm amber light in the top half of the frame, while below them a single
generic flat-screen television sinks down into cold cyan light at the bottom of the frame,
vertical composition of two opposing currents in black space, haze tinted amber above and
cyan below, `premium editorial retro-tech, dimensional collage still-life, cinematic 3D
render aesthetic, near-black background, split amber and cyan gel lighting, soft volumetric
haze, dust motes, shallow depth of field, 9:16 vertical portrait, blank screens, unbranded
generic hardware, no text, no logos, no people`
**NEGATIVE:** `text, letters, numbers, captions, subtitles, watermarks, logos, brand names, UI, human faces, people, hands, archival film look, VHS, news broadcast look, CCTV, security camera, home video, documentary photograph, storefront signage`

**FIREFLY VIDEO:** objects drift upward slowly, the TV sinks; camera locked, 5s.

**OVERLAY (REAL):**
- Split figures, entering on their phrases: amber `ALMOST EVERYTHING +38.2%` (top) · cyan
  `TVs ↓` (bottom, arrow only — the TV percentages get their own beat at 0:28).
- CITATION CHIP (verbatim): `BLS CPI-U ALL ITEMS CUUR0000SA0 · APR 2016 239.261 → JUL 2026 330.724 · +38.2%`
- "Why?" hangs over the last beat with the frame otherwise clean.

---

## SHOT 6 — EXCAVATION (THE ONE CAUSE) · 0:20–0:24 · 4s
**VO:** "One reason: panel factories outbuilt the market."

**FIREFLY IMAGE PROMPT:** A vast abstract factory interior receding to infinity, endless
identical sheets of luminous glass panels racked in towering rows like server aisles, each
thin glass sheet catching cold cyan edge light, the far end of the hall dissolving into black
haze, scale monumental and inhuman, floor mirror-dark, one aisle running straight down the
centre of the vertical frame toward a vanishing point, clearly a stylized symbolic space
rather than a real photographed factory, `premium editorial retro-tech, dimensional collage
still-life, cinematic 3D render aesthetic, near-black background, split amber and cyan gel
lighting, soft volumetric haze, dust motes, shallow depth of field, 9:16 vertical portrait,
blank screens, unbranded generic hardware, no text, no logos, no people`
**NEGATIVE:** `text, letters, numbers, captions, subtitles, watermarks, logos, brand names, UI, human faces, people, hands, archival film look, VHS, news broadcast look, CCTV, security camera, home video, documentary photograph, storefront signage`

**FIREFLY VIDEO:** slow dolly forward down the centre aisle, panels shimmer as they pass, 5s.

**OVERLAY (REAL):**
- Cause card, white, body scale: `ONE CAUSE: PANEL FACTORIES OUTBUILT THE MARKET`
- CITATION CHIP (verbatim): `VIZIO 10-K FY2023 · SEC EDGAR · FILED 28 FEB 2024 · "A SURGE IN PRODUCTION CAPACITY… SHARP DECLINES IN PRICES"`
- No price on screen; chip carries the causal receipt instead.

---

## SHOT 7 — EXCAVATION (the human stake: the exit) · 0:24–0:28 · 4s
**VO:** "The glut ran so deep, Korean panel makers left the business."

**FIREFLY IMAGE PROMPT:** The same monumental glass-panel hall now half dark, whole racks of
glass sheets standing unlit and grey toward the front of the frame while only the far end
still glows faint cyan, overhead lights extinguished in sequence down the hall, dust hanging
still in a single remaining cold beam, empty and monumental, mood of departure and shutdown,
symbolic stylized space, `premium editorial retro-tech, dimensional collage still-life,
cinematic 3D render aesthetic, near-black background, split amber and cyan gel lighting, soft
volumetric haze, dust motes, shallow depth of field, 9:16 vertical portrait, blank screens,
unbranded generic hardware, no text, no logos, no people`
**NEGATIVE:** `text, letters, numbers, captions, subtitles, watermarks, logos, brand names, UI, human faces, people, hands, archival film look, VHS, news broadcast look, CCTV, security camera, home video, documentary photograph, storefront signage`

**FIREFLY VIDEO:** hold, then the nearest bank of lights dims to black one row at a time, 5s.

**OVERLAY (REAL):**
- CITATION CHIP (verbatim): `TRENDFORCE · 3 JAN 2024 · "KOREAN PANEL MAKERS TO EXIT THE SUPPLY CHAIN UNDER LOSS PRESSURES"`
- No hero number. Let the lights-out beat carry it.

---

## SHOT 8 — PROOF FLEX (receipt 1: our pair) · **REAL CHART BEAT** · 0:28–0:32 · 4s
**VO:** "Our receipts: down sixty-six point nine percent, after inflation."

**GENERATED IMAGE: NONE. This shot IS the receipt.**
Full-screen REAL asset: `assets/price-chart-2016-2026.png` (the original 11-model chart,
built for this episode). It is a real graphic — do not regenerate, restyle, or trace it.

**MOVE (Premiere/Express, not Firefly):** slow push-in (~103% over 4s) anchored on the entry-tier
pair so the still never sits static over 2s (motion-director slideshow rule). Background
behind any letterboxing: #0A0A0A.

**OVERLAY (REAL):**
- Hero figure, cyan, entering on "sixty-six": `−66.9%` + white sub-line `after inflation`
- CITATION CHIP (verbatim): `$699.99 (VIZIO, 19 APR 2016, CPI-ADJ $967.58) → $319.96 (P.C. RICHARD, 3 AUG 2026) · 1 − 319.96/967.58 = −66.9%`
- The chart's own footer already carries the BLS constant-quality line and the c3/c4
  premium-tier anti-cherry-pick points — keep them visible, do not crop the footer.

---

## SHOT 9 — PROOF FLEX (receipt 2: two methods) · 0:32–0:37 · 5s
**VO:** "BLS's television index: sixty-seven point one. [PAUSE] Two methods. Point two apart."

**FIREFLY IMAGE PROMPT:** Two tall abstract monoliths of dark glass standing side by side in
black space like a diptych of standing stones, nearly identical in height, the left monolith
edge-lit in warm amber and the right monolith edge-lit in cold cyan, a narrow luminous gap
between them, floor reflective and dark, composition rigorously symmetrical with generous
black space above for type, monumental and minimal, `premium editorial retro-tech, dimensional
collage still-life, cinematic 3D render aesthetic, near-black background, split amber and cyan
gel lighting, soft volumetric haze, dust motes, shallow depth of field, 9:16 vertical portrait,
blank screens, unbranded generic hardware, no text, no logos, no people`
**NEGATIVE:** `text, letters, numbers, captions, subtitles, watermarks, logos, brand names, UI, human faces, people, hands, archival film look, VHS, news broadcast look, CCTV, security camera, home video, documentary photograph, storefront signage`

**FIREFLY VIDEO:** very slow rise (crane up) along the two monoliths, haze drifts through the
gap, 5s.

**OVERLAY (REAL):**
- Two figures side by side, entering together after the [PAUSE] is set up:
  left, white over amber-lit column: `OUR PAIR −66.9% (REAL)` · right, white over cyan-lit
  column: `BLS INDEX −67.1% (NOMINAL)`
- Delta line, white, on "Point two apart.": `0.2 APART`
- **REQUIRED COMPLIANCE CHIP (script v3 "point-two line" — must be on screen with the 67.1
  figure, verbatim):** `BLS CUUR0000SERA01, NOMINAL, CONSTANT-QUALITY · REAL FALL −76.2%`
- Second chip line: `BLS TELEVISIONS INDEX · APR 2016 283.408 → JUL 2026 93.176`

---

## SHOT 10 — VERDICT · **STAMP BEAT** · 0:37–0:39 · 2s
**VO:** "Verdict: [PAUSE] still cheap."

**FIREFLY IMAGE PROMPT:** A single generic flat-screen television alone in a vast black void,
seen straight on and centred low in the vertical frame, lit only by a soft cool cyan glow that
rises off it like the last light in a dark room, everything else pure black, absolute
stillness, enormous empty space above the set, `premium editorial retro-tech, dimensional
collage still-life, cinematic 3D render aesthetic, near-black background, split amber and cyan
gel lighting, soft volumetric haze, dust motes, shallow depth of field, 9:16 vertical portrait,
blank screens, unbranded generic hardware, no text, no logos, no people`
**NEGATIVE:** `text, letters, numbers, captions, subtitles, watermarks, logos, brand names, UI, human faces, people, hands, archival film look, VHS, news broadcast look, CCTV, security camera, home video, documentary photograph, storefront signage`

**FIREFLY VIDEO:** locked-off hold, cyan glow pulses up slightly once, 5s (use ~2s).

**OVERLAY (REAL) — ✅ STILL CHEAP STAMP (studio asset):**
- Use the studio stamp asset: `STILL CHEAP`, cyan #00E5FF, rotated 4° clockwise, hard-edged
  8px border, 2px offset shake on entry, no shadow/glow (brand/tokens.css `.pa-stamp--still-cheap`).
- **Sync rule (motion-director):** the stamp lands on the exact frame the voice says "cheap"
  — the [PAUSE] after "Verdict:" is the wind-up. Even 3 frames off reads as broken.
- No citation chip (no price on this frame); the verdict maps to evidence.json `verdict: STILL CHEAP`.

---

## SHOT 11 — HANDOFF (the catch, teased) · 0:39–0:42 · 3s
**VO:** "One catch. [PAUSE] Why it's this cheap costs you something else."

**FIREFLY IMAGE PROMPT:** The same television now glowing from within, its blank screen casting
a bright cold cyan wash across an otherwise empty dark room suggested only by faint floor and
wall planes, the light almost watchful, a thin amber hairline of light leaking under a door
edge far in the background, uneasy and quiet, symbolic not domestic, no furniture detail, no
people, `premium editorial retro-tech, dimensional collage still-life, cinematic 3D render
aesthetic, near-black background, split amber and cyan gel lighting, soft volumetric haze,
dust motes, shallow depth of field, 9:16 vertical portrait, blank screens, unbranded generic
hardware, no text, no logos, no people`
**NEGATIVE:** `text, letters, numbers, captions, subtitles, watermarks, logos, brand names, UI, human faces, people, hands, archival film look, VHS, news broadcast look, CCTV, security camera, home video, documentary photograph, storefront signage`

**FIREFLY VIDEO:** slow push-in toward the glowing screen, its light flickers once, 5s.

**OVERLAY (REAL):**
- NOTHING factual. One-cause rule: no figure, no mechanism, no "ads" on screen — the tease
  asserts only that a catch exists (backed by VIZIO 10-K FY2023, next episode's dig).
- Caption track only: "One catch. Why it's this cheap costs you something else."

---

## SHOT 12 — HANDOFF (serial kicker end card) · 0:42–0:44 · 2s
**VO:** "Next dig."

**FIREFLY IMAGE PROMPT:** Macro close-up of dark glass screen surface filling the frame,
a faint cyan glow fading out across it from centre to edges as if the set is powering down,
one last ember of amber light reflected small and deep in the glass, near-total darkness,
abstract, quiet, final, `premium editorial retro-tech, dimensional collage still-life,
cinematic 3D render aesthetic, near-black background, split amber and cyan gel lighting, soft
volumetric haze, dust motes, shallow depth of field, 9:16 vertical portrait, blank screens,
unbranded generic hardware, no text, no logos, no people`
**NEGATIVE:** `text, letters, numbers, captions, subtitles, watermarks, logos, brand names, UI, human faces, people, hands, archival film look, VHS, news broadcast look, CCTV, security camera, home video, documentary photograph, storefront signage`

**FIREFLY VIDEO:** the glow contracts and dies to black, 5s (use last 2s so it ends on black).

**OVERLAY (REAL):**
- End-card type, white, stamp scale: `NEXT DIG` — enters with the spoken words, holds to black.
- No figures, no chip. Cut to black on 0:44.

---

## ASSEMBLY TIMELINE (Premiere/Express, 1080×1920, ground #0A0A0A)

| Shot | Start | End | Beat | Underlying layer | Overlay (REAL data layer) | Caption line |
|---|---|---|---|---|---|---|
| 1 | 0:00.0 | 0:04.0 | ARTIFACT | Firefly: amber TV wall, push-in | `2016 · APRIL` eyebrow (amber) | "2016. April. A wall of brand-new 4K TVs." |
| 2 | 0:04.0 | 0:09.0 | ARTIFACT | Firefly: amber artifact TV, orbit | `$967.58` hero (amber) + "in today's money" + VIZIO/PRN 19 APR 2016 · $699.99 × BLS CUUR0000SA0 chip; optional `assets/2016-press-release.png` inset | "VIZIO's cheapest 4K 55-inch: $967.58 in today's money." |
| 3 | 0:09.0 | 0:12.0 | GAP ⚡ODOMETER | Firefly: amber/cyan diptych, hold | **Odometer $967.58 → $319.96** (studio `<PriceOdometer>` or 2-layer fake, 0.8s, rolls inside the pause) + P.C. Richard 3 AUG 2026 $319.96 / us.tcl.com $319.99 chip | "Watch it fall. $319.96." |
| 4 | 0:12.0 | 0:16.0 | GAP | Firefly: bezel macro, parallax L | `55-INCH CLASS` / `3840×2160` / `ENTRY 4K LINE` + MSRP-vs-shelf asterisk chip (LG 55UH7700 $1,799→$999 TechRadar) | "Same size. Same resolution. Same tier." |
| 5 | 0:16.0 | 0:20.0 | EXCAVATION | Firefly: rising goods vs sinking TV | `EVERYTHING ELSE +38.2%` (amber) / `TVs ↓` (cyan) + BLS CUUR0000SA0 chip | "Almost everything got more expensive. This didn't. Why?" |
| 6 | 0:20.0 | 0:24.0 | EXCAVATION | Firefly: infinite panel hall, dolly | `ONE CAUSE: PANEL FACTORIES OUTBUILT THE MARKET` + VIZIO 10-K FY2023 / SEC EDGAR chip | "One reason: panel factories outbuilt the market." |
| 7 | 0:24.0 | 0:28.0 | EXCAVATION | Firefly: hall going dark | TrendForce 3 JAN 2024 exit-quote chip | "The glut ran so deep, Korean panel makers left the business." |
| 8 | 0:28.0 | 0:32.0 | PROOF FLEX 📊 | **REAL `assets/price-chart-2016-2026.png`, slow push** | `−66.9%` (cyan) + "after inflation" + arithmetic chip; keep chart footer visible | "Our receipts: down 66.9%, after inflation." |
| 9 | 0:32.0 | 0:37.0 | PROOF FLEX | Firefly: twin monoliths, crane up | `−66.9% (REAL)` vs `−67.1% (NOMINAL)` + `0.2 APART` + **required chip: BLS CUUR0000SERA01, NOMINAL, CONSTANT-QUALITY · REAL FALL −76.2%** | "BLS's television index: 67.1%. Two methods. 0.2 apart." |
| 10 | 0:37.0 | 0:39.0 | VERDICT ✅ | Firefly: lone TV, cyan glow, hold | **STILL CHEAP stamp** (studio asset, cyan, 4°, 2px shake) — lands on the frame "cheap" is spoken | "Verdict: STILL CHEAP." |
| 11 | 0:39.0 | 0:42.0 | HANDOFF | Firefly: watchful glowing screen | caption only, no data | "One catch. Why it's this cheap costs you something else." |
| 12 | 0:42.0 | 0:44.0 | HANDOFF | Firefly: glow dies to black | `NEXT DIG` end card, cut to black | "Next dig." |

**Cut discipline (motion-director):** never cut during a [PAUSE] — all seven pauses live INSIDE
shots (the shot 2→3 cut lands after "in today's money", before "Watch it fall"; the odometer
rolls inside shot 3's pause; the stamp beat owns shot 10 whole). Fine-trim every boundary to
the actual VO waveform after TTS render — the table above is the target grid, the voice is
the clock.

---

## AUDIO NOTE

- **Voice:** the founder's cloned narrator in their ElevenLabs account. `voice_id`: per
  docs/08-voice-casting.md §2.4 Step 8 (copy verbatim from the ElevenLabs library — do not guess).
- **Settings (docs/08 §3, exact):** `stability: 0.42` · `similarity_boost: 0.85` · `style: 0.15`.
  A/B only one perturbation per setting if the read misbehaves (stability ±0.10, similarity ±0.05).
- **TTS input = the v3 spoken text only** (no beat labels, no stage directions), numerals
  spelled as spoken per docs/08 §5.1 — the read contains no numerals:

  > Twenty sixteen. April. A wall of brand-new four-K TVs. [PAUSE] VIZIO's cheapest fifty-five
  > inch: nine sixty-seven fifty-eight dollars, in today's money. Watch it fall. [PAUSE] Three
  > nineteen ninety-six. [PAUSE] Same size. Same resolution. Same tier. Almost everything got
  > more expensive. This didn't. [PAUSE] Why? One reason: panel factories outbuilt the market.
  > The glut ran so deep, Korean panel makers left the business. Our receipts: down sixty-six
  > point nine percent, after inflation. BLS's television index: sixty-seven point one. [PAUSE]
  > Two methods. Point two apart. Verdict: [PAUSE] still cheap. One catch. [PAUSE] Why it's this
  > cheap costs you something else. Next dig.

  Render the seven [PAUSE] marks as real silence (ElevenLabs `<break>` tags or post-cut gaps
  ~0.5–0.7s each; pause 2 must be ≥0.8s — the odometer rolls inside it). [EMPHASIS] on
  "This didn't."
- Target ~44s total. If the render lands long, trim pause tails, never the words.

## UPLOAD BLOCK (reminder — see handoff-upload.md)

- **AI disclosure: ON.** The Firefly layers are generated; the platform "altered/synthetic
  content" flag is not optional for this episode.
- **Visibility: PRIVATE first.** QC pass against gate.json (C2 claim map, C3 chip-on-every-price-frame,
  stamp sync) before flipping public.
- Receipts in-frame are real: chart PNG, press-release stills, live-listing chip text —
  never regenerate them.

---

### Production notes / flags for downstream agents

1. **Odometer endpoints follow script v3, not the founder's earlier brief.** The v3 source map
   (row 4) locks the roll as `$967.58 → $319.96` (today's-money pair). The nominal `$699.99`
   is carried in shot 2's citation chip, so the number is still on screen. If the founder
   insists on `$699.99 → $319.96`, shot 2's hero must become $699.99 (nominal) and the
   "in today's money" sub-line moves — flag to `head-of-format` before changing.
2. **One odometer, one stamp, both studio assets.** Never restyled, never re-generated in
   Firefly — they are the two most recognizable moves the channel owns.
3. **No generated frame ever shows text, a logo, a face, or a 2016 storefront.** If Firefly
   hallucinates lettering on a screen or bezel, regenerate or clone it out before edit —
   compliance Rule 6 (adapted) treats a legible fake brand as a fail.
4. **c5 `inflation_adjusted_value: 67.4` discrepancy** (matches neither 76.2% text nor the
   arithmetic) is inherited from evidence.json — nothing in this pack uses that field;
   `trend-archaeologist` still owes the reconciliation.
