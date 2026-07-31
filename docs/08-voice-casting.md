# 08 — Voice Casting

> **Status: DECIDED.** The founder delegated this call to the studio. `voice-director` made it.
> This document is the brief, the decision, the settings, and the audition. It is binding on
> every episode until `strategy-lead` deliberately changes it here.
>
> One thing in this document is *not* decided, and cannot be: the actual `voice_id`. That value
> exists only inside the founder's own ElevenLabs account. §2.4 is the procedure that resolves
> the criteria below to a real ID. **Nobody writes a voice ID into this repo that they did not
> read out of a live API response.** A guessed identifier on a provenance channel is the same
> failure as a guessed price.

---

## 1. The brief

The bible gives one line (§4): **a museum curator who is quietly furious about your rent.**

That is a good target and a useless casting filter. Translated into things you can actually hear
in a 30-second demo:

### 1.1 The measurable criteria

| Dimension | Target | Why this and not the neighbouring value |
|---|---|---|
| **Perceived age** | 38–48 | Under 35 has no archival authority — it sounds like someone reporting a fact they just learned. Over 55 tips into "documentary narrator," a register the audience has heard so often it stops carrying information |
| **Placement** | Chest-dominant, low in the speaker's own comfortable range | Head-voice and nasal placement lose definition first when the mix is normalised to −14 LUFS. Low-in-range also produces restraint for free — a speaker at the bottom of their range physically cannot get excited |
| **Timbre** | Matte. Dry-warm, not round-warm | Round/polished timbre reads as advertising. Matte reads as a person with a clipboard |
| **Pace** | 145–155 wpm sustained, **variable** | `read_wpm: 150` in config. The variance is the requirement: figures 15–20% slower than prose. A candidate with one speed is disqualified, however good the tone |
| **Accent** | General American, low-regional | Largest Shorts audience, and regionality becomes a personality that competes with the number. The number is the personality |
| **Energy** | 3/10 | Not 1/10 — a flatline is the audible signature of the channels that got deleted (`docs/05-compliance.md`). 3/10 is *interested*, not *excited* |
| **Terminal intonation** | Falls. Every sentence. | This is the single most diagnostic trait in the whole brief. A curator states; they do not check whether you agree |
| **Consonants** | Plosives and final consonants survive at 150 wpm | "Sixty" must not become "sixdy." "Months," "tenths," "percent" must keep their terminal clusters |
| **Vocal fry** | Minimal, and never sentence-final | Fry is the standard failure mode of low-energy reads, and it lands exactly where the verdict word lands |
| **Sibilance** | Controlled; must not need de-essing | Our vocabulary is unusually sibilant: dollars, costs, percent, cheapest, sources |
| **Room** | Dry, close, no baked-in reverb or trailer EQ | Archival footage supplies the texture. The voice supplies none |

### 1.2 The disqualifiers

Any one of these ends the audition. Do not talk yourself past them because the tone is nice.

- **Uptalk.** Rising terminal inflection, at any frequency. Non-negotiable.
- **Breathy "storyteller."** Breathiness reads as intimacy; we are not intimate, we are correct.
  (Audible *breaths* are fine and even good. Breathy *tone* is not. Different things.)
- **Ad-read cadence** — the lilt that leans into the second half of a clause.
- **Trailer gravel.** Manufactured gravitas is the loud version of hype.
- **Perfect evenness.** A read with no micro-variation across 40 seconds is the slop signature.
  This is the failure mode people mistake for "professional."
- **Audible smiling.** Incompatible with a verdict.
- **Any non-native stress pattern on American currency or product names.**

### 1.3 The one thing that actually matters

**Can it read a figure aloud and sound like it knows what the figure means?**

Everything above is a filter. This is the test. Most voices — human and synthetic — read numbers
as a foreign object dropped into a sentence: same speed as the surrounding prose, no weight, no
landing. Every episode of this channel opens on a number (bible §3: *the first spoken word is a
year or a number*). A voice that cannot carry a figure cannot carry the format, and no amount of
warmth compensates.

