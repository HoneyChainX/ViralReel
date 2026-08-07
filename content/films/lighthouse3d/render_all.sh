#!/bin/bash
# Resumable farm runner: renders every missing frame of every shot, then stamps DONE.
# Repo root from this script's own location — never a hardcoded path:
# these run from the job queue on hosts with a different user and checkout.
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
BPY=vendor/blender-headless/.venv/bin/python
declare -A TOTAL=( [s1]=120 [s2]=96 [s3]=144 )
for shot in s1 s2 s3; do
  mkdir -p out/lighthouse3d/$shot
  have=$(ls out/lighthouse3d/$shot/*.png 2>/dev/null | wc -l)
  want=${TOTAL[$shot]}
  if [ "$have" -lt "$want" ]; then
    echo "[$(date +%H:%M:%S)] $shot: $have/$want — rendering from $((have+1))"
    $BPY content/films/lighthouse3d/make_film.py $shot $((have+1)) >> out/lighthouse3d/render.log 2>&1
  fi
done
echo DONE > out/lighthouse3d/RENDER_COMPLETE
