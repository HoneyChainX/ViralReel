#!/bin/bash
cd /home/user/ViralReel
CHUNK=${1:-22}
have=$(ls out/keeper/a3/*.png 2>/dev/null | wc -l)
if [ "$have" -ge 384 ]; then echo A3_RENDER_COMPLETE; exit 0; fi
end=$(( have + CHUNK < 384 ? have + CHUNK : 384 ))
echo "a3 chunk: $((have+1))-$end of 384"
vendor/blender-headless/.venv/bin/python content/films/keeper/act3_3d.py $((have+1)) $end 2>&1 | grep -c "Saved:"
echo "A3_CHUNK_DONE $(ls out/keeper/a3/*.png | wc -l)/384"
