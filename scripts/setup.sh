#!/usr/bin/env bash
# Clones the two vendor repos and templates their .env files.
# Neither vendor is forked or patched — upstream fixes flow in with a git pull.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

say() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }

mkdir -p vendor out content/episodes content/reports

say "Cloning OpenMontage (production)"
if [ -d vendor/openmontage/.git ]; then
  git -C vendor/openmontage pull --ff-only || echo "  (pull skipped)"
else
  git clone --depth 1 https://github.com/calesthio/OpenMontage.git vendor/openmontage
fi

say "Cloning youtube-automation-agent (distribution)"
if [ -d vendor/yt-agent/.git ]; then
  git -C vendor/yt-agent pull --ff-only || echo "  (pull skipped)"
else
  git clone --depth 1 https://github.com/darkzOGx/youtube-automation-agent.git vendor/yt-agent
fi

say "Installing OpenMontage"
(
  cd vendor/openmontage
  if [ -f Makefile ]; then
    make setup
  else
    python3 -m venv .venv
    # shellcheck disable=SC1091
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    [ -d remotion-composer ] && (cd remotion-composer && npm install)
    python -m pip install piper-tts   # free TTS fallback, keeps cost at zero
  fi
)

say "Installing youtube-automation-agent"
( cd vendor/yt-agent && npm install )

say "Templating .env files"
[ -f vendor/openmontage/.env ] || cp config/env.openmontage.template vendor/openmontage/.env
[ -f vendor/yt-agent/.env ]    || cp config/env.ytagent.template    vendor/yt-agent/.env

cat <<'EOF'

Setup complete. Two things left, both manual on purpose:

  1. Add ELEVENLABS_API_KEY to vendor/openmontage/.env   (your existing subscription)
     Leave every other generator key EMPTY — that is the cost control.

  2. cd vendor/yt-agent && npm run walkthrough
     Interactive: YouTube OAuth + a free Gemini key. Keep PRIVACY_STATUS=private.

Then: make doctor
EOF