---

## 2. The decision

### 2.1 The call

**Cast PROFILE A. Fall back to B only if A fails the audition on a disqualifier, and to C only if
both fail.** Do not blend profiles or "split the difference" — the point of a ranked list is that
the ranking gets used.

### 2.2 The three profiles

**PROFILE A — "The Curator"  ← CAST THIS**
Female, perceived 38–48, General American. Alto, placed low and forward. Matte, unpolished,
slightly cool. Minimal fry, hard terminal consonants, falling sentence ends. Reads as competent
and unimpressed.

*Why first:*
1. **Differentiation.** The price/inflation/explainer category is saturated with a single voice —
   mid-30s American male, mid-energy, mid-bright. In a feed at 2× scroll speed, sounding
   *unlike* the category is worth more than sounding marginally better within it.
2. **Distance from the slop signature.** The flat mid-male synthetic narrator is the voice viewers
   have learned to associate with mass-produced AI channels. That association is a real risk to a
   channel whose entire defence is that it is not one (`docs/05-compliance.md`).
3. **Intelligibility at low energy.** A low-placed alto keeps consonant definition at 3/10 energy
   through a phone speaker after −14 LUFS normalisation. A male bass at the same energy loses its
   final consonants first, which is precisely where our numbers live.
4. **The line fits.** "Quietly furious about your rent" is not a register most male explainer
   voices reach without either raising energy or adding gravel. Both are banned.

**PROFILE B — "The Registrar"  (fallback)**
Male, perceived 40–55, General American. Light baritone with the *bottom* audible but no
sub-bass and no gravel. Dry, procedural, slightly bored.

*When to use:* only if every Profile A candidate in the library fails on uptalk, fry, or
sibilance. *Cost of using it:* closer to the category default, so the differentiation argument is
lost. *Mitigation if cast:* hold pace at the slow end of the band (145 wpm) and be even stricter
about the flat verdict — a baritone that performs the verdict sounds like a movie trailer
instantly.

**PROFILE C — "The Conservator"  (last resort)**
Restrained British, non-RP, perceived 40–50, low-regional.

*Why third, despite being the most obviously "curator" option:* it gets institutional credibility
for free and then spends it. The brief is *quietly furious about **your** rent* — a British read
turns an American cost-of-living complaint into commentary about someone else's country. The
anger stops being shared and becomes observed. That is a real loss and it is why this profile
ranks below a compromise on gender.

### 2.3 Not eligible without an audition

Library labels describe a demo, not a read. A voice tagged **narration**, **documentary**,
**trailer**, **audiobook**, **conversational**, or **upbeat** is neither shortlisted nor excluded
by that tag. The tag is a hint about the demo clip somebody uploaded. Audition or discard.

### 2.4 Resolving the profile to a real `voice_id`

Run this. It is deterministic, it is reproducible, and it is the only path by which a voice ID
enters this repo.

> **Before you start:** never echo, log, paste, or commit `ELEVENLABS_API_KEY`. It lives in
> `vendor/openmontage/.env`, which is gitignored (`docs/04-stack.md`).

**Step 1 — enumerate the library. Read the response before trusting any field name.**

```bash
curl -sS -H "xi-api-key: $ELEVENLABS_API_KEY" \
     https://api.elevenlabs.io/v1/voices > /tmp/voices.json

jq 'keys' /tmp/voices.json          # confirm the envelope shape yourself
jq '.voices[0]' /tmp/voices.json    # confirm the per-voice field names yourself
```

If the shape differs from what follows, **trust the live response, not this document**, and then
fix this document. The endpoint path and response schema are the provider's to change; if the
path 404s, resolve the current one from the ElevenLabs API reference — do not guess a path.

**Step 2 — dump the candidate table.**

```bash
jq -r '.voices[] | [.voice_id, .name, .category, (.labels // {} | tostring)] | @tsv' \
   /tmp/voices.json | column -t -s $'\t'
```

