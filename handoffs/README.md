# Handoffs — browser jobs for Claude for Chrome

The founder's operating model: **jobs that happen in a browser get written up as a markdown
brief and handed to Claude for Chrome**, which runs in the founder's own logged-in browser.
No credentials change hands, no OAuth clients get created, nothing is automated server-side.

This replaced the yt-agent automated-publishing plan at launch (docs/DECISIONS.md, D1).
Automation returns as phase 2 if manual cadence ever hurts.

| Brief | Job | Cadence |
|---|---|---|
| [`upload-episode.md`](upload-episode.md) | Upload a gated episode via YouTube Studio | Per episode |
| [`collect-analytics.md`](collect-analytics.md) | Transcribe retention data from Studio | Weekly |

## Rules for every handoff

1. **The brief is complete or it doesn't ship.** A browser agent cannot ask the repo questions
   mid-task. Every value it needs is IN the brief — filled from the episode's `packaging.json`
   before handing it over.
2. **The gate came first.** No upload brief is generated for an episode whose `gate.json` is
   not PASS. There is no browser-side override of the gate, by design.
3. **The agent never flips a video public.** It uploads PRIVATE, the founder reviews playback
   and flips it. The human is the last gate (compliance C10, now literal).
4. **Every upload ends with the log.** `python3 scripts/log_publish.py --slug <slug>` — this is
   what keeps the 2/day cap (gate C6) real. An unlogged upload is a compliance hole.
5. Briefs describe **what the agent is looking for, not exact menu labels** — Google renames UI
   elements; intent survives renames.
