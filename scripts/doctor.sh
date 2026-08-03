#!/usr/bin/env bash
# Verifies dependencies, keys, and — importantly — that no paid generator key
# has crept in. A surprise bill is a strategy failure, not just an expense.
#
# Sections map to the operating mode (docs/DECISIONS.md): production is required,
# automated publishing is PHASE 2 and only warns. Manual-first distribution runs
# through handoffs/upload-episode.md and needs no credentials at all.
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
# ffmpeg: system install, or the static build scripts/get-ffmpeg.sh drops in
# vendor/ffbin (works in containers with no root — verified in the cloud session).
if command -v ffmpeg >/dev/null 2>&1 && command -v ffprobe >/dev/null 2>&1; then
  ok "ffmpeg $(ffmpeg -version 2>&1 | head -1 | cut -d' ' -f3)"
elif [ -x vendor/ffbin/bin/ffmpeg ] && [ -x vendor/ffbin/bin/ffprobe ]; then
  ok "ffmpeg (static, vendor/ffbin) — add to PATH: export PATH=\$PWD/vendor/ffbin/bin:\$PATH"
else
  bad "ffmpeg/ffprobe not found — apt install ffmpeg, or: bash scripts/get-ffmpeg.sh"
fi

echo ""
echo "Vendors"
[ -d vendor/openmontage ] && ok "OpenMontage cloned"          || bad "OpenMontage missing — run make setup"
[ -d vendor/yt-agent ]    && ok "youtube-automation-agent cloned" || warn "yt-agent missing — phase 2 only; run make setup when automating"
[ -d vendor/openmontage/.venv ] && ok "OpenMontage venv"      || warn "no venv — run make setup"

OM_ENV=vendor/openmontage/.env
YT_ENV=vendor/yt-agent/.env

# A key is SET only if it has a real value. `KEY=` followed by whitespace and a
# `# comment` is EMPTY — how both templates document their keys. Same matcher as
# the CI secret scanner.
getkey() { [ -f "$1" ] && grep -E "^$2=[ \t]*[^[:space:]#]" "$1" >/dev/null 2>&1; }

echo ""
echo "Production keys"
# ElevenLabs may arrive via the process environment (e.g. a Claude environment
# variable) instead of the .env file — both work: OpenMontage reads the process
# env, and setup.sh copies the env var into .env for file-only tools.
if [ -n "${ELEVENLABS_API_KEY:-}" ]; then ok "ELEVENLABS_API_KEY set (environment)"
elif getkey "$OM_ENV" ELEVENLABS_API_KEY; then ok "ELEVENLABS_API_KEY set (.env)"
else warn "ELEVENLABS_API_KEY absent — VO falls back to Piper (free, lower quality). Fallback must be a per-episode decision, never silent: see docs/DECISIONS.md"; fi

echo ""
echo "Cost controls  (these MUST stay empty)"
# Expanded after auditing what the vendor code actually reads — the original list
# of 8 missed 11+ live aliases (FAL_AI_API_KEY verified at tools/video/_shared.py:422).
# GOOGLE_API_KEY / GEMINI_API_KEY count as paid *here*: in OpenMontage's env they
# unlock paid Imagen/Veo. (GEMINI_API_KEY in yt-agent's env is the free publish loop.)
PAID=(FAL_KEY FAL_AI_API_KEY RUNWAY_API_KEY KLING_API_KEY XAI_API_KEY SUNO_API_KEY \
      ATLASCLOUD_API_KEY HEYGEN_API_KEY OPENAI_API_KEY REPLICATE_API_TOKEN \
      HIGGSFIELD_API_KEY HIGGSFIELD_API_SECRET HIGGSFIELD_KEY \
      GOOGLE_API_KEY GEMINI_API_KEY DASHSCOPE_API_KEY DOUBAO_SPEECH_API_KEY \
      VOLC_ACCESSKEY VOLC_SECRETKEY AZURE_SPEECH_KEY)
LEAK=0
for k in "${PAID[@]}"; do
  if getkey "$OM_ENV" "$k"; then bad "$k is SET in openmontage/.env — this bills per generation. Unset it (docs/04-stack.md)"; LEAK=1; fi
done
[ "$LEAK" -eq 0 ] && ok "no paid generator keys — marginal cost stays \$0.00"

echo ""
echo "Brand font"
# The CC desktop app does not exist for Linux, so on a Linux render host Acumin
# cannot be synced — renders fall back to Liberation Sans (digits measured safe:
# uniform widths in both weights). That fallback must be LOUD, never discovered
# in a published video. Platform paths: docs/09-adobe-connectors.md.
if command -v fc-list >/dev/null 2>&1; then
  if fc-list -q "Acumin Pro" 2>/dev/null; then ok "Acumin Pro installed"
  else warn "Acumin Pro NOT installed — renders on this host use Liberation Sans. Fine for drafts; the founder decides if it ships (docs/DECISIONS.md)"; fi
else
  warn "fc-list unavailable — cannot verify fonts; check before rendering"
fi

echo ""
echo "Publish log  (what makes the 2/day cap real)"
EPS=$(find content/episodes -maxdepth 1 -mindepth 1 -type d ! -name '_*' 2>/dev/null | wc -l)
if [ -f content/publish_log.json ]; then ok "content/publish_log.json present"
elif [ "$EPS" -gt 0 ]; then warn "episodes exist but no publish log — every upload must end with: python3 scripts/log_publish.py --slug <slug>"
else ok "no episodes yet — log will be created by the first upload"; fi

echo ""
echo "Phase 2 — automated publishing (yt-agent). Not required in manual-first mode."
if getkey "$YT_ENV" GEMINI_API_KEY; then ok "GEMINI_API_KEY set (free tier)"
else warn "GEMINI_API_KEY empty — only needed when automating distribution"; fi
[ -f vendor/yt-agent/config/credentials.json ] && ok "OAuth credentials.json present" \
  || warn "no OAuth credentials — only needed for automated upload (npm run walkthrough)"
[ -f vendor/yt-agent/config/tokens.json ] && ok "OAuth tokens.json present" \
  || warn "no OAuth tokens — only needed for automated upload"
if grep -E '^DEFAULT_PRIVACY_STATUS=private' "$YT_ENV" >/dev/null 2>&1; then
  ok "DEFAULT_PRIVACY_STATUS=private"
else
  warn "DEFAULT_PRIVACY_STATUS not 'private' — must be fixed before phase 2 goes live"
fi
if grep -E '^PRIVACY_STATUS=' "$YT_ENV" >/dev/null 2>&1; then
  warn "PRIVACY_STATUS found — that name is INERT, the vendor reads DEFAULT_PRIVACY_STATUS"
fi

echo ""
[ "$FAIL" -eq 0 ] && echo "Ready." || echo "Not ready — fix the FAILs above."
exit $FAIL