Label vocabularies differ by account and library version. Use whatever keys actually came back to
do a first cut toward Profile A (roughly: adult female, American, low/calm/serious descriptors).
This cut is a convenience, not a decision — **labels never cast anyone.**

**Step 3 — audition the top 5 at OUR settings, on OUR script.**

The library preview clip is not evidence. It was generated from different text, at different
settings, probably by whoever uploaded it. Regenerate every candidate yourself, using the exact
audition script in §4 and the exact settings in §3:

```bash
# per candidate
curl -sS -X POST "https://api.elevenlabs.io/v1/text-to-speech/$CANDIDATE_ID" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d @audition-request.json --output "content/voice/audition/$CANDIDATE_NAME.mp3"
```

where `audition-request.json` carries the §4 text, the §3 `voice_settings`, and
`"model_id": "<<FILL: model_id from GET /v1/models on your account — pick the highest-quality
non-realtime English model available to your plan; latency is irrelevant to us, we render offline>>"`.

**Step 4 — score. Phone speaker, low volume, one pass each.**

Not headphones. Not twice. The real listening environment is a phone at arm's length in a noisy
room, and a voice that only works on studio monitors does not work. Every candidate must pass all
five gates in §4.2. **If you have to replay a figure to be certain what the number was, that is a
FAIL** — regardless of how good the voice sounds.

**Step 5 — first candidate to pass all five wins.** No aggregate scoring, no "best of a bad
field." If none passes, drop to Profile B and repeat Steps 2–4. If B also empties, then C.

**Step 6 — tie-break, if two pass in the same batch:** play both verdict lines back to back. The
one whose `[PAUSE]` before the verdict word you are more willing to sit through is the cast. That
silence recurs in every episode for the life of the channel; preference for it is the correct
tiebreaker.

**Step 7 — record.** Keep the winning and rejected audition MP3s under `content/voice/audition/`
and write a short casting log next to them: date, candidates heard, which gate each rejection
failed. This costs ten minutes and makes the decision auditable in eighteen months when someone
asks why. It is the same discipline as `evidence.json`, applied to a taste decision.

**Step 8 — hand off.** `config/channel.yaml` is `strategy-lead`'s file (see its header).
`voice-director` supplies the resolved ID and the log; `strategy-lead` writes the line:

```yaml
voice:
  provider: "elevenlabs"
  voice_id: "<<FILL: voice_id from your ElevenLabs library — the Step 5 winner. Copy it verbatim
             from the API response; do not retype it and do not reconstruct it from memory>>"
  settings: { stability: 0.42, similarity_boost: 0.85, style: 0.15 }
```

---

## 3. The settings

These are the values already in `config/channel.yaml`. Here is what each one is actually
protecting against, because a setting nobody can defend is a setting somebody will change.

### `stability: 0.42`

Just below the midpoint. Deliberately asymmetric, and the asymmetry is the point.

- **Protects against (high side):** the flatline. Push stability up and a 40-second read becomes
  metronomic — identical contour on every sentence. That is the exact texture viewers have learned
  to identify as mass-produced, and on this channel it is not merely ugly, it is
  *on-theme with the accusation we are structurally defending against*.
- **Protects against (low side):** prosody roulette. Drop stability and the model starts making
  interpretive choices — inventing emphasis, moving stress. When the word it decides to emphasise
  is a figure, the read is wrong in the one dimension this channel cannot be wrong in. Low
  stability also drifts episode-to-episode, which is a branding failure in slow motion.
- **Why 0.42 specifically:** it is the point where micro-variation survives *inside* a sentence
  while character holds *across* sentences. Practically: enough life that the excavation does not
  drone, enough control that "Verdict: still cheap" lands flat instead of being decorated.

### `similarity_boost: 0.85`

High, on purpose, and the highest of the three.

- **Protects against:** cross-episode drift. We are casting for several hundred episodes. The
  charter's requirement is that a viewer *recognises the channel with their eyes shut* — that
  requires the timbre at episode 200 to be indistinguishable from episode 2. High similarity binds
  output tightly to the reference timbre and is the main lever that buys that.
