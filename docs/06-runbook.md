# 06 — Runbook

Day 0 to day 90. Follow it in order; the sequencing matters more than the speed.

---

## Day 0 — install

```bash
make setup     # clones both vendors, installs deps, templates .env files
```

Then two manual steps, manual on purpose:

1. **ElevenLabs key** → `vendor/openmontage/.env`. Leave every other generator key empty.
   That emptiness is the cost control (`docs/04-stack.md`).
2. **`cd vendor/yt-agent && npm run walkthrough`** — browser OAuth for YouTube, plus a free
   Gemini key. Keep `PRIVACY_STATUS=private`.

```bash
make doctor    # verifies deps, keys, and that no paid key crept in
make gate SLUG=_selftest   # proves the gate runs; C9 fails by design (no render)
```

`_selftest` is a fixture with fictional figures. It exists so you can confirm the gate works
before you trust it with a real episode. Never publish it.

---

## Day 1 — the decisions only you can make

Three things the studio cannot decide for you, and all three are permanent-ish:

**1. Cast the voice.** `@voice-director` shortlists; you pick. This voice is the channel for the
next several hundred episodes — changing it at episode 40 costs more recognition than any
upgrade gains. Record the ID in `config/channel.yaml`.

**2. Approve the visual system.** `@brand-designer` renders the avatar, banner, verdict stamps
and a sample frame. Approve or adjust *now*, while changing it is free.

**3. Confirm the slate.** Read `content/episodes/SLATE.md`. Kill anything you find boring —
your boredom is the most reliable early signal available, and you are the only one who has it.

---

## Day 2–7 — first three episodes

Build `four-k-tv`, `grocery-cart-001`, `fast-food-combo` — a collapse, the series anchor, and
the highest-reach rage episode. That mix establishes all three modes before an audience decides
what the channel is.

```bash
make episode SLUG=four-k-tv
```

Then, in Claude Code:

```
@trend-archaeologist  build the evidence pack for four-k-tv
@head-of-format       approve or kill, assign segment
@hook-writer          12 hooks                      ← YOU CHOOSE
@script-editor        script from the chosen hook
@archive-sourcer      assets + licenses
@motion-director      scene plan
@voice-director       VO
@post-supervisor      render
make gate SLUG=four-k-tv
@seo-packager         title, description, tags
make publish SLUG=four-k-tv                          ← lands PRIVATE
```

**Expect the first gate run to fail.** That is the system working. Route each failure to the
agent named in `gate.json` and re-run. Episode one typically takes 3–4 gate cycles; by episode
ten it is usually one.

**Watch all three before publishing any.** Back to back. You are checking one thing: do they
feel like the same channel, and do they feel like *different videos*? If they feel like a
template with the nouns swapped, that is the mass-production signal — fix it now, at three
episodes, not at thirty.

---

## Week 2–4 — cadence

One per day. **Do not raise this.** More videos increases policy exposure and cannot increase
Shorts ad revenue enough to matter (`docs/01-strategy.md` §3).

Alternate STILL CHEAP and THE DIG strictly. Never two rage episodes back to back.

Weekly: `@growth-analyst` produces a retention report. **Change one thing per week, not five** —
change five and you learn nothing from the result.

**Milestone, day 30:** 30 published, format locked, average view duration above 85%.
If retention is below 70% by episode 15, stop publishing and fix the format. Publishing more of
something that isn't working just teaches the algorithm that the channel isn't worth showing.

---

## Month 2–3 — compounding

- Every episode adds a verified pair to the price database. That database is the actual company
  (`docs/01-strategy.md` §4) — treat `evidence.json` files as the asset, not the videos.
- Start the correction discipline the first time you are wrong. Publicly, in `CORRECTIONS.md`.
- At 10k subs, `@monetization-lead` turns on YouTube Shopping affiliate — **STILL CHEAP only.**
- Begin the first long-form cut. Long-form earns roughly 20× per view; Shorts are the funnel.

**Milestone, day 90:** 1,000 subs, one Short above 100k, and a clear answer to which segment
drove it.

---

## When things go wrong

| Symptom | Read this first |
|---|---|
| Gate keeps failing C2 | The research is thin. That's the gate doing its job — fix the evidence, not the check |
| Gate fails C7 | Scripts have converged to a template. Rewrite; this is the one that gets channels deleted |
| Renders look like slideshows | `@archive-sourcer` needs clips with real motion |
| VO sounds robotic | `@voice-director` is shipping defaults. It should never ship defaults |
| Retention dies in the excavation | Most common failure, and it is a *research* problem — the middle has no surprise |
| A number was wrong | `docs/05-compliance.md` → corrections policy. Within 1 hour |
| Costs appeared | `make doctor`. A paid key got set |

---

## The two rules worth memorizing

**1. Never publish a number you cannot show a source for.** The entire brand is that our figures
are checkable. One fabricated number ends that permanently, and no amount of subsequent accuracy
rebuilds it.

**2. Never raise the cadence to chase growth.** Every channel that got deleted this year was
optimizing throughput. The compounding asset is the verified database, not the upload count.
