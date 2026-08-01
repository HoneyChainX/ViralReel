# 05 — The Publish Gate

> This is the most important document in the repo. Two risks can end this channel: a policy
> strike for mass-produced content, and a wrong number. Everything here exists to make both
> mechanically difficult rather than merely discouraged.

---

## The situation

In 2026 YouTube removed 16 AI-slop channels — **4.7 billion views, 35 million subscribers, and
roughly $10M in annual revenue, gone.** The Inauthentic Content Policy now evaluates
**entire channels**, not individual videos, for mass-produced or templated content. Separately,
since May 2026 YouTube uses internal signals to detect significant photorealistic AI content and
will **apply the disclosure label itself** if a creator fails to.

The practical translation for an automated studio:

- Producing more videos makes you *more* likely to be flagged, not more likely to succeed.
- Templated output is the specific detection signal.
- Undisclosed synthetic realism is a separate, compounding exposure.

A pipeline that maximizes throughput is optimizing directly for deletion. This one maximizes
**defensible originality per video** instead, and caps throughput on purpose.

---

## Rule 1 — the original research artifact

**Every episode must contain at least one piece of evidence that did not exist in retrievable
form before we made it.**

Qualifying artifacts:
- An archived 2016 retail listing pulled from the Wayback Machine, screenshotted and cited
- A price delta computed from a named BLS/FRED series with the series ID on screen
- A period photograph or clip with documented provenance, newly assembled into a comparison
- An original chart built from ≥3 independent price sources

Not qualifying: restating a known fact; a generated illustration; a template with the nouns
swapped; anything a chatbot could produce without a browser.

This single rule is what separates us from the channels that got deleted, and it is also — not
coincidentally — what makes the content genuinely good. The compliance requirement and the
quality requirement point the same direction, which is the only reason a gate this strict is
survivable.

## Rule 2 — two sources per number

Every price claim carries **two independent sources**, recorded in `evidence.json`, at least one
of them primary (an archived listing, a filing, a government series).

One source is a rumor. Two is a fact. Zero is how a provenance brand dies in a single afternoon.

## Rule 3 — the throughput cap

**Maximum 2 published videos per day. Launch cadence 1.**

Enforced in `config/channel.yaml` and checked by the gate against the publish log. This is a
deliberate cap on our own scale. If you ever want to raise it, the correct move is to hire more
research capacity — not to loosen this number.

## Rule 4 — AI disclosure, always on

`ai_disclosure: true` on every upload, unconditionally. We use synthetic narration, so it's
required. We also never use photorealistic synthetic humans, synthetic "archival" footage, or
generated imagery presented as real — the format's entire value is that the footage is real.

Disclosing costs nothing. Being auto-labeled after failing to disclose costs trust.

## Rule 5 — license discipline

Public domain or CC-BY only. Every asset in `licenses.json` with source URL, license, and
attribution string. Attribution renders in the video description. No asset without a recorded
license reaches the render — the gate checks the file, not the intention.

## Rule 6 — the archive layer is never synthesised

Adobe Creative Cloud brings image tooling into reach. Two capabilities would
**falsify evidence** if pointed at the archive layer, and both are banned:

**`image_generative_expand` — banned outright, everywhere.** It is outpainting: it invents
pixels beyond the frame edge. Extending a 2016 storefront photo to fill 9:16 would fabricate
visual evidence on a channel whose entire defence is that its evidence is real. If an archival
frame does not fill vertical, **crop it, letterbox it, or source a different clip** — those are
the only three answers. There is no episode important enough to invent a shopfront for.

**Adobe Stock is never period material.** Stock is modern imagery. Using it for a 2016
comparison shot is the same falsification by an easier route, which is precisely what makes it
dangerous — `archive-sourcer` already bans presenting modern footage as period, and Stock makes
that ban easier to break by accident than any other source. Stock is permitted only for
explicitly-present-day shots, must be recorded in `licenses.json` like any other asset, and is
`stock_enabled: false` by default because licensing consumes credits and breaks the $0 model.

