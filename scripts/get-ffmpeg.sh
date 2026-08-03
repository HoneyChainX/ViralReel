#!/usr/bin/env bash
# Fetch a static ffmpeg+ffprobe build into vendor/ffbin — for hosts where apt is
# unavailable (containers without root). Verified working in the cloud session:
# the BtbN build ran clean where johnvansickle returned 403 through the proxy.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/vendor/ffbin"

if [ -x "$DEST/bin/ffmpeg" ] && [ -x "$DEST/bin/ffprobe" ]; then
  echo "static ffmpeg already present at $DEST/bin"
  exit 0
fi

mkdir -p "$DEST"
cd "$DEST"

echo "==> Downloading static ffmpeg (BtbN master build, ~90MB)"
curl -fsSL --max-time 600 -o ff.tar.xz \
  "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz" \
  || curl -fsSL --max-time 600 -o ff.tar.xz \
  "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"

tar xf ff.tar.xz --strip-components=1
rm -f ff.tar.xz

# BtbN layout has bin/; johnvansickle puts binaries at the root — normalise.
if [ ! -x bin/ffmpeg ] && [ -x ffmpeg ]; then mkdir -p bin && mv ffmpeg ffprobe bin/; fi

bin/ffmpeg -version | head -1
bin/ffprobe -version | head -1
echo ""
echo "Done. Add to PATH for this shell:"
echo "  export PATH=\"$DEST/bin:\$PATH\""
