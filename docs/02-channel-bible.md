# 02 — Channel Bible

The single source of truth for what Price Archaeology is. Every agent reads this. If a proposed
video violates this document, `head-of-format` kills it — no appeal, no "just this once."

---

## 1. Identity

| | |
|---|---|
| **Channel** | Price Archaeology |
| **Handle** | `@PriceArchaeology` |
| **Tagline** | *We dig up what things used to cost.* |
| **Bio** | Ten years ago, this cost less. We find the receipt. New dig every day. |
| **Anchor year** | 2016 (config-driven, rolling 10-year window) |
| **Format** | 9:16 vertical, 1080×1920, 30–45 seconds |
| **Cadence** | 1/day at launch. **Hard ceiling 2/day** — see `docs/05-compliance.md` |

### The one-sentence test

> *"In 2016, [OBJECT] cost [PRICE]. Here's the receipt, here's what happened, and here's what
> you should do about it."*

If a video idea does not fit that sentence, it is not an episode. This test has killed more bad
ideas than any other rule in this document — use it first, before any research is commissioned.

---

## 2. The four segments

### 🔻 THE DIG — *things that got worse* (40% of slate)
The core format. An everyday object that has become meaningfully more expensive or worse in
value. Delivers validation and rage. Highest reach, zero purchase intent.
**Ends on:** the honest reason why, not a rant.

### 🟢 STILL CHEAP — *things that collapsed* (40% of slate)
**This is the revenue engine.** Objects that are dramatically cheaper or better-per-dollar than
in 2016 — TVs, storage, solar, LEDs, sequencing, 3D printing. Delivers delight and permission
to buy.
**Ends on:** "this is the cheapest this has ever been" + the affiliate shelf.

### ⚫ EXTINCT PRICES — *gone at any price* (10%)
Things you genuinely cannot buy in 2026 at any price: the single $9.99 streaming bundle, the
headphone jack, unlimited data that was actually unlimited, a phone with a replaceable battery.
Pure nostalgia and format identity. Strong comment-bait.
**Ends on:** the trade we made without voting on it.

### 🟡 TIME CAPSULE CART — *the series anchor* (10%)
Rebuild a complete 2016 basket — a grocery run, a back-to-school haul, a Friday night out — and
price it in 2026. Runs weekly, numbered (`CART #007`), and is the primary subscribe driver
because it is explicitly serial.
**Ends on:** the total, and the total only. No commentary. The number does the work.

---

## 3. The beat sheet

Every episode. No exceptions. Timings are enforced by `script-editor`.

```
┌ 0:00–0:03  ARTIFACT ──────────────────────────────────────────────┐
│  Period footage or the object, cold. One line. A number on screen. │
│  NO channel intro. NO "hey guys." NO logo. The number is the logo. │
│  → "In 2016, AirPods cost $159."                                   │
├ 0:03–0:08  THE GAP ───────────────────────────────────────────────┤
│  Today's number lands next to it. Let the contrast sit 1 full beat.│
│  → "Today, the same tier is $XXX."                                 │
├ 0:08–0:26  THE EXCAVATION ────────────────────────────────────────┤
│  The evidence + the one surprising cause. Exactly ONE cause —      │
│  not three. The archived listing appears on screen here.           │
│  This is the segment that makes us un-copyable. Do not rush it.    │
├ 0:26–0:36  THE VERDICT ───────────────────────────────────────────┤
│  A stamp. RIPOFF / FAIR / STILL CHEAP / EXTINCT. Said out loud.    │
├ 0:36–0:42  THE HANDOFF ───────────────────────────────────────────┤
│  One question to the comments, or the affiliate line. Never both.  │
└───────────────────────────────────────────────────────────────────┘
```

**Non-negotiables**
- The first spoken word is a **year or a number**. Never a greeting.
- **One cause only.** Two causes is an essay; an essay is a scroll.
- The verdict stamp is spoken *and* on screen, at the same frame.
- Total script: **95–130 words.** Below 95 it's thin; above 130 it rushes at ~150wpm.
- Every price on screen carries its source, small, bottom-left. Always. Even when ugly.