**What Adobe tooling *is* for.** Colour and grain treatment of assets we already legitimately
hold — desaturation, grain, monochromatic tint, temperature — applied to make sourced material
match the bible's look. Treating a real photograph is grading. Extending one is fabrication.
The line is whether a pixel describes something that was actually photographed.

## Rule 7 — no editorial drift

No political-party framing, no partisan blame, no medical or financial advice, no claims about
named living individuals. Mechanical causes only (see bible §7).

---

## The gate

Runs after render, before publish. Every episode, every time — including re-renders of episodes
that already passed, because the thing that changed might be the thing that breaks a rule.

```
$ make gate SLUG=airpods-159
```

| # | Check | Fails if |
|---|---|---|
| C1 | Original research artifact present | `evidence.json.artifact` empty or unverifiable |
| C2 | Two sources per price claim | any claim with < 2 sources, or 0 primary |
| C3 | On-screen citations render | any price frame without a citation chip |
| C4 | Asset licenses recorded | any asset missing license/URL/attribution |
| C5 | AI disclosure set | `ai_disclosure != true` |
| C6 | Publish cap | ≥ 2 already published in the trailing 24h |
| C7 | Template-similarity | script > 70% structurally similar to the last 10 |
| C8 | Editorial bounds | partisan/medical/financial/individual-claim language detected |
| C9 | Delivery QC | not 1080×1920, or duration outside 25–50s |
| C10 | Privacy | upload privacy != `private` — **see the limit below** |

**Any FAIL blocks publish.** Result written to `gate.json`. There is no override flag and no
`--force`. If you need to ship something the gate rejects, fix the episode or change the rule
in this document deliberately — the absence of a bypass is the feature.

### On C10 — what it actually enforces, and what it doesn't

C10 checks *our* `packaging.json`. It does **not** reach into the vendor uploader. That uploader
reads `process.env.DEFAULT_PRIVACY_STATUS || 'private'`
(`vendor/yt-agent/agents/publishing-scheduling-agent.js:130`), so uploads do land private — but
that is the **vendor's hardcoded fallback** doing the work, not this gate.

Stated plainly: if `DEFAULT_PRIVACY_STATUS=public` were set in `vendor/yt-agent/.env`, C10 would
still pass and the upload would go out public. `make doctor` catches that case; the gate does
not. Found by auditing the vendor rather than trusting our own env template, and recorded here
rather than quietly rewritten — a compliance check that overstates its reach is worse than one
that admits its edge.

### On C7 (template similarity)

This is the check that most directly targets the thing YouTube is detecting. It compares the
new script's structure against the last ten. If ten consecutive episodes share a skeleton with
only the nouns swapped, that is the mass-production signal, and we catch it before YouTube does.

The beat sheet is a *rhythm*, not a fill-in-the-blank. Same beats, genuinely different writing —
the way a news segment has a consistent structure but is never the same script twice.

---

## Corrections policy

We will get a number wrong eventually. When we do:

1. Unlist within 1 hour of confirmation.
2. Pinned comment stating the error and the correct figure.
3. Log it in `content/CORRECTIONS.md`, publicly, in the repo.
4. If the error changes the verdict, re-cut and republish — do not quietly edit the description.

A visible corrections log is an *asset* for a provenance brand. It is the single cheapest signal
that the other numbers are trustworthy, and it costs nothing but ego.

---

## What I will not build

For the record, and so the boundary is in the repo rather than in a conversation:

- Sub4Sub, view bots, engagement pods, or any artificial engagement
- Multi-channel networks reposting the same content to dodge the mass-production signal
- Scraped or re-uploaded third-party footage outside its license
- Undisclosed AI, synthetic "archival" evidence, or fabricated citations
- Fake scarcity, fake testimonials, or affiliate placement disguised as editorial

Not on principle alone — these are also precisely the behaviors that got 4.7 billion views
deleted this year. The compliant path and the durable path are the same path here.
