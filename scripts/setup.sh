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

say "Pinning OpenMontage cost + checkpoint config"
# Verified against vendor/openmontage/config.yaml + lib/config_model.py: the vendor
# ships budget.mode=warn with $10 headroom and checkpoint.policy=guided. Warn-mode
# with headroom is not a cap — pin to cap/$0 so a paid tool CANNOT bill even if a
# key ever leaks in, and auto_noncreative so mechanical stages run unattended while
# creative checkpoints still stop for a human (the docs/03 handoff contract).
python3 - <<'PYEOF'
import pathlib, re
cfg = pathlib.Path("vendor/openmontage/config.yaml")
if cfg.exists():
    t = cfg.read_text()
    t = re.sub(r"(?m)^(\s*mode:)\s*\S+(\s*#.*)?$",  r"\1 cap\2",  t, count=1)
    t = re.sub(r"(?m)^(\s*total_usd:)\s*\S+",       r"\1 0.00",   t, count=1)
    t = re.sub(r"(?m)^(\s*policy:)\s*\S+(\s*#.*)?$", r"\1 auto_noncreative\2", t, count=1)
    cfg.write_text(t)
    print("  pinned: budget.mode=cap, budget.total_usd=0.00, checkpoint.policy=auto_noncreative")
else:
    print("  (no vendor config.yaml yet — skipped)")
PYEOF

say "Templating .env files"
# OpenMontage's own `make setup` already ran `cp .env.example .env`, so the guard
# below is always a no-op for it — our template never lands. That is fine: their
# .env.example documents every provider key and ships them all EMPTY, which is
# exactly the cost control we want. What we add is the reason, so the next person
# to open the file knows the blanks are deliberate.
if [ -f vendor/openmontage/.env ] && ! grep -q "ViralReel cost control" vendor/openmontage/.env; then
  cat >> vendor/openmontage/.env <<'EOF'

# ── ViralReel cost control ──────────────────────────────────────────────────
# Every paid generator key above is intentionally EMPTY. OpenMontage scores and
# selects providers automatically; it cannot bill what it cannot see. Generated
# b-roll is also the strategically weaker option for a provenance channel —
# real archival footage is free AND more persuasive. See docs/04-stack.md.
# The ONLY key to fill here is ELEVENLABS_API_KEY (your existing subscription).
# `make doctor` fails if any paid key acquires a value.
EOF
  echo "  annotated vendor/openmontage/.env with the cost-control note"
fi
[ -f vendor/openmontage/.env ] || cp config/env.openmontage.template vendor/openmontage/.env
[ -f vendor/yt-agent/.env ]    || cp config/env.ytagent.template    vendor/yt-agent/.env

# If the ElevenLabs key is already in the process environment (e.g. set as a
# Claude environment variable), propagate it into the .env so file-only tools see
# it too. Nothing is printed; nothing leaves the machine.
if [ -n "${ELEVENLABS_API_KEY:-}" ] && ! grep -qE '^ELEVENLABS_API_KEY=[ \t]*[^[:space:]#]' vendor/openmontage/.env; then
  sed -i.bak 's|^ELEVENLABS_API_KEY=.*|ELEVENLABS_API_KEY='"$ELEVENLABS_API_KEY"'|' vendor/openmontage/.env \
    && rm -f vendor/openmontage/.env.bak
  echo "  ELEVENLABS_API_KEY propagated from environment into vendor/openmontage/.env"
fi

# Static ffmpeg fallback for hosts without root (verified in the cloud session)
if ! command -v ffmpeg >/dev/null 2>&1; then
  say "No system ffmpeg — fetching static build"
  bash scripts/get-ffmpeg.sh
fi

cat <<'EOF'

Setup complete. Two things left, both manual on purpose:

  1. Add ELEVENLABS_API_KEY to vendor/openmontage/.env   (your existing subscription)
     Leave every other generator key EMPTY — that is the cost control.

  2. cd vendor/yt-agent && npm run walkthrough
     Interactive: YouTube OAuth + a free Gemini key. Keep PRIVACY_STATUS=private.

Then: make doctor
EOF