- **Why not 1.0:** at the ceiling, adherence to the reference starts reproducing the reference's
  *artefacts* as well as its identity — room tone, breath character, sibilance. Those then recur in
  every episode forever, and they are exactly the things you cannot fix in the mix without
  changing the voice. 0.85 is maximum consistency stopping short of inheriting the flaws.

### `style: 0.15`

Low, but deliberately not zero.

- **Protects against:** the voice performing the attitude. The bible's central claim is that the
  numbers are already shocking and the delivery must be calm or the shock is wasted. Style
  exaggeration is the parameter that makes the voice editorialise — and editorialising is not only
  off-brand, it is adjacent to a compliance boundary (`docs/05-compliance.md` Rule 6: mechanical
  causes only, no editorial drift). **The writing carries the attitude. The voice carries the
  figure.**
- **Why not 0.0:** a true zero flattens the falling sentence-end that §1.1 identifies as the most
  diagnostic trait in the brief. 0.15 preserves terminal shape without adding interpretation.
- **Interaction worth knowing:** style trades against stability — raising style makes the read less
  predictable. The two values were chosen together and must be changed together or not at all.
  Moving one is not a small edit.

### Any other knob

Whatever additional parameters your API version exposes: **verify what each one actually does and
what its current default is before leaving it alone.** "Left at default because I checked and
neutral is correct here" is a decision. "Left at default because I didn't look" is the thing this
section exists to prevent. Do not add new keys to `config/channel.yaml` without `strategy-lead`;
the three above are the contract.

### The rule

> **Never ship library defaults.** — `.claude/agents/voice-director.md`

Two reasons, and the second is the one people miss. First, defaults produce the flat AI read that
makes viewers bounce (`docs/04-stack.md`, failure modes). Second, **the defaults are what every
other channel on this provider is also shipping.** Shipping defaults is shipping the
category-average voice on a channel whose whole thesis is that it is not category-average.

And the corollary: **the settings live in config, not in your head, and they do not move
per-episode.** If a line does not land, rewrite the line or re-place the `[PAUSE]`. Do not touch
the sliders. Per-episode tuning is how a channel voice quietly becomes a channel of voices.

Loudness is not a voice setting. `loudness_lufs: -14` / `true_peak_db: -1` are handled at the mix
by `post-supervisor`. Never solve a quiet read by re-generating hotter.

---

## 4. The audition script

### 4.1 The fixture

> **AUDITION FIXTURE — NOT AN EPISODE.** Every figure below is arbitrary, invented for the purpose
> of stressing a text-to-speech read, and refers to no real product, listing, retailer, or series.
> It is deliberately object-less — "the shelf," never a named thing — so it can never be mistaken
> for a claim. It is **85 words**, below the 95-word floor in `config/channel.yaml`, so it cannot
> pass as a shippable script even by accident. It is never rendered and never published.

**[ARTIFACT]**
In twenty sixteen, the shelf price was two forty-nine. [PAUSE]

**[GAP]**
Today, the same shelf: six ninety-five. [PAUSE]

**[EXCAVATION]**
The listing is archived, timestamped, and dull. [EMPHASIS] One input moved.
Everything else drifted inside three percent. That input rose one hundred and seventy-six percent
across eighteen months, and the shelf followed within two quarters. The specialist version still
lists at one thousand four hundred and ninety-five dollars. Nothing here is a mystery.
It's arithmetic nobody had to show you.

**[VERDICT]**
Verdict: [PAUSE] ripoff.

**[HANDOFF]**
What's the number on your shelf?

*Why these lines:* the shape is `_selftest`'s, so it exercises the real beat structure. The
content is chosen to break things — a year as the opening word, a compressed currency figure, a
three-figure percentage, two `[PAUSE]` placements (mid-flow and pre-verdict), a four-figure full
read, a terminal-cluster gauntlet ("months," "percent," "quarters," "arithmetic"), and a verdict
word that dies on a fricative.

