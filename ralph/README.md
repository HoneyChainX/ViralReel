# Ralph loops

Bounded autonomous work loops, after Geoffrey Huntley's "Ralph Wiggum" technique: `claude -p`
is treated as a **stateless function**, called repeatedly by a dumb bash loop, with every bit
of memory living in files that get re-fed each turn. The loop is deliberately stupid; the
files are the intelligence.

```
bash ralph/ralph.sh                      # list jobs
bash ralph/ralph.sh platform-install     # run one (default budget: 8 iterations)
bash ralph/ralph.sh episode-factory --max 12
make ralph JOB=integration-qa            # same thing, via make
```

## The jobs

| Job | Standing order | Ends when |
|---|---|---|
| `platform-install` | Install + verify every enabled module in `config/platform.yaml` | studio doctor exits 0 |
| `episode-factory` | Advance the next slate episode through stages 1–8 | a **human gate** (hook choice / publish) — always |
| `integration-qa` | Keep tests, doctors, adapters, and docs green and honest | full green run |
| `research-slate` | Keep ≥5 gate-ready evidence packs ahead of production | stock reached |

## Anatomy of a job

```
ralph/jobs/<job>/
  PROMPT.md     the standing order — re-read from scratch every iteration
  AGENT.md      operating notes the agent writes to its future self
  fix_plan.md   the backlog; exactly ONE unchecked item is worked per iteration
  DONE          sentinel the agent creates to stop the loop (deleted at run start)
ralph/logs/<job>/iter-N.log   full transcript of every iteration
```

## Guardrails, all mechanical

- **Bounded.** Default 8 iterations. There is no unbounded mode.
- **One item per iteration.** Small diffs, every iteration committed; a crash loses nothing —
  the runner parks any uncommitted tree as a WIP commit.
- **The gate is untouchable.** If an iteration modifies `scripts/gate.py`, `tests/`, or
  `docs/05-compliance.md`, the runner reverts the change and kills the loop with exit 2.
- **Human gates end loops.** `episode-factory` cannot pick a hook and cannot publish; it stops
  and says so. Taste and liability stay human (docs/03, handoff rule 5).
- **$0 doctrine holds.** No job may set a paid key or enable a `cost: paid` module. ElevenLabs
  VO (already subscribed) is the single sanctioned exception, per DECISIONS D7.

Exit codes: `0` done · `2` protected path touched · `3` budget spent before DONE.
