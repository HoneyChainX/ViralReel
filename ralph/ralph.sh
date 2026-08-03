#!/usr/bin/env bash
# Ralph loop runner — runs a stateless `claude -p` against a persistent job
# prompt until the job's completion promise is on disk or the iteration budget
# is spent. The technique (after Geoffrey Huntley's "Ralph Wiggum" loop): the
# agent is a stateless function; all memory lives in files the loop re-feeds it.
#
#   ralph/jobs/<job>/PROMPT.md    the standing instruction — re-read every turn
#   ralph/jobs/<job>/AGENT.md     operating notes the agent maintains for itself
#   ralph/jobs/<job>/fix_plan.md  the backlog — ONE item is worked per iteration
#   ralph/jobs/<job>/DONE         sentinel — the agent creates it, the loop stops
#   ralph/logs/<job>/iter-N.log   full transcript of every iteration
#
# Usage:
#   bash ralph/ralph.sh <job> [--max N] [--sleep SECONDS] [--dry-run]
#
# Guardrails (all deliberate):
#   * bounded — default 8 iterations, hard flag to raise, never unbounded
#   * one backlog item per iteration — the prompt enforces it, small diffs
#   * every iteration must leave the tree committed — a crash loses nothing
#   * the compliance gate is out of scope — no ralph job may edit scripts/gate.py,
#     tests/, or docs/05-compliance.md (checked after every iteration)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

JOB="${1:-}"; shift || true
MAX_ITER=8
SLEEP_BETWEEN=5
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --max)   MAX_ITER="$2"; shift 2 ;;
    --sleep) SLEEP_BETWEEN="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) echo "unknown flag: $1"; exit 1 ;;
  esac
done

JOB_DIR="ralph/jobs/$JOB"
LOG_DIR="ralph/logs/$JOB"

if [ -z "$JOB" ] || [ ! -f "$JOB_DIR/PROMPT.md" ]; then
  echo "usage: bash ralph/ralph.sh <job> [--max N] [--sleep S] [--dry-run]"
  echo ""
  echo "available jobs:"
  for d in ralph/jobs/*/; do
    [ -f "$d/PROMPT.md" ] && printf '  %-20s %s\n' "$(basename "$d")" \
      "$(head -n 2 "$d/PROMPT.md" | tail -n 1 | sed 's/^> *//')"
  done
  exit 1
fi

command -v claude >/dev/null 2>&1 || {
  echo "ERROR: the 'claude' CLI is not on PATH. Ralph drives Claude Code headlessly."
  exit 1
}

mkdir -p "$LOG_DIR"
rm -f "$JOB_DIR/DONE"   # a stale sentinel must never end a fresh run on turn 0

# The gate is load-bearing and no autonomous loop may touch it.
PROTECTED='scripts/gate.py tests/ docs/05-compliance.md'
protected_sha() { git rev-parse "HEAD:scripts/gate.py" 2>/dev/null || true; }

say() { printf '\n\033[1m[ralph:%s] %s\033[0m\n' "$JOB" "$1"; }

say "job dir  : $JOB_DIR"
say "budget   : $MAX_ITER iterations, ${SLEEP_BETWEEN}s between"
[ "$DRY_RUN" = 1 ] && { say "dry run — printing composed prompt and exiting"; cat "$JOB_DIR/PROMPT.md"; exit 0; }

GATE_BEFORE="$(protected_sha)"

for i in $(seq 1 "$MAX_ITER"); do
  say "iteration $i/$MAX_ITER"
  ITER_LOG="$LOG_DIR/iter-$i.log"

  # The whole job state is re-fed each turn: standing prompt + the agent's own
  # notes + the live backlog. The model is stateless; the files are the memory.
  {
    cat "$JOB_DIR/PROMPT.md"
    echo ""
    if [ -f "$JOB_DIR/AGENT.md" ]; then
      echo "--- YOUR OPERATING NOTES (AGENT.md — update them as you learn) ---"
      cat "$JOB_DIR/AGENT.md"
      echo ""
    fi
    if [ -f "$JOB_DIR/fix_plan.md" ]; then
      echo "--- CURRENT BACKLOG (fix_plan.md — work exactly ONE unchecked item) ---"
      cat "$JOB_DIR/fix_plan.md"
    fi
  } | claude -p --permission-mode acceptEdits 2>&1 | tee "$ITER_LOG" || {
    say "claude exited non-zero on iteration $i — see $ITER_LOG; continuing"
  }

  # Guardrail: the gate and its tests must be byte-identical after every turn.
  if [ "$(protected_sha)" != "$GATE_BEFORE" ] || ! git diff --quiet -- $PROTECTED 2>/dev/null; then
    say "PROTECTED PATH MODIFIED ($PROTECTED) — reverting and stopping the loop"
    git checkout -- $PROTECTED 2>/dev/null || true
    exit 2
  fi

  # Guardrail: no uncommitted wreckage between iterations. Ralph jobs must
  # commit their own work; if one didn't, park it on a WIP commit so the next
  # iteration starts from a clean, recoverable tree.
  if ! git diff --quiet || ! git diff --cached --quiet; then
    git add -A && git commit -m "ralph($JOB): WIP iteration $i (auto-parked by runner)" >/dev/null
    say "uncommitted changes parked as WIP commit"
  fi

  if [ -f "$JOB_DIR/DONE" ]; then
    say "DONE sentinel found after iteration $i — job complete"
    say "completion note:"; sed 's/^/    /' "$JOB_DIR/DONE"
    exit 0
  fi

  [ "$i" -lt "$MAX_ITER" ] && sleep "$SLEEP_BETWEEN"
done

say "iteration budget spent without DONE — read $LOG_DIR and $JOB_DIR/fix_plan.md, then re-run"
exit 3