### 4.2 The five gates — and what a FAIL sounds like

**GATE 1 — The year: "twenty sixteen"**
This is the first sound of every episode we will ever publish.
- **FAIL:** "two thousand and sixteen." Bureaucratic, four syllables too long, wrong register.
- **FAIL:** run together as one word, no internal beat, stress collapsed onto "sixteen."
- **HARD FAIL:** rising inflection. The channel's first spoken word becomes a question.

**GATE 2 — The currency figure: "two forty-nine" / "six ninety-five"**
- **FAIL:** expanded to "two hundred and forty-nine." That means the model is re-interpreting our
  text, which means it will do so unpredictably across episodes.
- **FAIL:** split by an internal comma-pause — "two … forty-nine" — which sounds like two numbers.
- **FAIL:** delivered at prose speed. Figures take 15–20% longer than surrounding words or they do
  not register. A useful sync check: the `<PriceOdometer>` runs 800 ms (`odometer_ms`), and the
  roll should complete *inside* the spoken figure. If the odometer lands while the voice is still
  on the first syllable, the read is too slow; if the voice finishes first, too fast.
- **FAIL:** pitch rises on the second half — "six ninety-FIVE?" That is the ad-read lilt.

**GATE 3 — The percentage: "one hundred and seventy-six percent"**
- **FAIL:** "percent" swallowed to "purcen." The terminal /t/ is the most-lost consonant in this
  channel's whole vocabulary, and it disappears first on a phone speaker.
- **FAIL:** inconsistent construction — "one hundred and seventy-six" here, "a hundred
  seventy-six" three lines later. Either is acceptable; varying between them inside one episode is
  not.
- **HARD FAIL:** the voice gets excited. Widening, rising, louder on the big number. If the
  delivery sells the figure, the figure was not shocking on its own, and the bible's entire
  premise collapses. A number above +100% is the one place restraint is doing the most work.

**GATE 4 — The `[PAUSE]`**
- **HARD FAIL:** the model speaks the word "pause." Rare, catastrophic, and it happens. Listen
  for it explicitly.
- **FAIL:** no pause at all. The charter names this as the most common failure: *not a bad voice —
  a voice that never stops.* Silence after a number is what makes the number register.
- **FAIL:** under ~350 ms. That reads as a breath, not a beat. A full beat after a figure is
  roughly 600–900 ms.
- **FAIL:** filled with an audible inhale or a synthesised breath artefact. The beat must be empty.
- **FAIL:** landing mid-clause — a sign the marker was absorbed as text rather than honoured.

**GATE 5 — The verdict word: "ripoff"**
This is the frame where the stamp slams in. The word and the stamp share a frame (bible §3), so
if the word is mush the stamp has nothing to land on.
- **HARD FAIL:** triumphant. Louder, rising, satisfied. *Flat is more damning than emphatic, every
  time* — charter. A verdict that sounds pleased with itself turns a source into a rant channel.
- **FAIL:** a smile in the voice.
- **FAIL:** the pre-verdict silence collapses and "Verdict: ripoff" becomes one phrase. The colon
  has to be audible as a gap.
- **FAIL:** stress on "off." It is a trochee — RIP-off.
- **FAIL:** fry or trail-off on the final consonant, so the word ends in a rasp instead of a stop.

**Bonus check — the four-figure full read: "one thousand four hundred and ninety-five dollars"**
- **FAIL:** compressed to "fourteen ninety-five" (violates §5).
- **FAIL:** read as digits.
- **FAIL:** one undifferentiated run with no internal grouping.

### 4.3 The listening protocol

Phone speaker. Arm's length. Low volume. One pass. No transcript in front of you.

Then answer two questions: *what were the two prices*, and *what was the verdict*. If you cannot
answer both from a single pass, the candidate fails, and the failure is not fixable with settings.

---

## 5. Pronunciation policy — LOCKED CHANNEL-WIDE

