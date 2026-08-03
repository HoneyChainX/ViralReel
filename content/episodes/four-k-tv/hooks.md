# Hooks — 001 `four-k-tv`

**Writer:** hook-writer · **Session:** 2026-08-03 · **Segment:** STILL CHEAP
**Source of every number:** `content/episodes/four-k-tv/evidence.json`. No figure below appears
that is not in that file or arithmetic performed only on figures in that file (shown inline).

## The number pool (nothing else may be spoken)

| Figure | Claim | What it actually is |
|---|---|---|
| **$699.99** | c1 | VIZIO E55u-D0, 55" 4K, **MSRP at announcement**, 19 Apr 2016 |
| **$569.99** | c1 | E55-D0, the **1080p** sibling, same release. Difference: exactly **$130.00** |
| **$967.58** | c1 | The $699.99 in July-2026 dollars (BLS CPI-U `CUUR0000SA0`, factor 1.382273) |
| **$319.96** | c2 | TCL 55Q651G, **live shelf price**, P.C. Richard & Son, 3 Aug 2026 |
| **$319.99** | c2 | Same SKU, us.tcl.com, same day |
| **$299.99** | c2 | Hisense 55QD65QF, Newegg, same day (tier corroboration, **new** not refurb) |
| **$1,799** | c3 | LG 55UH7700, premium 4K LED, 10 Mar 2016 |
| **$999** | c3 | TechRadar's in-model-year street price for that same LG — **the MSRP asterisk** |
| **$2,299** | c4 | Samsung UN55KS9000, 2016 flagship flat 55" LED |
| **$1,297.99** | c4 | Samsung QN55QN90F, Newegg, 3 Aug 2026 |
| **283.408 → 93.176** | c5 | BLS televisions index `CUUR0000SERA01`, Apr 2016 → Jul 2026 |
| **−67.1% / −76.2%** | c5 | That index, nominal / after general inflation |
| **$380.03** | c1−c2 | 699.99 − 319.96 |
| **+38.2%** | c1 | CPI-U all items, Apr 2016 → Jul 2026 (330.724 / 239.261) |

**The one live truth hazard in this pack:** every 2016 figure is a manufacturer MSRP; every 2026
figure is a shelf price. Street prices fell inside 2016 too — the same LG that launched at $1,799
was $999 in review. Any hook that says a 2016 TV *"cost"* $699.99 is shading by a few points.
Hooks that say *"listed at"* / *"launched at"* are clean. This is scored, not ignored.

---

### V1
SPOKEN: "In 2016, the cheapest 55-inch 4K TV Vizio sold listed at $699.99."
ON SCREEN: `$699.99` (amber) / sub: "VIZIO E55u-D0 · 55-inch · 4K · April 2016" / chip: "VIZIO press release, 19 Apr 2016"
Stop 3 | Gap 3 | Truth 5 | Voice 5 | Total 16
> The format-default. Flawless and slightly inert: $699.99 for a 2016 TV is exactly what a viewer would guess, so the number confirms rather than stops.

### V2
SPOKEN: "$699.99 in 2016. $319.96 today. Same size, same resolution."
ON SCREEN: `$699.99` (amber) → odometer → `$319.96` (cyan) / chips: "VIZIO, 19 Apr 2016" · "P.C. Richard & Son, 3 Aug 2026"
Stop 3 | Gap 4 | Truth 5 | Voice 4 | Total 16
> Both held axes are literally true (55-inch, 3840×2160). Carries the whole episode in nine words. Still leads with an unsurprising number.

### V3
SPOKEN: "$699.99 in 2016. $319.96 now. Everything else went up 38%."
ON SCREEN: `−54.3%` (cyan) vs `+38.2%` (amber) / chip: "BLS CPI-U CUUR0000SA0"
Stop 3 | Gap 5 | Truth 4 | Voice 4 | Total 16
> The wrong-direction pattern, and the contrast is the real story. Truth 4 not 5: "everything else" is a gloss on CPI-U all items, which is an average, not everything.

### V4
SPOKEN: "$699.99 — that's the line in Vizio's own April 2016 press release."
ON SCREEN: `assets/2016-press-release.png`, the $699.99 row boxed / chip: "VIZIO press release, 19 Apr 2016"
Stop 3 | Gap 4 | Truth 5 | Voice 5 | Total 17
> Receipt pattern, and we have the artifact on disk. Note the render is a captured-HTML render, not a Wayback capture — it must never be captioned as an archive grab.

### V5
SPOKEN: "283.408 in 2016. 93.176 today. That's the government's television price index."
ON SCREEN: `283.408 → 93.176` / chip: "BLS CUUR0000SERA01, Dec 2024=100"
Stop 3 | Gap 4 | Truth 5 | Voice 5 | Total 17
> Maximum curator. Unimpeachable, and it is the constant-quality number the whole episode rests on. But unitless index values do not stop a thumb — they read as noise for the first second, and the first second is all there is.

### V6
SPOKEN: "76.2%. That's how far television prices fell after inflation since 2016."
ON SCREEN: `−76.2%` (cyan) / sub: "constant quality, after general inflation" / chip: "BLS CUUR0000SERA01 ÷ CUUR0000SA0"
Stop 3 | Gap 4 | Truth 5 | Voice 4 | Total 16
> The biggest honest number in the pack, and the least tangible. Percentages are conclusions; the channel's currency is prices.

