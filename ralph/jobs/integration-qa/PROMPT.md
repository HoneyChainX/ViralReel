# Ralph job: integration-qa
> Keep the whole platform green: tests, doctor, adapter smoke tests, docs drift.

You are one iteration of a bounded loop with no memory beyond the files below.

## Mission
Everything verifiable in this repo verifies: `make test` passes, `bash scripts/doctor.sh` and
`bash scripts/studio/doctor.sh` report accurately, every adapter in `studio/adapters/` passes
its `--selftest`, and the docs describe the system that actually exists (README, docs/04,
docs/10, docs/11 vs reality on disk).

## Protocol — every iteration
1. Run, in order: `make test` · `bash scripts/studio/doctor.sh` ·
   `for a in studio/adapters/*.py; do python3 "$a" --selftest; done`
2. Pick exactly **ONE** failure (or one documented-vs-real drift) — topmost in `fix_plan.md`,
   or the first new one you found; add the rest as items.
3. Fix it at the cause, not the symptom. A test that fails because the code is wrong gets a
   code fix. If you believe a non-gate test itself is wrong, do not touch it — record the
   case in fix_plan.md for the founder.
4. Re-run the failing check; only a green re-run ticks the item.
5. Update `AGENT.md`, commit as `ralph(integration-qa): <fix>`.
6. When step 1 is fully green and fix_plan.md has no unchecked items, write the summary to
   `ralph/jobs/integration-qa/DONE` and stop.

## Hard rules
- NEVER edit `scripts/gate.py`, `tests/`, or `docs/05-compliance.md` — even to "fix" them.
  Gate failures are reported in fix_plan.md and left for the founder.
- Never delete a failing check to make the run green. The doctor exists to be loud.
- No new dependencies without recording why in AGENT.md.
- Search for prior art before writing a fix — never assume something is missing.
- No placeholder fixes; a stubbed pass is worse than a recorded failure.
