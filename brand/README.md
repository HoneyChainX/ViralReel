# brand/ — the Price Archaeology visual system

Owner: `brand-designer`. Approved by the founder on the visual-system gate (`docs/06-runbook.md`,
Day 1, decision 2).

This directory is the built form of `docs/02-channel-bible.md` §5. The bible says what the system
is; these files *are* the system. Colour values are read from `config/channel.yaml` — that file is
the source of truth, and anything here that disagrees with it is a bug in here.

| File | What it is | Status |
|---|---|---|
| `tokens.css` | Custom properties: colour, type scale, motion, layer rules | **Locked** |
| `avatar.svg` | Channel avatar, 800×800, built to survive 48px | **Locked** |
| `banner.svg` | Channel banner, 2560×1440, safe area respected | **Locked** |
| `verdict-stamps.svg` | RIPOFF / STILL CHEAP / EXTINCT / FAIR | **Locked** |
| `PriceOdometer.tsx` | The signature move, as a Remotion component | **Locked** |

"Locked" means: change it once, for every episode, by changing the bible and this directory
together. It does not mean frozen forever — it means never changed for one video.

---

## The rule that matters most

**One-episode exceptions are forbidden.**

Not discouraged — forbidden. If an episode needs amber on a 2026 figure "because the frame looks
better," the answer is no. If a verdict needs a fifth colour, the answer is no until the fifth
colour is in `config/channel.yaml` and in the bible, at which point it applies to every episode
that follows.

The reason is mechanical, not aesthetic. Amber-past / cyan-present only works because after ten
episodes the audience reads the colour before the label. That recognition is built by repetition
and destroyed by variation, and it is worth more than any single frame it costs. A system that
bends per episode is a mood board, and a mood board is not recognisable at 2× scroll speed.

The same logic covers the odometer: one motion, used identically, is what makes a two-second
glimpse of this channel identifiable. `PriceOdometer` deliberately exposes no colour, easing, or
physics props. If you want a prop for one of those, you want a bible change.

---

## Using them

### `tokens.css`

Import once at the root of the Remotion project, then reference the variables. Never hardcode a
hex anywhere else in the codebase — a hex in a component is a token that will drift.

```css
@import "../../../../brand/tokens.css";
```

Authored in frame pixels for the 1080×1920 delivery frame (`config/channel.yaml` → `format`).
Consumers at other raster sizes scale the values; they do not re-pick them.

The odometer needs real values rather than `var()` references in order to interpolate colour, so
`PriceOdometer.tsx` mirrors the colour tokens as TS constants (`PA_TOKENS`). Those two lists must
agree with `config/channel.yaml`. To check all three at once:

```bash
grep -A6 'colors:' config/channel.yaml
grep -n 'pa-color-' brand/tokens.css
grep -n -A6 'PA_TOKENS' brand/PriceOdometer.tsx
```

### `avatar.svg`

YouTube wants at least 98×98 and renders it as a circle; 800×800 is the upload size, 48px is the
size that actually matters — comment rows, search results, the subscribe strip. The mark is three
shapes and two colours for exactly that reason: a crisp cyan slab (2026) over a torn amber slab
(2016), split by the gap. Everything sits inside a circle of radius ~304 of the 400 available, so
the crop never clips it.

Check it at real size before approving anything: view the SVG at 48px, not at 100%.

### `banner.svg`

2560×1440 with the essential content inside the centred **1546×423** safe area (x 507–2053,
y 508.5–931.5) — the only rectangle a phone shows. The full width carries the colour grammar
(amber `2016` left, cyan `2026` right) and the strata bands, so the TV/desktop crop earns its
extra pixels without the mobile crop depending on them.

There is a safe-area guide in the file as `<g id="safe-area-guide" display="none">`. Flip it to
`inline` to check a change, flip it back before export.

No price appears on the banner, on purpose. Every number this channel shows carries a citation
(`docs/05-compliance.md`, C3), and a banner cannot carry one. Years are configuration; prices are
evidence.

### `verdict-stamps.svg`

The deliverable is the four `<g id="stamp-*">` definitions in `<defs>`, each centred on its own
origin:

```svg
<use href="#stamp-still-cheap" transform="translate(540, 1180)"/>
```

The 2×2 layout and the captions (`#sheet-annotations`) are a contact sheet for review — hide them
before rasterising anything for production.

Rotation is 4° clockwise (`brand.stamp_rotation_deg`). The 2px offset shake on entry lives in
Remotion, not in the SVG (`--pa-stamp-shake-px`). The stamp slams; it never fades in, never
scales up softly. A rubber stamp is an impact.

### `PriceOdometer.tsx`

Copy or symlink into the Remotion composition tree used by the render
(`vendor/openmontage/remotion-composer/src/`) and use it wherever a price appears:

```tsx
<PriceOdometer from={159} to={249} currency="$" />
```

- `from` / `to` — major currency units. Both must be sourced figures. This component renders
  whatever it is given; `docs/05-compliance.md` C2 is what stops it rendering a number with one
  source behind it.
