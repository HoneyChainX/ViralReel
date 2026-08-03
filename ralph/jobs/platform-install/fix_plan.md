# platform-install backlog
One unchecked item per iteration. Add discoveries as new items; never delete history.

- [ ] **BLOCKED — needs a human/founder permission decision, see AGENT.md.** This session's
      Bash permission layer denies `python3`/`bash -c` execution and all network calls
      (`git clone`, `curl`) with no interactive approver present. `doctor.sh`/`install.sh`
      both need both. Confirmed 2026-08-03: `vendor/` doesn't exist, nothing installed.
      Resolve by adding a scoped Bash allowlist (see AGENT.md for the exact commands) to
      `.claude/settings.json`, or running this job with a human present to approve, before
      any install item below can be honestly attempted.
- [ ] Run `bash scripts/studio/install.sh --profile core` and fix whatever breaks first
- [ ] Verify OpenMontage + yt-agent (legacy `make setup` path) still install cleanly alongside the platform tree
- [ ] Install `distribution` profile modules and smoke-test each headless driver
- [ ] Install `genai` profile modules to code+config level (GPU smoke tests only if a GPU exists)
- [ ] Install `animation` profile modules to code+config level
- [ ] Run `bash scripts/studio/doctor.sh` end to end; file one new item per red check above this line
- [ ] Run `make test` — the gate suite must still pass untouched
