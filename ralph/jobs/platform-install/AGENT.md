# Operating notes — platform-install
(Maintained by the loop. Newest lessons at the top. Keep it under ~60 lines; prune stale notes.)

- **2026-08-03 (main session): installs run fine with interactive permissions.** Core +
  distribution profiles verified (exit 0) and SHA-pinned via the new `platform.py pin`
  command. The iteration-1 permission findings below remain TRUE for unattended
  `claude -p --permission-mode acceptEdits` runs — until a founder adds a scoped Bash
  allowlist to `.claude/settings.json`, this job only works driven from a session with
  exec/network permissions. Torch-based pip installs (whisperx, comfyui) are the disk/time
  hogs: ~5-8 GB each with nvidia wheels; check `df` before genai installs on small hosts.
- Legacy-path gap found: the manifest's openmontage install_cmd does NOT apply
  scripts/setup.sh's budget pin (mode=cap/$0.00). Run scripts/setup.sh after manifest
  installs, or the vendor ships budget.mode=warn — a real cost-control hole.

- **Iteration 1 (2026-08-03): environment blocker, not a code bug.** This session's Bash
  permission layer denies two things outright, with no interactive human available to
  approve them mid-run: (1) any interpreter execution — `python3 <script>`, `python3 -c`,
  `bash -c` all return "This command requires approval" and fail; (2) any network call —
  `git clone`, `git fetch` of a remote, `curl` all fail the same way. Plain read-only /
  local commands work fine: `ls`, `cat`, `echo`, `mkdir`, `git status`, `git log`, `git
  diff`. Confirmed by direct probing this iteration, not assumed.
  - Consequence: `scripts/studio/doctor.sh` and `install.sh` cannot run — both shell out to
    `python3 scripts/studio/platform.py`, which itself does `git clone`. Neither the doctor
    nor the installer executed even once.
  - Confirmed via `find`/`ls` (not the doctor) that `vendor/` does not exist at all yet —
    zero modules installed, consistent with iter-1.log being empty.
  - Root cause traced one level up: `ralph/ralph.sh` invokes each iteration as
    `claude -p --permission-mode acceptEdits`. `acceptEdits` auto-accepts Write/Edit tool
    calls but does **not** allowlist Bash execution of interpreters or network egress — so
    a real unattended `ralph.sh` run of this job would hit the identical wall on iteration 1,
    every time, with nothing to show for it.
  - Fix needs a founder/user decision, not a loop decision: either (a) add a scoped
    `.claude/settings.json` Bash allowlist for the exact commands this job needs
    (`python3 scripts/studio/platform.py *`, `git clone` of the specific pinned repo URLs
    in config/platform.yaml, pip/venv installs under `vendor/*`), or (b) run this job with a
    human present to approve commands live, or (c) a broader permission mode for this job
    specifically. Granting broad Bash/network permission is exactly the kind of
    security-relevant, hard-to-reverse-ish call this loop should not make for itself —
    flagged to the user instead of self-granted.
  - Until that's resolved, no fix_plan.md item can be honestly ticked — do not mark
    "install core" done based on reading the manifest/scripts alone. Re-probe with a plain
    `python3 --version` or `echo` first each iteration; if it's still blocked, don't re-run
    the same denied command more than once (burns iterations for nothing) — just record it
    and stop for a human decision.
