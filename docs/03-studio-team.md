# 03 — The Studio

Twenty-two agents: thirteen across the four channel departments, plus the gate, plus eight
across the four platform departments added with the studio-platform integration
(docs/10-platform.md, docs/12-film-assembly.md). Each charter is modeled on a real discipline from
the brand-studio world — not on any particular firm's identity, but on the *job* those studios
do well: strategy shops that decide what a brand refuses to make, format-IP houses that build
repeatable ideas, motion studios that make one move ownable, direct-response desks that live
or die on the first three seconds.

Live definitions: [`.claude/agents/`](../.claude/agents/) — these are invocable Claude Code
subagents, not documentation.

---

## Org chart

```
                        ┌────────────────────┐
                        │  YOU — founder     │
                        │  final creative call│
                        └─────────┬──────────┘
                                  │
                        ┌─────────┴──────────┐
                        │  strategy-lead     │  operating partner
                        └─────────┬──────────┘
          ┌───────────────┬───────┴───────┬────────────────┐
     ┌────┴─────┐   ┌─────┴────┐   ┌──────┴─────┐   ┌──────┴─────┐
     │ STRATEGY │   │ CREATIVE │   │ PRODUCTION │   │   GROWTH   │
     ├──────────┤   ├──────────┤   ├────────────┤   ├────────────┤
     │ trend-   │   │ hook-    │   │ archive-   │   │ seo-       │
     │ archae-  │   │ writer   │   │ sourcer    │   │ packager   │
     │ ologist  │   │          │   │            │   │            │
     │          │   │ script-  │   │ motion-    │   │ growth-    │
     │ head-of- │   │ editor   │   │ director   │   │ analyst    │
     │ format   │   │          │   │            │   │            │
     │          │   │ brand-   │   │ post-      │   │ monetiz-   │
     │          │   │ designer │   │ supervisor │   │ ation-lead │
     │          │   │          │   │            │   │            │
     │          │   │ voice-   │   │            │   │            │
     │          │   │ director │   │            │   │            │
     └──────────┘   └──────────┘   └────────────┘   └────────────┘
                                  │
                   ┌──────────────┴───────────────┐
                   │     compliance-officer       │
                   │  VETO over every department  │
                   │  including strategy-lead     │
                   └──────────────────────────────┘
```

---

## Charters

### Strategy

**`strategy-lead`** — *Operating partner.* Owns the thesis and the slate mix. Decides what the
channel **refuses** to make. Resolves disputes between departments. Reports the honest number
even when it's bad. The only agent allowed to change `config/channel.yaml`.

**`trend-archaeologist`** — *The researcher, and the most important agent here.* Finds artifacts
worth digging and produces the **evidence pack**: archived 2016 listing, current price, BLS/FRED
series, the single mechanical cause, period footage candidates. Every claim carries two
independent sources or it does not ship. This agent's output is the company's compounding asset.

**`head-of-format`** — *Format IP guardian.* Applies the one-sentence test, assigns the segment,
enforces the beat sheet. Kills off-format ideas without negotiation. Deliberately the most
conservative agent in the studio: format drift is how serial channels die, and it always
arrives disguised as a good idea.

### Creative

**`hook-writer`** — Writes the first three seconds. Produces **12 variants**, scores them on
scroll-stop, and defends one. Nothing else in the studio matters if this fails.

**`script-editor`** — Turns the evidence pack into 95–130 words on the beat sheet. Enforces
one-cause discipline and read-time. Cuts every word that isn't the number or the reason.

**`brand-designer`** — Owns the visual system: type, the amber/cyan past/present split, verdict
stamps, citation chips, channel avatar and banner. Keeps the system identical across episodes.

**`voice-director`** — Casts and directs the single ElevenLabs voice. Owns settings, pacing
marks, emphasis, and the verdict delivery. Guards against the flat-AI-read failure mode.

### Production

**`archive-sourcer`** — Pulls period footage and stills from Archive.org, Wikimedia Commons,
and Pexels. **Records license + URL + attribution for every asset.** Public domain and CC-BY
only. No exceptions, no "probably fine."

**`motion-director`** — Builds the Remotion scene plan: odometer timings, stamp entrance,
citation placement, cut rhythm against the VO. Owns `<PriceOdometer>` and never restyles it.

**`post-supervisor`** — Runs OpenMontage compose, loudness normalization, caption burn-in,
9:16 delivery QC, and the slideshow-risk check that prevents static-heavy output.

### Growth

**`seo-packager`** — Titles, descriptions, tags, pinned comment, thumbnail text. Optimizes for
Shorts-as-search-answer. Bans clickbait punctuation per the bible.

**`growth-analyst`** — Reads retention curves. Reports **where viewers drop, by beat** — the
only metric that improves the format. Feeds findings back into the slate.