- `currency` — rendered verbatim. No symbol is inferred from a currency code, ever.
- `durationMs` — defaults to `brand.odometer_ms` (800). The prop exists so the config value can be
  threaded through, not so an episode can decide it feels better at 1200.
- `decimals` — inferred (0 when both figures are integers, otherwise 2) unless you pass it.

Also exported: `PA_TOKENS`, `PA_ODOMETER_MS`, `PA_FONT_STACK`, and `formatPriceValue()` — use the
last one for captions and citation chips so the spoken number, the burned-in caption and the
wheels can never disagree.

Digits live in fixed-width, overflow-hidden slots with tabular figures enforced on the container.
Leading zeros are hidden with `opacity: 0` rather than removed, so a number crossing a power of
ten never shifts sideways; the currency mark steps one column left instead. Wheels above the least
significant one stay locked and carry only across their final unit — a price at rest reads as a
crisp digit, and only a price in motion is allowed to smear.

---

## Open items — one placeholder left

**1. ~~The grotesque family is not chosen.~~ RESOLVED: Acumin Pro.** Licensed through the
founder's Creative Cloud plan; entitlement verified per weight against this account
(`Regular`, `Semibold`, `Bold`, `Black`, `AcuminProCond-Bold` — all `available: true`).

Chosen for true tabular lining figures — with a correction from the Fable-5 review (B1a): tnum is
**not** what keeps the odometer roll stable. The DigitWheels are fixed-width slots, so the roll
is stable in any font. Tabular figures earn their keep *at rest* — letterfit and consistency
across captions, citation chips and multi-figure frames. Still required; for the true reason.

**Platform constraint (review B1b — a reversal of the original loading plan):** the Creative
Cloud desktop app does not exist for Linux, so on a Linux render host Acumin **cannot be synced**
and every render silently falls back to Liberation Sans. That fallback is typographically safe
(digit widths measured uniform in both weights, no serif degrade) but it is a different face.

- **Render in Acumin** → a CC-synced macOS/Windows machine, or separately licensed OTFs installed
  into fontconfig on Linux. `scripts/doctor.sh` reports which state the host is in — the failure
  this guards against is *silent*, not loud.
- **Render on Linux without those** → Liberation Sans ships, deliberately and loudly. The founder
  decides whether that's acceptable per batch (`docs/DECISIONS.md`).
- **HTML / Express:** Typekit kit `meo1cll` — `<link rel="stylesheet" href="https://use.typekit.net/meo1cll.css">`,
  families `acumin-pro` and `acumin-pro-condensed`. Never in the render path.

`--pa-font-grotesque` lists the kit name, then the installed name, then real OS grotesques, so it
degrades to something correct rather than to a serif. Full reasoning: `docs/09-adobe-connectors.md`.

**2. EXTINCT grey is derived, not locked.** The bible assigns EXTINCT a grey; `config/channel.yaml`
has no grey key, so there was nothing to read. Rather than invent one, `#848484` is the floor of the 50/50
mix of `brand.colors.data` and `brand.colors.ground` — reproducible from two locked tokens.

To make it enforceable, `strategy-lead` adds to `config/channel.yaml`:

```yaml
brand:
  colors:
    extinct: "#848484"
```

Until then, treat it as provisional — and still do not substitute a different grey per episode.

---

## One flag for `head-of-format`

`--pa-text-cite: 14px` is quoted verbatim from bible §5 and has been implemented verbatim. On a
1080-wide frame that is 1.3% of frame width — legible in a full-screen pause, marginal mid-scroll.

It has deliberately **not** been changed here. The citation chip is the brand, its size is a format
decision, and quietly resizing it locally is precisely the drift this directory exists to prevent.
If it should be bigger, change the bible and the token together, once, for every episode.

---

## How this was checked

The colour values were read out of `config/channel.yaml`, not typed from memory.

`PriceOdometer.tsx` typechecks clean under the composer's own strict config against the installed
Remotion 4.0.484 and React 18, and was rendered frame-by-frame through `react-dom/server` (real
`interpolate` / `interpolateColors` / `Easing`, hooks stubbed) to confirm: `$159` amber at frame 0,
`$249` cyan at frame 24 at 30fps, correct digits at every sampled frame in between, leading-zero
suppression across a power-of-ten crossing, and `$9.99` sitting crisp at rest.

That probe is not committed — it depends on `vendor/openmontage/remotion-composer/node_modules`,
which is not this repo's to own. Re-create it there if you change the roll maths.

**No SVG rasteriser is installed in this environment**, so the three SVGs have not been converted to
PNG here and no conversion command is claimed to work. YouTube wants raster uploads for avatar and
banner; render them with whatever you install (`rsvg-convert`, `resvg`, Inkscape, or a headless
Chromium screenshot) and check the type renders in a grotesque rather than falling back to a serif.
If your rasteriser has none of the stack, convert the text to outlines before upload.