The charter says: *"159" read as "one fifty-nine" vs "one hundred fifty-nine" — pick one and stay
consistent channel-wide.* Picked.

### 5.1 The mechanical rule (this one is load-bearing)

> **The VO script contains no numerals. Ever.**
>
> Figures are spelled out in words in `script.md`, exactly as they are to be spoken. Numerals live
> in `scene_plan.json` (the on-screen layer) and `evidence.json` (the source of truth).

`_selftest/script.md` already works this way — "nine hundred and ninety-nine dollars," not "$999"
— and that convention is now policy, not habit.

The reason is not style. Automatic numeral expansion is the provider's behaviour, not ours: it
varies by model version, it can change under us without notice, and it is the single most likely
mechanism by which this channel says a number that does not match the number on screen. On a
channel whose entire brand is that the figures are checkable, a silent upstream change to how
"$1,299" is voiced is an unacceptable dependency. Spelling the figure removes it. It also means
the script reviewer reads exactly what the audience will hear, which is how a wrong read gets
caught at `script-editor` rather than at QC.

### 5.2 The style rule (what words to spell)

**Compressed retail read below $1,000. Full read at $1,000 and above.**

| Written figure | Spoken (locked) |
|---|---|
| $0.89 | "eighty-nine cents" |
| $9.99 | "nine ninety-nine" |
| $49 | "forty-nine dollars" |
| $159 | "one fifty-nine" |
| $159.99 | "one fifty-nine ninety-nine" |
| $1,299 | "one thousand two hundred and ninety-nine dollars" |
| 218% | "two hundred and eighteen percent" |
| 3% | "three percent" |
| 2016 | "twenty sixteen" |
| 1.8× | "one point eight times" |

**Why compressed below $1,000.** It is how a price is said out loud by a person holding the
receipt, and that is the exact posture of this channel — someone who handles receipts, not someone
reading a spreadsheet. It is also short: the ARTIFACT beat is three seconds (bible §3), and "one
hundred and fifty-nine dollars and ninety-nine cents" spends eleven syllables where "one
fifty-nine ninety-nine" spends six. The saved second goes into the `[PAUSE]`, which is worth more.

**Why the full read at $1,000 and above.** Because that is exactly where the compressed form
becomes ambiguous: "twelve ninety-nine" is both $12.99 and $1,299. This channel cannot ship a
figure that a viewer could reasonably hear wrong. Four-figure prices are rare, and they are the
ones that most deserve the extra beat anyway.

**Why the ambiguity is otherwise survivable.** Every spoken price appears simultaneously on
screen with a citation chip (bible §5) and again in the burned captions
(`burn_captions: true`). The voice is never the only carrier of a figure. That is a
format-specific property, and it is the reason a compressed read is safe here and would not be on
an audio-only product.

**Percentages are never compressed.** No cashier idiom exists for them, and the percentage is
usually the payload of the excavation. Always "percent," never "per cent." Deltas above +100% —
the alarm-colour figures — get the full read *and* the figure slow-down from §4.2 Gate 2.

**Years are always "twenty sixteen," never "two thousand sixteen."** The first spoken word of
every episode is a year (bible §3), so this rule fires more often than any other in the table.

**The unit is spoken on the first figure of an episode and may be dropped after**, once "dollars"
is established. "In twenty sixteen, this cost one fifty-nine dollars. Today the same tier is two
forty-nine." Dropping it on the *first* figure is the failure; repeating it every time is merely
clumsy.

**The deliberate exception.** The long form is available as a device — "one hundred and fifty-nine
dollars" said in full is audibly slower and reads as *this number is absurd*, without any
adjective, which is precisely the bible's rule that the number does the work. It requires no new
markup and no new agent contract: `script-editor` simply spells it long in `script.md`, and per
§5.1 the voice reads what is written. Use it at most once per episode, on the figure the episode
is about. Twice in one script and it stops being a device.

---

## 6. Lock-in