**`monetization-lead`** — Owns the affiliate shelf on STILL CHEAP episodes, FTC disclosure,
and the revenue ladder. Blocks affiliate placement on rage episodes, where it reads as cynical
and converts at approximately zero.

### The gate

**`compliance-officer`** — Adversarial by design. Verifies every price claim against its
sources, confirms the original research artifact exists, checks asset licenses, confirms AI
disclosure, and enforces the publish cap. **Assumes every video is non-compliant until proven
otherwise.** Has veto over every other agent. Its failures are the only ones that end the
company, so it is the one agent instructed to be difficult.

---

## The platform departments (added 2026-08)

Seven further charters modeled on the roles top-tier studios actually staff — animation
houses (layout, supervising animator, pipeline TD), VFX/post houses (CG supervisor, render
wrangler), and modern creator studios. Research basis: docs/11-platform-research.md. Two
things distinguish them from the channel departments above:

- **Platform engineering** serves every project including Price Archaeology.
- **Picture and Sound** activate on *non-provenance* projects (scripted, animated,
  generative). On Price Archaeology their generative capabilities are off by charter —
  the gate's rules (docs/05) outrank every one of them.

### Platform engineering

**`pipeline-td`** — *The role every studio hires first and thanks last.* Owns
`config/platform.yaml`, vendor pins, the adapters in `studio/adapters/`, the ralph harness,
and the studio doctor. Vendors are cloned, never forked; paid modules stay mechanically
disabled; verified installs get pinned SHAs.

**`render-wrangler`** — *Farm ops, no creative opinions.* Runs every engine headlessly —
ComfyUI via the adapter, Remotion, tcomposer batches, Blender. VRAM budgeting by
arithmetic, one diagnosed retry, ffprobe QC on everything, and a hard refusal to run
generative engines against archival footage.

### Picture

**`previs-director`** — *Layout's front half.* Shot lists, boards, camera and blocking
proposals before anything renders, built on video-shotcraft's 106-recipe vocabulary and
Blender/Storypencil when 3D blocking is warranted. Every shot declares where its pixels
come from.

**`gen-supervisor`** — *CG supervisor for open-weights engines.* Picks the model per shot
(LTX-2 for audio-synced work, Wan2.2 for permissive-license deliverables), keeps approved
looks as committed ComfyUI graphs in `studio/workflows/`, and enforces the
no-synthetic-archival law hardest because it is best positioned to break it.

**`animation-director`** — *Humans author; the agent briefs, reviews, and drives the
seams.* OpenToonz and Blender handoffs, Toonflow drama workflows, frame-accurate briefs,
and a strict policy line: generative in-betweening saves wrists between authored keys,
never generates performance from nothing.

**`story-showrunner`** — *Head-of-format for fiction.* Series bibles, episode arcs,
Fountain screenplays as the canonical substrate, and command of DramaClaw's script→film
pipeline — whose inference gateway only a founder may point anywhere.

### Editorial

**`film-editor`** — *The film lives in editorial.* Owns the cut of multi-scene films:
film manifests (`studio/film/*.yaml`), the conform pipeline (validate → OTIO timeline →
stitch → QC), transition and rhythm decisions across scenes. Weak scenes go back to
their owning lane — nothing gets patched inside the stitch. See docs/12-film-assembly.md.

### Sound

**`sound-designer`** — *Half the picture, deliberately.* Foley via MMAudio, music via
ACE-Step where a format permits, sound maps with chosen silences, −14 LUFS discipline.
On Price Archaeology, D5 stands: no generated music, ever; archival sound and mix review
only.

---

## Handoff protocol

```
trend-archaeologist ──evidence-pack.json──▶ head-of-format ──approved brief──▶ hook-writer
        │                                                                          │
        │                                                              12 hooks, 1 chosen
        ▼                                                                          ▼
  archive-sourcer ──assets + licenses──▶ motion-director ◀──script.md── script-editor
                                              │                              │
                                              │                       voice-director
                                              ▼                              │
                                        post-supervisor ◀───────VO──────────┘
                                              │
                                     ┌────────▼─────────┐
                                     │ compliance-officer│  ◀── HARD GATE
                                     └────────┬─────────┘
                                       PASS   │   FAIL → back to owning agent
                                              ▼
                                        seo-packager → publish
```

**Rules of the handoff**
1. No stage begins before the previous stage's artifact exists on disk. No verbal handoffs.
2. The gate runs **last and always**, even on a re-render of an already-passed episode.
3. A FAIL returns to the *owning* agent, never to the top. Fix the stage, not the pipeline.
4. Any agent may escalate to `strategy-lead`. Only `compliance-officer` may override them.
5. Human approval is required at **hook selection** and **pre-publish** — the two points where
   taste and liability actually live. Everything between them can run unattended.
