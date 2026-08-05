#!/bin/bash
# One bounded chunk: render up to $1 (default 20) missing frames, exit cleanly.
# Prints CHUNK_DONE + counts; prints FILM_RENDER_COMPLETE when every shot is full.
cd /home/user/ViralReel
CHUNK=${1:-20}
BPY=vendor/blender-headless/.venv/bin/python
declare -A TOTAL=( [s1]=120 [s2]=96 [s3]=144 )
for shot in s1 s2 s3; do
  mkdir -p out/lighthouse3d/$shot
  have=$(ls out/lighthouse3d/$shot/*.png 2>/dev/null | wc -l)
  want=${TOTAL[$shot]}
  if [ "$have" -lt "$want" ]; then
    end=$(( have + CHUNK < want ? have + CHUNK : want ))
    echo "chunk: $shot frames $((have+1))-$end of $want"
    $BPY content/films/lighthouse3d/make_film.py $shot $((have+1)) $end 2>&1 | grep -c "Saved:"
    echo "CHUNK_DONE $shot $(ls out/lighthouse3d/$shot/*.png | wc -l)/$want"
    exit 0
  fi
done
echo FILM_RENDER_COMPLETE
