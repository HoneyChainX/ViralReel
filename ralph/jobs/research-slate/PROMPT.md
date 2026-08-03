# Ralph job: research-slate
> Keep 5+ gate-ready evidence packs ahead of production at all times.

You are one iteration of a bounded loop with no memory beyond the files below.

## Mission
The studio's compounding asset is researched, sourced, verifiable price pairs
(docs/03: trend-archaeologist charter). Keep `content/episodes/SLATE.md` stocked with at
least 5 episodes whose `evidence.json` already exists, validates against
`schemas/evidence.schema.json`, and would survive the gate's source checks.

## Protocol — every iteration
1. Count slate entries with a valid evidence pack. If ≥ 5, write the count to
   `ralph/jobs/research-slate/DONE` and stop — do not overproduce.
2. Otherwise: EITHER research one new artifact candidate (2016 price + today's price + the
   one mechanical cause, two independent sources per number, one primary — Wayback, BLS,
   FRED) and add it to SLATE.md with its evidence pack; OR complete the evidence pack of an
   existing slate entry that lacks one. One episode per iteration.
3. Run the format test before writing anything: would head-of-format kill it? One object,
   one number, one cause, fits a segment in docs/02-channel-bible.md. If yes, kill it
   yourself and note why in AGENT.md — a dead idea recorded is research too.
4. Validate evidence.json against the schema, commit as
   `ralph(research-slate): <slug> evidence`.

## Hard rules
- NEVER edit `scripts/gate.py`, `tests/`, or `docs/05-compliance.md`.
- A claim with one source does not enter SLATE.md. No exceptions — this file feeds a channel
  whose whole brand is provenance.
- Do not fabricate archived prices. If the Wayback Machine doesn't have it, the idea dies.
- Search SLATE.md and content/episodes/ before adding an idea — never duplicate a slug or
  re-research a shipped artifact.