---

## 4. Voice

**Sounds like:** a museum curator who is quietly furious about your rent.

Precise, dry, evidence-first. Never a hype voice. Never "INSANE" or "you won't BELIEVE."
The numbers are already shocking — the delivery must be calm or the shock is wasted. Confidence
comes from the citation, not the adjectives.

| Do | Don't |
|---|---|
| "That's a 218% increase. Here's the filing." | "That's INSANE!!" |
| "Three things changed. Only one mattered." | "Let me explain everything…" |
| "Verdict: ripoff." | "Honestly guys, it's kind of a ripoff?" |
| Name the number first | Build up to the number |
| Concede when it's actually fair | Manufacture outrage |

**Conceding is a feature.** When something is genuinely worth more now, the verdict is FAIR and
we say so. A channel that always says "ripoff" is a rant channel. A channel that sometimes says
"fair" is a *source* — and sources get cited, screenshotted, and trusted.

### Banned
Greetings. "Let's dive in." "Stay tuned." "Like and subscribe" as speech. Any claim without a
source. Fake urgency. Round numbers when the real number is known. Rage about anything we
haven't verified.

---

## 5. Visual system

**Principle:** *archive on the bottom, data on the top.* Period footage plays underneath;
typography is the interface layer above it. Never blend them — the contrast between grainy
2016 footage and crisp 2026 data *is* the visual idea.

| | |
|---|---|
| **Base** | Full-bleed archival footage, desaturated to ~40%, slight grain |
| **Data layer** | Flat, sharp, pure white, no drop shadow, no glow |
| **Accent — past** | Faded amber `#C8964B` — every 2016 number |
| **Accent — present** | Hard cyan `#00E5FF` — every 2026 number |
| **Alarm** | `#FF3B30` — deltas above +100% only. Rare on purpose |
| **Ground** | Near-black `#0A0A0A` |

**Type:** one grotesque family, two weights. Numbers set in tabular figures at 3–4× the body
size. The number is the hero of every frame; text explains the number, never competes with it.

**The signature move — the odometer.** Prices *count up* from the 2016 figure to the 2026 figure
in a mechanical roll, ~0.8s, ease-out. This is the channel's visual trademark: one motion, used
identically every episode, instantly recognizable in a feed at 2× scroll speed. Implemented once
in Remotion as `<PriceOdometer>` and never restyled.

**Verdict stamp:** rotated 4°, hard-edged, slams in with a 2px offset shake. Physical, like an
inspector's rubber stamp. Amber for RIPOFF, cyan for STILL CHEAP, grey for EXTINCT, white for FAIR.

**Citation chip:** bottom-left, 14px, 60% opacity, always present when a price is on screen.
It should feel like a museum placard. Ugly is acceptable; absent is not.

---

## 6. Titles & packaging

Format: `[OBJECT] in 2016 vs 2026` — plain, searchable, no clickbait punctuation.

Good:
- `AirPods cost $159 in 2016`
- `The 2016 grocery cart, priced today`
- `Why 4K TVs collapsed in price`

Bad:
- `You WON'T BELIEVE what AirPods cost in 2016 😱`
- `The TRUTH about inflation`

We are optimizing for a viewer who will *return*, and increasingly for Shorts surfacing as
answers in search. Clickbait wins the impression and loses the brand. The number in the title
does more work than any emoji ever will.

---

## 7. The line we don't cross

We are not an inflation-politics channel. We report verified numbers and name the single
mechanical cause — a tariff, a patent expiry, a supply chain, a subsidy, a licensing change.
We do not assign blame to political parties or run partisan framing.

This is a commercial decision before it is an ethical one: the moment we pick a side we lose
half the audience, all the brand safety, and the ability to be cited as a source. The numbers
are more damning than any commentary, and they travel further.
