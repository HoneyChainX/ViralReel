# 09 — Adobe Creative Cloud

The founder subscribed to Creative Cloud, which put four Adobe connectors in reach. This is what
the studio uses, what it refuses, and why.

**Account verified as `auth`** (full signed-in account, not a guest session).

---

## The decision in one line

> **Fonts and grading: yes. Generation and Stock-as-archive: never.**

Creative Cloud is a fixed subscription already being paid, so fonts and image treatment sit in
the same category as ElevenLabs — real capability at **no marginal cost per video**. The
`$0.00` guarantee in `docs/01-strategy.md` holds.

---

## What we adopted

### 1. Adobe Fonts — closes a real gap

The channel bible specified *"one grotesque family, two weights, tabular figures"* and **named no
family**, because there was no licensed one to name. `brand/tokens.css` carried an honest
`<<FILL>>` placeholder rather than a guess.

**Resolved: Acumin Pro.** Entitlement verified per-weight against this account — `Regular`,
`Semibold`, `Bold`, `Black`, and `AcuminProCond-Bold` all returned `available: true`.

The deciding factor was not taste. Acumin ships **true tabular lining figures**.
`<PriceOdometer>` rolls digits for 800ms; on proportional figures the column widths shift
mid-roll and the number visibly jitters. That roll is the channel's signature motion, so a
family without `tnum` is unusable here regardless of how it looks standing still. Archivo, IBM
Plex Sans and Roboto Mono are all entitled and were all viable; Acumin won on figure quality.

> Inter is also entitled but was skipped: its lookup resolved to the PostScript name
> `Sinter-Bold`, which doesn't match the family and wasn't worth trusting unverified.

**Two loading paths, and they are not equivalent:**

| Surface | Path |
|---|---|
| **Remotion render** (the pipeline) | Sync Acumin Pro locally via the Creative Cloud desktop app |
| HTML / Adobe Express | Typekit kit `meo1cll`, families `acumin-pro` / `acumin-pro-condensed` |

The render path matters more. A webfont fetch inside the render is a network dependency in a
pipeline that produces a video every day — and a font that fails to load mid-render yields a
**silently wrong video, not an error**. Sync it locally; keep the kit for HTML surfaces.

### 2. Image treatment — makes the look repeatable

`image_apply_adjustments`, `image_add_grain`, `image_apply_monochromatic_tint`. The bible calls
for archival stills desaturated ~40% with light grain; these turn that from a per-episode
judgement into a fixed recipe, now written into `archive-sourcer`'s charter.

Applies to stills we already legitimately hold — the Wayback screenshot, the receipt, period
photographs. Not to video; the vendor tools are image-only.

---

## What we refuse

### `image_generative_expand` — banned outright

Outpainting invents pixels beyond the frame edge. Using it to extend a 2016 storefront photo to
fill a 9:16 frame would **fabricate visual evidence** on a channel whose entire defence is that
its evidence is checkable. If an archival frame doesn't fill vertical: crop, letterbox, or source
another clip. Those three, nothing else.

Worth noting: Adobe's own routing documentation states that **most generative AI is unavailable
in this environment**, with `image_generative_expand` as the sole exception. So the risk surface
is one named tool rather than a whole category — which is why banning it by name is sufficient.

### Adobe Stock as period material — banned; Stock disabled by default

Stock is modern imagery. Presenting it as 2016 material is the same falsification by an easier
route — and *easier* is the problem. `archive-sourcer` already bans passing modern footage as
period, but Stock makes that ban simple to break by accident, because the image is high-quality
and one call away.

`stock_enabled: false` in `config/channel.yaml`, for two reasons: licensing consumes credits (the
only thing here that would break the $0 model), and a disabled default means using it takes a
deliberate act rather than a reflex.

### The line

**Treating a real photograph is grading. Extending one is fabrication.** The test is whether a
pixel describes something that was actually photographed.

---

## Not adopted — the other three connectors

**Adobe Experience Manager**, **Journey Optimizer**, and **Marketing Agent** are enterprise CMS
and marketing-automation platforms: customer journeys, campaign orchestration, org-scale content
management. None of it applies to a Shorts channel run by one founder.

They have not been called, and Journey Optimizer in particular requires selecting a sandbox
before any operation — not something to do exploratory against a live marketing system.

---

## Enforcement

`config/channel.yaml` carries `stock_enabled: false` and `generative_expand_enabled: false`.
CI asserts both, alongside the existing compliance defaults, so neither can be flipped quietly —
the same guard pattern that now protects the throughput cap and AI disclosure.
