#!/usr/bin/env bash
# Verifies dependencies, keys, and — importantly — that no paid generator key
# has crept in. A surprise bill is a strategy failure, not just an expense.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

FAIL=0
ok()   { printf '  \033[32mOK\033[0m    %s\n' "$1"; }
warn() { printf '  \033[33mWARN\033[0m  %s\n' "$1"; }
bad()  { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; FAIL=1; }

need() {
  if command -v "$1" >/dev/null 2>&1; then ok "$1 $("$1" --version 2>&1 | head -1)"
  else bad "$1 not found — $2"; fi
}

echo "Dependencies"
need git     "install git"
need python3 "need Python 3.10+"
need node    "need Node.js 18+ (22+ for HyperFrames)"
need ffmpeg  "brew install ffmpeg / apt install ffmpeg"

echo ""
echo "Vendors"
[ -d vendor/openmontage ] && ok "OpenMontage cloned"          || bad "OpenMontage missing — run make setup"
[ -d vendor/yt-agent ]    && ok "youtube-automation-agent cloned" || bad "yt-agent missing — run make setup"
[ -d vendor/openmontage/.venv ] && ok "OpenMontage venv"      || warn "no venv — run make setup"

echo ""
echo "Keys"
OM_ENV=vendor/openmontage/.env
YT_ENV=vendor/yt-agent/.env

getkey() { [ -f "$1" ] && grep -E "^$2=." "$1" >/dev/null 2>&1; }

if getkey "$OM_ENV" ELEVENLABS_API_KEY; then ok "ELEVENLABS_API_KEY set (your subscription)"
else warn "ELEVENLABS_API_KEY empty — VO falls back to Piper (free, lower quality)"; fi

if getkey "$YT_ENV" GEMINI_API_KEY; then ok "GEMINI_API_KEY set (free tier)"
else bad "GEMINI_API_KEY missing — yt-agent needs an LLM key"; fi

echo ""
echo "Cost controls  (these MUST be empty)"
PAID=(FAL_KEY RUNWAY_API_KEY KLING_API_KEY XAI_API_KEY SUNO_API_KEY \
      ATLASCLOUD_API_KEY HEYGEN_API_KEY OPENAI_API_KEY)
LEAK=0
for k in "${PAID[@]}"; do
  if getkey "$OM_ENV" "$k"; then bad "$k is SET — this bills per generation. Unset it (docs/04-stack.md)"; LEAK=1; fi
done
[ "$LEAK" -eq 0 ] && ok "no paid generator keys — marginal cost stays \$0.00"

echo ""
echo "Publishing safety"
if grep -E '^PRIVACY_STATUS=private' "$YT_ENV" >/dev/null 2>&1; then
  ok "PRIVACY_STATUS=private"
else
  bad "PRIVACY_STATUS is not 'private' — every upload must land private (compliance C10)"
fi

echo ""
[ "$FAIL" -eq 0 ] && echo "Ready." || echo "Not ready — fix the FAILs above."
exit $FAIL
