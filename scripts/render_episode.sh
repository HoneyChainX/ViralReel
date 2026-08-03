#!/usr/bin/env bash
# Render one episode with the PriceArchaeology Remotion composition.
#
#   bash scripts/render_episode.sh <slug>
#
# What it does, in order:
#   1. Materialises brand/remotion/ into vendor/openmontage/remotion-composer/src/
#      (the vendor clone is never committed; our repo is the source of truth)
#   2. Registers the composition in Root.tsx (idempotent, marker-guarded)
#   3. Stages the episode's assets + VO into the composer's public/<slug>/
#   4. Builds render props from scene_plan.json (+ captions.json if present)
#   5. Renders 1080x1920@30 via headless Chromium
#   6. Loudness-normalises to -14 LUFS / -1 dBTP (delivery spec) -> out/<slug>.mp4
set -euo pipefail

SLUG="${1:?usage: render_episode.sh <slug>}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EP="$ROOT/content/episodes/$SLUG"
RC="$ROOT/vendor/openmontage/remotion-composer"
export PATH="$ROOT/vendor/ffbin/bin:$PATH"

[ -f "$EP/scene_plan.json" ] || { echo "no scene_plan.json for $SLUG"; exit 1; }
[ -f "$EP/vo.mp3" ]          || { echo "no vo.mp3 for $SLUG"; exit 1; }
[ -d "$RC/node_modules" ]    || { echo "remotion-composer not installed — run make setup"; exit 1; }

echo "==> [1/6] Materialising brand composition into the composer"
# A dedicated entry (pa-entry.tsx) registers ONLY our composition. The vendor's
# index.tsx pulls in compositions that load Google Fonts at page load, which is a
# fatal NetworkError in an egress-blocked environment. The vendor's Root.tsx is
# never touched.
cp "$ROOT/brand/PriceOdometer.tsx"             "$RC/src/PriceOdometer.tsx"
cp "$ROOT/brand/remotion/PriceArchaeology.tsx" "$RC/src/PriceArchaeology.tsx"
cp "$ROOT/brand/remotion/pa-entry.tsx"         "$RC/src/pa-entry.tsx"

echo "==> [2/6] Entry ready (vendor Root untouched)"

echo "==> [3/6] Staging assets + VO into composer public/"
mkdir -p "$RC/public/$SLUG"
# scene assets are referenced as bare filenames relative to public/<slug>/
find "$EP/assets" -maxdepth 1 -type f -exec cp {} "$RC/public/$SLUG/" \;
cp "$EP/vo.mp3" "$RC/public/$SLUG/vo.mp3"

echo "==> [4/6] Building render props"
python3 - "$EP" "$SLUG" <<'PY'
import json, pathlib, sys
ep, slug = pathlib.Path(sys.argv[1]), sys.argv[2]
plan = json.loads((ep / "scene_plan.json").read_text())
scenes = plan["scenes"]
# assets in the plan may carry an assets/ prefix — strip to bare filenames
for s in scenes:
    s["asset"] = s["asset"].split("/")[-1]
captions = []
cap_file = ep / "captions.json"
if cap_file.exists():
    captions = json.loads(cap_file.read_text())
props = {"slug": slug, "scenes": scenes, "voSrc": "vo.mp3", "captions": captions}
(ep / "render_props.json").write_text(json.dumps(props, indent=2))
print(f"  {len(scenes)} scenes, {len(captions)} caption chunks")
PY

echo "==> [5/6] Remotion render (headless shell)"
# Remotion launches Chromium with the OLD headless mode, which modern Chromium
# removed ("Old Headless mode has been removed from the Chrome binary" — found by
# the dry run). Playwright ships chrome-headless-shell, the standalone old-headless
# implementation, alongside its Chromium — use that.
SHELL_BIN="$(find /opt/pw-browsers -name headless_shell -type f 2>/dev/null | head -1)"
BROWSER="${SHELL_BIN:-/opt/pw-browsers/chromium}"
echo "    browser: $BROWSER"
cd "$RC"
npx remotion render src/pa-entry.tsx PriceArchaeology "/tmp/$SLUG-raw.mp4" \
  --props="$EP/render_props.json" \
  --browser-executable="$BROWSER" \
  --codec=h264 --crf=18 --concurrency=2 --timeout=120000 2>&1 | tail -15

echo "==> [6/6] Loudness normalise to -14 LUFS / -1 dBTP"
mkdir -p "$ROOT/out"
ffmpeg -y -loglevel error -i "/tmp/$SLUG-raw.mp4" \
  -af "loudnorm=I=-14:TP=-1:LRA=11" \
  -c:v copy -c:a aac -b:a 192k "$ROOT/out/$SLUG.mp4"
rm -f "/tmp/$SLUG-raw.mp4"

ffprobe -v error -select_streams v:0 -show_entries stream=width,height \
  -show_entries format=duration -of default=nw=1 "$ROOT/out/$SLUG.mp4"
echo "Rendered: out/$SLUG.mp4"