### V7
SPOKEN: "$1,799 for a 55-inch TV. LG's, March 2016."
ON SCREEN: `$1,799` (amber) / sub: "LG 55UH7700 · SUPER UHD · 10 Mar 2016" / chip: "LG Electronics USA press release PDF, 10 Mar 2016"
Stop 4 | Gap 4 | Truth 5 | Voice 5 | Total 18
> A genuinely stopping 2016 number, from LG's own PDF, and it pre-empts the cherry-picking accusation by opening on the premium tier. Cost: the episode's actual object is the $699.99 entry set, so the hook promises a different video than the one that follows.

### V8
SPOKEN: "$2,299 was Samsung's best 55-inch in 2016. Today's is $1,297.99."
ON SCREEN: `$2,299` → `$1,297.99` / chips: "Forbes, 12 Apr 2016" · "Newegg, 3 Aug 2026"
Stop 4 | Gap 4 | Truth 4 | Voice 4 | Total 16
> Flagship-to-flagship, exactly as c4 states it. Truth 4 because the 2016 side is secondary-sourced (Forbes) — the only headline number in the pack without a primary behind it.

### V9 ★
SPOKEN: "$967.58, in today's money. That's Vizio's cheapest 55-inch 4K TV, 2016. It's $319.96 now."
ON SCREEN: `$967.58` (amber, tabular) / sub: "55-inch 4K TV, April 2016 — in July 2026 dollars" / chip: "VIZIO press release, 19 Apr 2016 · BLS CPI-U CUUR0000SA0" → odometer rolls down to `$319.96` (cyan) / chip: "P.C. Richard & Son, 3 Aug 2026"
Stop 5 | Gap 5 | Truth 4 | Voice 5 | Total 19
> $967.58 is a number the viewer's model of the world rejects on contact — nobody's mental price for a TV starts with a 9 — and rejection is what buys the second second. The qualifier rides inside the hook, at word four, so a viewer who bounces at 0:03 has still heard "in today's money."

### V10
SPOKEN: "$319.96 buys a 55-inch 4K TV today. In 2016 that wasn't half of one."
ON SCREEN: `$319.96` (cyan) / sub: "half of $699.99 is $349.99" / chips: "P.C. Richard & Son, 3 Aug 2026" · "VIZIO, 19 Apr 2016"
Stop 4 | Gap 5 | Truth 5 | Voice 5 | Total 19
> Arithmetic the viewer finishes themselves, which is the most reliable engagement mechanic there is (½ × $699.99 = $349.99 > $319.96 — correct, and only pack numbers used). The one objection: it opens on 2026, and the ARTIFACT beat is supposed to open in the past.

### V11
SPOKEN: "$569.99 bought a 55-inch Vizio in 2016. Four K cost $130 more."
ON SCREEN: `$569.99` → `$699.99` / sub: "E55-D0 (1080p) · E55u-D0 (4K) — same release" / chip: "VIZIO press release, 19 Apr 2016"
Stop 3 | Gap 5 | Truth 5 | Voice 5 | Total 18
> The best excavation in the pack: $130.00 exactly, both lines on the same page, and it quietly documents the tier trap that would have sunk this episode. But it takes three seconds just to establish which TV we mean, and three seconds is the whole budget.

### V12
SPOKEN: "$380.03 came off the price of a 55-inch 4K TV since 2016."
ON SCREEN: `−$380.03` (cyan) / sub: "$699.99 (Apr 2016) → $319.96 (Aug 2026)" / chips: both
Stop 4 | Gap 4 | Truth 4 | Voice 4 | Total 16
> A delta stated as money rather than percent, which travels better. Truth 4: it is an MSRP-minus-shelf-price subtraction, and the pack says plainly that the street-to-street fall is smaller.

---

## RECOMMENDED: **V9**

This episode's nominal collapse — $699.99 to $319.96 — is real but unsurprising, and a hook that
opens on $699.99 confirms what the viewer already assumes about TVs instead of contradicting it;
$967.58 is the only number here that produces the "that's wrong" reflex, and that reflex is the
entire mechanism of a stop. It is also the *correct* comparison rather than a decorative one —
the deflator is BLS CPI-U `CUUR0000SA0` computed in the pack, the qualifier is spoken aloud inside
the hook rather than buried in a chip, and the payoff number ($319.96) is a live shelf price from a
named seller on a named day.

**Strongest counter-argument against my own pick:** $967.58 is a *derived* number, and this channel's
promise is "we find the receipt." No receipt anywhere says $967.58 — the citation chip has to read
*BLS CPI-U*, not *a listing*, which is the one frame in this episode where a hostile viewer can say
"you made that up." And it inherits the pack's live asterisk twice over: it is a deflated **MSRP**,
while its comparison is a **shelf price**, and the pack itself proves 2016 street prices fell far
below MSRP within the model year ($1,799 → $999 on the LG). If the founder weights receipt-purity
over stopping power, **V10** is the pick — every number in it is a real price someone actually paid
or was actually asked, and its gap is arithmetic the viewer completes unaided. **V1** remains the
zero-risk fallback and should be shot as an alternate take regardless; it costs eight seconds of VO.

**Do not use V5 or V6 as the opening line.** Both are the most defensible numbers in the pack and
both belong on screen during THE EXCAVATION — index values and percentages are conclusions, and a
conclusion cannot be the first three seconds.
