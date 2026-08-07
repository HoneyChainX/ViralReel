#!/usr/bin/env bash
# Remove CUDA payload from a venv on a host that has no GPU.
#
#   bash scripts/studio/prune-cuda.sh vendor/whisperx/.venv whisperx
#   bash scripts/studio/prune-cuda.sh --all
#
# The CPU-torch rule (install torch from the CPU index BEFORE anything that
# pulls it) is necessary but not sufficient, and this repo has the receipts:
# whisperx re-resolved to a CUDA torch anyway and carried 4.7 GB of nvidia
# wheels, while argos-translate held 3.4 GB of cuda-toolkit reached through a
# dependency torch never touches. Eight gigabytes on a machine that cannot
# execute a single CUDA kernel.
#
# On a GPU host this script does nothing at all — there the payload is the point.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# venv path : module to import as the proof it still works
ALL_TARGETS=(
  "vendor/whisperx/.venv:whisperx"
  "vendor/argos-translate/.venv:argostranslate"
  "vendor/kokoro/.venv:kokoro"
  "vendor/mediapipe/.venv:mediapipe"
)

say()  { printf '\n\033[1m==> %s\033[0m\n' "$1"; }
ok()   { printf '  \033[32mOK\033[0m    %s\n' "$1"; }
warn() { printf '  \033[33mWARN\033[0m  %s\n' "$1"; }
bad()  { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; }

if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi -L >/dev/null 2>&1; then
  echo "GPU present — leaving CUDA packages alone (they are the fast path here)."
  exit 0
fi

du_mb() { du -sm "$1" 2>/dev/null | cut -f1; }

prune_one() {
  local venv="$1" module="$2"
  local pip="$venv/bin/pip" py="$venv/bin/python"
  [ -x "$pip" ] || { warn "$venv: no venv, skipping"; return 0; }

  local sp before after
  sp="$(ls -d "$venv"/lib/python*/site-packages 2>/dev/null | head -1)"
  [ -n "$sp" ] || { warn "$venv: no site-packages"; return 0; }
  before="$(du_mb "$sp")"

  say "$venv"

  # A CUDA torch build links against the nvidia wheels at import time, so
  # deleting them without replacing torch turns `import torch` into a missing
  # libcublas. Swap the build first, then sweep.
  local tv
  tv="$($pip show torch 2>/dev/null | awk '/^Version:/{print $2}')"
  if [ -n "$tv" ] && [[ "$tv" != *"+cpu" ]]; then
    echo "  torch $tv is not a CPU build — reinstalling from the CPU index"
    # Pin the same version so the dependent package's own constraint still holds.
    if ! $pip install --quiet --force-reinstall \
         "torch==${tv%%+*}" --index-url https://download.pytorch.org/whl/cpu; then
      warn "could not reinstall a CPU torch — leaving this venv untouched"
      return 0
    fi
    ok "torch is now $($pip show torch 2>/dev/null | awk '/^Version:/{print $2}')"
  fi

  local victims
  victims="$($pip list --format=freeze 2>/dev/null \
    | cut -d= -f1 \
    | grep -iE '^(nvidia-|cuda-|triton$|cupti)' || true)"
  if [ -z "$victims" ]; then
    ok "no CUDA packages left"
  else
    echo "  removing: $(echo "$victims" | tr '\n' ' ')"
    # shellcheck disable=SC2086
    $pip uninstall -y $victims >/dev/null 2>&1
  fi

  # `pip uninstall` leaves the shared `nvidia/` namespace directory behind —
  # measured at 397MB of files pip no longer believes it installed. Sweep only
  # what pip has disowned: if it still lists a cuda package, we do not touch it.
  if ! $pip list --format=freeze 2>/dev/null | cut -d= -f1 \
       | grep -qiE '^(nvidia-|cuda-|triton$)'; then
    for orphan in "$sp/nvidia" "$sp/triton" "$sp"/cuda "$sp"/cuda_*; do
      [ -d "$orphan" ] && rm -rf "$orphan" && echo "  swept orphaned $(basename "$orphan")/"
    done
  fi

  # The only honest test that the prune was safe.
  if $py -c "import $module" >/dev/null 2>&1; then
    after="$(du_mb "$sp")"
    ok "import $module still works — ${before}MB → ${after}MB (freed $((before - after))MB)"
  else
    bad "import $module FAILED after pruning — reinstall this module:"
    echo "        rm -rf $venv && bash scripts/studio/install.sh --profile all"
    return 1
  fi
}

rc=0
if [ "${1:-}" = "--all" ]; then
  for t in "${ALL_TARGETS[@]}"; do
    prune_one "${t%%:*}" "${t##*:}" || rc=1
  done
elif [ $# -ge 2 ]; then
  prune_one "$1" "$2" || rc=1
else
  echo "usage: $0 <venv-path> <import-name>   |   $0 --all" >&2
  exit 2
fi

say "Disk"
df -h . | tail -1
exit $rc
