# platform-install backlog
One unchecked item per iteration. Add discoveries as new items; never delete history.

- [x] **BLOCKED — needs a human/founder permission decision, see AGENT.md.** This session's
      Bash permission layer denies `python3`/`bash -c` execution and all network calls
      (`git clone`, `curl`) with no interactive approver present. `doctor.sh`/`install.sh`
      both need both. Confirmed 2026-08-03: `vendor/` doesn't exist, nothing installed.
      Resolve by adding a scoped Bash allowlist (see AGENT.md for the exact commands) to
      `.claude/settings.json`, or running this job with a human present to approve, before
      any install item below can be honestly attempted.
      → **Resolved 2026-08-03:** at the founder's request the job's work moved to the main
      session, which holds interactive exec/network permissions. The unattended-loop
      permission gap itself is still open for future ralph runs — recorded in AGENT.md as a
      standing note; the settings.json allowlist remains a founder decision.
- [x] Run `bash scripts/studio/install.sh --profile core` and fix whatever breaks first
      → done 2026-08-03, exit 0: openmontage (full `make setup`), video-shotcraft,
      screenplain, auto-editor, otio. SHAs pinned in config/platform.yaml via
      `platform.py pin` (added this run).
- [ ] Verify OpenMontage + yt-agent (legacy `make setup` path) still install cleanly alongside the platform tree
      → partially: both installed via the manifest path; still to run: `scripts/setup.sh`
      to apply its OpenMontage budget pin (mode=cap/$0.00, checkpoint auto_noncreative) —
      the manifest install alone does NOT pin the vendor's budget config.
- [ ] Install `distribution` profile modules and smoke-test each headless driver
      → yt-agent installed + pinned; smoke = doctor checks in the running full pass
- [ ] Install `genai` profile modules to code+config level (GPU smoke tests only if a GPU exists)
      → in progress (background run; this host has no GPU — code+config level only)
- [ ] Install `animation` profile modules to code+config level
      → in progress (blender-mcp clone; blender/opentoonz/toonflow are desktop, skipped)
- [ ] Install `voice` + `audio` profile modules
      → in progress: whisperx installed + pinned; kokoro/chatterbox/voxcpm/mmaudio/ace-step pending
- [ ] Run `bash scripts/studio/doctor.sh` end to end; file one new item per red check above this line
- [ ] Pin SHAs for the remaining modules once their installs verify (`platform.py pin --profile all`)
- [ ] Run `make test` — the gate suite must still pass untouched
