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
- [x] Verify OpenMontage + yt-agent (legacy `make setup` path) still install cleanly alongside the platform tree
      → done: `scripts/setup.sh` ran end-to-end idempotently over the manifest-installed
      tree. Its two distinctive effects verified applied: OpenMontage budget pin
      (mode=cap, total_usd=0.00, checkpoint auto_noncreative — vendor had shipped `warn`)
      and the .env cost-control annotation.
- [x] Install `distribution` profile modules and smoke-test each headless driver
      → yt-agent installed + pinned; doctor checks green. Postiz stays disabled (D1/D2).
- [x] Install `genai` profile modules to code+config level (GPU smoke tests only if a GPU exists)
      → comfyui, ltx-2, wan2-2, dramaclaw, practical-rife cloned + pinned. No GPU on this
      host: comfyui venv + adapter selftest correctly deferred (`needs_gpu` checks; the
      .venv check gained `needs_gpu: true` this run — it demanded a GPU-level artifact on
      a CPU host, a declaration bug, fixed in the manifest not the doctor).
- [x] Install `animation` profile modules to code+config level
      → blender-mcp cloned + pinned; blender/opentoonz/toonflow are desktop (human-installed).
- [x] Install `voice` + `audio` profile modules
      → whisperx, kokoro (pip installs), chatterbox, voxcpm, mmaudio, ace-step (clones):
      all installed + pinned.
- [x] Run `bash scripts/studio/doctor.sh` end to end; file one new item per red check above this line
      → **All green for profile 'all', exit 0** (2026-08-03). One red found and root-caused
      along the way (comfyui .venv declaration, above). Static ffmpeg fetched to
      vendor/ffbin (no system ffmpeg on this host).
- [x] Pin SHAs for the remaining modules once their installs verify (`platform.py pin --profile all`)
      → 18 modules pinned total; `main` remains only on disabled/desktop modules, which is
      the design: `main` visibly means "not verified".
- [x] Run `make test` — the gate suite must still pass untouched
      → 30 tests OK (3 pre-existing environment skips locally; CI runs them in full and is
      green on the branch head).