**Once `voice.voice_id` is written to `config/channel.yaml`, it does not change.** Not for a
better voice, not for a new model, not because episode 40 would sound slightly nicer.

### Why

Recognition compounds, and it is the only asset in this studio that a competitor cannot copy by
reading the repo. The charter's standard is that *a viewer should recognise the channel with their
eyes shut.* That recognition is built one episode at a time and it is the reason a returning
viewer stops scrolling before they have consciously identified what they are watching.

The arithmetic of a swap is brutally asymmetric:

- The **gain** from a better voice is small and one-time. It applies only to episodes not yet made.
- The **loss** from a swap is proportional to the size of the back catalogue and is permanent for
  it. A swap does not upgrade the existing forty episodes. It splits the channel into two channels
  sharing a logo, and resets the recognition clock to zero while keeping every cost already paid.

Past roughly episode ten there is no quality upgrade large enough to clear that bar. Assume there
never will be, and cast accordingly — which is why §2.4 spends effort auditioning properly *now*,
when changing your mind is still free.

### What may change without a recast

| Free to change | Locked |
|---|---|
| Script writing, `[PAUSE]` and `[EMPHASIS]` placement | `voice_id` |
| Mix, loudness, encode | `stability` / `similarity_boost` / `style` |
| Pronunciation of a specific product name | The §5 pronunciation policy |

If a read is not landing, the answer is nearly always in the left column.

### The durability caveat — worth a founder decision

A **stock library voice can be withdrawn, revised, or re-licensed by the provider.** A voice you
own — your own recording, or a clone you created and control — cannot. Given that this document
commits the channel to one voice for several hundred episodes, the provider's right to change that
voice is the largest single risk to the lock-in, and it is not a risk `voice-director` can retire
alone: owning a voice requires a recording and a consenting speaker.

**Recommendation:** cast per §2.4 now so production is unblocked, and treat "own the voice"
as a live decision to revisit before roughly episode 30 — early enough that a migration is still
cheap, late enough to know the format is working. If the owned voice is created, it must be cast
against this same brief and gates, not adopted because it is convenient.

### The Piper fallback is also a cast decision

`voice-director` falls back to Piper TTS with no `ELEVENLABS_API_KEY` (charter;
`docs/04-stack.md`). Left unmanaged, that fallback silently changes the channel's voice mid-
catalogue — the exact harm this section exists to prevent.

So: **cast the fallback too.** Pick the installed Piper voice closest to the cast profile, log it
alongside the ElevenLabs decision, and record it here:

```
Piper fallback voice: <<FILL: voice name from the Piper voices actually installed under
vendor/openmontage — list them after `make setup`; do not assume a name, read the directory>>
```

And the directorial call on when it may be used: **the Piper fallback is for preview renders and
pipeline continuity, not for published episodes.** If the key lapses mid-catalogue, delay the
episode. Cadence is one per day with a hard cap of two precisely because throughput is not the
goal (`docs/05-compliance.md` Rule 3) — a skipped day costs nothing that matters; a published
episode in a different voice costs recognition that took months to build. Note every fallback use
in the episode log so the drop is traceable rather than mysterious.

### If the voice is lost anyway

Account loss, voice withdrawal, provider shutdown. Then:

1. Treat it as an **incident, not an upgrade.** Recast against this document, unchanged.
2. Log the change and its date in the repo, with the audition record.
3. Do **not** log it in `content/CORRECTIONS.md` — that file is reserved for factual errors, and
   diluting it with production notes weakens the one signal that says our numbers are trustworthy.

---

## Open placeholders in this document

| Placeholder | Where | How to resolve |
|---|---|---|
| `voice_id` | §2.4 Step 8 | Run §2.4 Steps 1–7 against the founder's ElevenLabs account |
| `model_id` | §2.4 Step 3 | `GET /v1/models` on the same account; pick the highest-quality non-realtime English model on the plan |
| Piper fallback voice | §6 | List the Piper voices installed under `vendor/openmontage` after `make setup` |

None of these can be filled from inside this repo, and none of them may be guessed.
