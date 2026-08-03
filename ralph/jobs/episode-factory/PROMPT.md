# Ralph job: episode-factory
> Advance the next slate episode through stages 1–8, stopping at every human gate.

You are one iteration of a bounded loop with no memory beyond the files below.

## Mission
Take the next unproduced episode from `content/episodes/SLATE.md` through the pipeline in
`docs/04-stack.md` (§ Making an episode): evidence pack → format check → hooks → script →
assets → scene plan → VO → render. Each stage is owned by a studio agent in `.claude/agents/`
— do the stage the way that agent's charter says, or invoke the agent if subagents are
available in this session.

## Protocol — every iteration
1. Find the current episode + stage: the first slug in SLATE.md whose `content/episodes/<slug>/`
   is missing a stage artifact (stage order and artifact names are in docs/04-stack.md § table).
2. Complete exactly **ONE** stage. The artifact must land on disk in the episode folder —
   no verbal handoffs (docs/03 rule 1).
3. Verify: the artifact validates (evidence against `schemas/evidence.schema.json`, script
   word count 95–130, licenses.json complete, etc. — each agent charter states its own bar).
4. Tick progress in `fix_plan.md`, note lessons in `AGENT.md`, commit as
   `ralph(episode-factory): <slug> stage <n> <name>`.
5. HUMAN GATES — these end the loop, they are not yours:
   - After stage 3 (12 hooks written): write `DONE` saying "hooks ready for founder choice
     on <slug>" and stop. A human picks the hook; the loop restarts after.
   - After stage 8 (render exists): run `make gate SLUG=<slug>`; report the result in `DONE`
     and stop. Publishing is the founder's, always.

## Hard rules
- NEVER edit `scripts/gate.py`, `tests/`, or `docs/05-compliance.md`.
- Search the episode folder before producing a stage — never redo an artifact that exists.
- No placeholder artifacts. A stage without its real content stays uncompleted in fix_plan.md.
- Every price claim needs two independent sources in evidence.json — one primary. If the
  research can't find them, the honest output is a `research-blocked.md` note in the episode
  folder, not a weaker claim.
- Archive assets: public domain / CC-BY only, every asset in licenses.json. No generated
  imagery presented as archival — ever (docs/05 Rule 6).
- ElevenLabs is the only billable call permitted, per docs/DECISIONS.md D7. Piper fallback
  must be recorded loudly in the episode log, never silent.
