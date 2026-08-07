#!/usr/bin/env bash
# Where the disk went. Run this before blaming a render for dying — on this
# platform an out-of-space failure looks like an engine crash, and the vendor
# tree plus a frame sequence will fill a drive faster than anything else here.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."

echo "== filesystem =="
df -h . | tail -1
echo ""

echo "== largest directories in the repo =="
du -sh -- * .agents 2>/dev/null | sort -rh | head -12
echo ""

echo "== vendor modules over 500MB =="
du -sh vendor/* 2>/dev/null | sort -rh | awk '$1 ~ /G$/ || ($1 ~ /M$/ && $1+0 >= 500)' | head -15
echo ""

echo "== frame sequences (the usual culprit) =="
# A finished render leaves its PNGs behind; each 1080p frame is ~2MB, so a
# 384-frame act is most of a gigabyte sitting on disk with nothing to say.
found=0
while IFS= read -r d; do
  n=$(find "$d" -maxdepth 1 -name '*.png' | wc -l)
  [ "$n" -gt 20 ] && { printf '%8s  %5s frames  %s\n' "$(du -sh "$d" | cut -f1)" "$n" "$d"; found=1; }
done < <(find out content -type d 2>/dev/null)
[ "$found" -eq 0 ] && echo "  none"
echo ""

echo "== reclaimable caches =="
for c in ~/.cache/pip ~/.npm/_cacache ~/.cache/huggingface; do
  [ -d "$c" ] && printf '%8s  %s\n' "$(du -sh "$c" 2>/dev/null | cut -f1)" "$c"
done
exit 0
