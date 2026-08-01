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

# A key is SET only if it has a real value. `KEY=` followed by whitespace and a
# `# comment` is EMPTY — which is how both our template and OpenMontage's
# .env.example document their keys. Matching `^KEY=.` treats every documented-but-
# empty key as populated, which reported all eight paid keys as billing-enabled on
# a clean install. Same matcher as the CI secret scanner.
getkey() { [ -f "$1" ] && grep -E "^$2=[ \t]*[^[:space:]#]" "$1" >/dev/null 2>&1; }

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
echo "YouTube OAuth  (NOT env vars — the walkthrough writes these files)"
YT_CREDS=vendor/yt-agent/config/credentials.json
YT_TOKENS=vendor/yt-agent/config/tokens.json
if [ -f "$YT_CREDS" ]; then ok "config/credentials.json present (client id + secret)"
else bad "no config/credentials.json — run: cd vendor/yt-agent && npm run walkthrough"; fi
if [ -f "$YT_TOKENS" ]; then ok "config/tokens.json present (refresh token)"
else bad "no config/tokens.json — the browser consent step has not completed"; fi

echo ""
echo "Publishing safety"
# The variable is DEFAULT_PRIVACY_STATUS. PRIVACY_STATUS is not read by the
# vendor; if it is present it is a leftover from the old template and is inert.
if grep -E '^DEFAULT_PRIVACY_STATUS=private' "$YT_ENV" >/dev/null 2>&1; then
  ok "DEFAULT_PRIVACY_STATUS=private"
elif grep -E '^DEFAULT_PRIVACY_STATUS=' "$YT_ENV" >/dev/null 2>&1; then
  bad "DEFAULT_PRIVACY_STATUS is set to something other than 'private'"
else
  warn "DEFAULT_PRIVACY_STATUS unset — vendor falls back to 'private', but set it explicitly"
fi
if grep -E '^PRIVACY_STATUS=' "$YT_ENV" >/dev/null 2>&1; then
  warn "PRIVACY_STATUS found — that name is INERT, the vendor reads DEFAULT_PRIVACY_STATUS"
fi

echo ""
[ "$FAIL" -eq 0 ] && echo "Ready." || echo "Not ready — fix the FAILs above."
exit $FAIL
