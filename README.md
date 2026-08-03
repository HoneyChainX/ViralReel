# ViralReel — Price Archaeology

**An agentic brand studio that runs a YouTube Shorts channel about what things used to cost.**

Marginal cost per video: **$0.00**. Everything below runs on open-source repos, free archives,
and one subscription you already pay for.

---

## The one-paragraph pitch

Two things are true in July 2026. First, the internet is drowning in *2016 nostalgia* — the
"2026 is the new 2016" wave has 37M+ Instagram posts and 1M+ TikTok posts behind it, and the
reason people give for loving it is that 2016 was "the last moment of true mass culture,"
before algorithmic feeds. Second, everyone is quietly furious about what everything costs now.

Nobody has put those two things in the same video. **Price Archaeology** does: we excavate a
single object from 2016, show you the receipt, show you today's receipt, and explain the gap.
The nostalgia is the hook. The price is the payload. The bargain is the payoff.

---

## Why this survives 2026 YouTube

In 2026 YouTube deleted 16 AI-slop channels — 4.7 billion views, 35M subscribers, ~$10M/yr of
revenue — and now evaluates **whole channels** for mass-production under the Inauthentic Content
Policy. Volume is no longer a strategy; it is a liability.

So this studio is built backwards from that. Every video must carry an **original research
artifact** — an archived 2016 price listing, a BLS series, a period photograph — that a
template cannot produce and a chatbot cannot show you. The pipeline **physically cannot publish**
a video whose price claims lack a verifiable source (see `docs/05-compliance.md`). Our defense
against the slop crackdown isn't a promise. It's a gate.

---

## The studio

Twenty-two agents in eight departments, each modeled on a discipline from the studio world —
strategy shops, format-IP houses, motion studios, direct-response copy desks, and (since the
platform integration) the roles animation houses and VFX shops actually staff.

| Dept | Agents |
|---|---|
| **Strategy** | `strategy-lead` · `trend-archaeologist` · `head-of-format` |
| **Creative** | `hook-writer` · `script-editor` · `brand-designer` · `voice-director` |
| **Production** | `archive-sourcer` · `motion-director` · `post-supervisor` |
| **Growth** | `seo-packager` · `growth-analyst` · `monetization-lead` |
| **Platform** | `pipeline-td` · `render-wrangler` |
| **Picture** | `previs-director` · `gen-supervisor` · `animation-director` · `story-showrunner` |
| **Editorial** | `film-editor` — multi-scene assembly: manifests, conform, the cut (docs/12) |
| **Sound** | `sound-designer` |
| **Gate** | `compliance-officer` — can veto any department, including me |

Full charters and reporting lines: [`docs/03-studio-team.md`](docs/03-studio-team.md).
The agents are real, invocable Claude Code subagents in [`.claude/agents/`](.claude/agents/).
Picture and Sound's generative powers are off on this channel by charter — see the platform
doctrine below.

---

## The stack (all free, or already paid for)

| Job | Tool | Cost |
|---|---|---|
| Research + writing + orchestration | Claude Code (this studio) | — |
| Video production pipeline | [OpenMontage](https://github.com/calesthio/OpenMontage) — `hybrid` pipeline | Free / OSS |
| Archival footage & stills | Archive.org, Wikimedia Commons, Pexels | Free |
| Price evidence | Wayback Machine, BLS CPI, FRED | Free |
| Narration | ElevenLabs (**your existing subscription**) | Already paid |
| Composition & render | Remotion + FFmpeg | Free |
| Publish, schedule, SEO, analytics | [youtube-automation-agent](https://github.com/darkzOGx/youtube-automation-agent) | Free / OSS |
| LLM for the automation agent | Gemini free tier | Free |

No Higgsfield credits, no Veo, no Kling, no paid video models. Wiring:
[`docs/04-stack.md`](docs/04-stack.md).

---

## The platform (beyond this channel)

Since 2026-08 the repo also carries a **studio platform** layer
([`docs/10-platform.md`](docs/10-platform.md)): 26 integrated open-source modules in
[`config/platform.yaml`](config/platform.yaml) — ComfyUI, LTX-2, Wan2.2, DramaClaw,
Toonflow, OpenToonz, Blender, video-shotcraft, whisperX, Kokoro, MMAudio, ACE-Step and
more — plus seven platform agents modeled on real studio roles, and bounded
[ralph loops](ralph/README.md) that do the unattended work.

The doctrine (DECISIONS D8): **capability is universal, permission is per-project.** The
generative lane exists for future scripted/animated projects; Price Archaeology's rules
above don't move. Paid modules are mechanically locked off; the compliance gate is fenced
from every loop.

```bash
make platform PROFILE=core        # install a profile's modules
make platform-doctor PROFILE=core # verify — loud on purpose
make ralph JOB=platform-install   # let the loop finish the job
```

---

## Read in this order

1. [`docs/01-strategy.md`](docs/01-strategy.md) — the thesis, the money math, and the risks I'd bet against
2. [`docs/02-channel-bible.md`](docs/02-channel-bible.md) — format spec, four segments, brand voice
3. [`docs/03-studio-team.md`](docs/03-studio-team.md) — the org chart
4. [`docs/04-stack.md`](docs/04-stack.md) — how the repos plug together
5. [`docs/05-compliance.md`](docs/05-compliance.md) — the publish gate
6. [`docs/06-runbook.md`](docs/06-runbook.md) — day 0 → day 90
7. [`docs/07-credentials-handoff.md`](docs/07-credentials-handoff.md) — YouTube OAuth + Gemini keys, as a browser-agent prompt
8. [`content/episodes/`](content/episodes/) — the 10-episode launch slate
9. [`docs/10-platform.md`](docs/10-platform.md) — the studio platform: manifest, adapters, agents, loops
10. [`docs/11-platform-research.md`](docs/11-platform-research.md) — the research behind every platform choice

## Start

```bash
make setup      # clone OpenMontage + youtube-automation-agent, create .env
make doctor     # verify every dependency and key
make test       # gate regression suite — also runs in CI on every push
make episode SLUG=airpods-159        # research → script → gate → render
make publish SLUG=airpods-159        # only runs if the compliance gate passed
```

See [`docs/06-runbook.md`](docs/06-runbook.md) before the first run.
