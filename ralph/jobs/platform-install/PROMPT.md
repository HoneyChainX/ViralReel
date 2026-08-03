# Ralph job: platform-install
> Install and verify every enabled module in config/platform.yaml for this host's profile.

You are one iteration of a bounded loop. You have no memory of previous iterations except
what is written in the files below. Work in the repo root.

## Mission
Bring the studio platform to a state where `bash scripts/studio/doctor.sh` exits 0 for the
active profile in `config/platform.yaml`: every enabled module cloned/installed at its pinned
ref, every headless driver smoke-tested, every cost control verified.

## Protocol — every iteration, in order
1. Read `config/platform.yaml`, then run `bash scripts/studio/doctor.sh` to see live state.
2. Open `fix_plan.md` (appended below). Pick exactly **ONE** unchecked item — the topmost
   unless your AGENT.md notes say otherwise. Do not start a second item.
3. Do the item. Prefer the module's own installer; never fork or patch a vendor repo —
   pin refs and configure from outside, the way `scripts/setup.sh` treats OpenMontage.
4. Verify honestly: re-run the doctor check for that module. A red check stays unchecked.
5. Record: tick the item in `fix_plan.md` (add any newly discovered work as new items),
   update `AGENT.md` with anything you learned that a future iteration needs.
6. Commit everything with message `ralph(platform-install): <what you did>`.
7. If **every** item is checked AND the doctor exits 0, write a short completion summary to
   `ralph/jobs/platform-install/DONE` and stop.

## Hard rules
- NEVER edit `scripts/gate.py`, `tests/`, or `docs/05-compliance.md`. The runner reverts and
  kills the loop if you do.
- Search the repo for prior art before building anything — never assume something is missing.
  (Duplicate implementations are the classic ralph failure.)
- No placeholder or stub implementations. Honest partial progress recorded in fix_plan.md
  beats a fake complete.
- NEVER set a paid provider key or enable a `cost: paid` module. The platform default is
  $0 marginal cost; paid connectors are founder decisions, not loop decisions.
- GPU modules on a CPU-only host: install to the point the doctor can verify code + config,
  mark the module `status: needs-gpu` in your notes, and move on. Absence of a GPU is a
  host property, not a backlog item you can fix.
- If an upstream repo is gone or renamed, record it in `fix_plan.md` and AGENT.md with the
  evidence, disable the module in the manifest with a dated comment, and continue.
