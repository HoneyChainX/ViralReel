#!/usr/bin/env bash
# Bring a fresh Ubuntu (normally inside WSL2 on Windows 11) up to a working
# ViralReel host. Idempotent: safe to re-run after a failure, and safe to re-run
# when everything is already fine.
#
#   bash install/wsl/bootstrap.sh                       # tools + core platform
#   bash install/wsl/bootstrap.sh --profile none        # tools only, no vendors
#   bash install/wsl/bootstrap.sh --profile all --with-claude --with-services
#
# Run it as the normal user, NOT as root — it calls sudo only where it must, and
# the services it installs must run as the human who owns the checkout.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

PROFILE=core
WITH_CLAUDE=0
WITH_SERVICES=0
SKIP_APT=0
NODE_MAJOR=22            # Remotion and the HyperFrames lane need 22+

while [ $# -gt 0 ]; do
  case "$1" in
    --profile)       PROFILE="$2"; shift ;;
    --with-claude)   WITH_CLAUDE=1 ;;
    --with-services) WITH_SERVICES=1 ;;
    --skip-apt)      SKIP_APT=1 ;;
    -h|--help)       sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
  shift
done

say()  { printf '\n\033[1m==> %s\033[0m\n' "$1"; }
ok()   { printf '  \033[32mOK\033[0m    %s\n' "$1"; }
warn() { printf '  \033[33mWARN\033[0m  %s\n' "$1"; }
die()  { printf '  \033[31mFAIL\033[0m  %s\n' "$1" >&2; exit 1; }

# ── preconditions ───────────────────────────────────────────────────────────

say "Checking the host"
[ "$(uname -s)" = "Linux" ] || die "this installs the Linux stack — on Windows run it inside WSL2 (see install/windows/)"
[ "$(id -u)" -ne 0 ] || die "do not run as root; run as your normal user and let sudo prompt"
command -v sudo >/dev/null || die "sudo is required"

if grep -qi microsoft /proc/version 2>/dev/null; then
  ok "WSL detected: ${WSL_DISTRO_NAME:-unknown distro}"
  # /mnt/c is a 9p mount into Windows; building here is many times slower and
  # breaks file modes that venvs and git rely on.
  case "$ROOT" in
    /mnt/*) die "the repo is on the Windows filesystem ($ROOT). Move it into the Linux filesystem (e.g. ~/ViralReel) — renders and npm installs are dramatically slower on /mnt, and permissions do not survive." ;;
  esac
  ok "repo is on the Linux filesystem"
else
  ok "native Linux (not WSL) — everything below still applies"
fi

FREE_GB=$(df -BG --output=avail . | tail -1 | tr -dc '0-9')
if [ "$PROFILE" != "none" ] && [ "${FREE_GB:-0}" -lt 40 ]; then
  warn "${FREE_GB}GB free — a full vendor tree is ~26GB plus renders. Consider --profile none for now."
else
  ok "${FREE_GB}GB free"
fi

# ── system packages ─────────────────────────────────────────────────────────

if [ "$SKIP_APT" -eq 0 ]; then
  say "System packages"
  sudo apt-get update -qq
  # python3-yaml comes from apt on purpose: Ubuntu 24.04 marks the system
  # interpreter externally-managed (PEP 668), so `pip install pyyaml` into it
  # fails, and our loaders (platform.py, jobd.py) run on system python.
  sudo apt-get install -y -qq \
    git curl ca-certificates xz-utils unzip jq \
    build-essential pkg-config \
    python3 python3-venv python3-pip python3-yaml \
    fonts-dejavu-core fonts-liberation fontconfig \
    libnss3 libgbm1 libasound2t64 libatk-bridge2.0-0t64 libatk1.0-0t64 \
    libcups2t64 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libpango-1.0-0 libcairo2 2>/dev/null \
  || sudo apt-get install -y -qq \
    git curl ca-certificates xz-utils unzip jq build-essential pkg-config \
    python3 python3-venv python3-pip python3-yaml \
    fonts-dejavu-core fonts-liberation fontconfig \
    libnss3 libgbm1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 \
    libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libpango-1.0-0 libcairo2
  ok "base packages installed"

  # Every composition in this repo asks for Liberation Sans. A host with only
  # DejaVu does not fail — it silently substitutes and re-renders in different
  # metrics, which is precisely the class of error DECISIONS D3 exists to stop
  # anyone from discovering inside a published video.
  if fc-list 2>/dev/null | grep -qi liberation; then
    ok "Liberation fonts present (renders match the reference)"
  else
    warn "Liberation fonts still missing after install — renders WILL substitute silently (DECISIONS D3). Fix before rendering: sudo apt-get install fonts-liberation"
  fi
else
  warn "skipping apt (--skip-apt)"
fi

# ── python 3.11 for the 3D lane ─────────────────────────────────────────────

say "Python 3.11 (required by bpy)"
# bpy publishes cp311 wheels and nothing else — no 3.10, no 3.12. Ubuntu 24.04
# ships 3.12, so on a stock host `pip install bpy` fails with "no matching
# distribution" and the whole 3D lane goes with it. The interpreter is therefore
# a real dependency, not a preference.
PY311=""
if command -v python3.11 >/dev/null 2>&1; then
  PY311="$(command -v python3.11)"
  ok "python3.11 already present"
elif [ "$SKIP_APT" -eq 0 ]; then
  if sudo apt-get install -y -qq python3.11 python3.11-venv 2>/dev/null \
     && command -v python3.11 >/dev/null 2>&1; then
    PY311="$(command -v python3.11)"
    ok "installed python3.11 from the distro"
  else
    warn "python3.11 is not in this distro's archive (Ubuntu 24.04 ships 3.12)"
    # uv fetches a standalone CPython build without adding a third-party apt
    # repository, and OpenMontage needs uv anyway.
    if ! command -v uv >/dev/null 2>&1; then
      curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1 || true
      export PATH="$HOME/.local/bin:$PATH"
    fi
    if command -v uv >/dev/null 2>&1 && uv python install 3.11 >/dev/null 2>&1; then
      PY311="$(uv python find 3.11 2>/dev/null || true)"
      [ -n "$PY311" ] && ok "installed python3.11 via uv ($PY311)"
    fi
  fi
fi
if [ -n "$PY311" ]; then
  # The manifest reads this when building the blender venv, so the 3D lane no
  # longer depends on whatever `python3` happens to mean on this host.
  export VIRALREEL_PY311="$PY311"
  grep -q 'VIRALREEL_PY311' "$HOME/.profile" 2>/dev/null || \
    printf '\n# ViralReel: bpy needs CPython 3.11 (docs/15)\nexport VIRALREEL_PY311=%s\n' \
      "$PY311" >> "$HOME/.profile"
else
  warn "no python3.11 — the 3D lane (blender-headless, film-chunk) will not install"
  warn "install it manually, then re-run: sudo add-apt-repository ppa:deadsnakes/ppa"
fi

say "uv"
# OpenMontage's Makefile prefers uv and pins its own Python; without uv that
# venv silently becomes whatever python3 is, which is not what was verified.
if command -v uv >/dev/null 2>&1; then
  ok "uv $(uv --version 2>/dev/null | awk '{print $2}')"
else
  curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1 \
    && export PATH="$HOME/.local/bin:$PATH" \
    && ok "uv installed" || warn "uv install failed — OpenMontage may build against the wrong Python"
fi

say "Node.js"
CURRENT_NODE=$(node -v 2>/dev/null | tr -dc '0-9.' | cut -d. -f1 || true)
if [ -n "${CURRENT_NODE:-}" ] && [ "$CURRENT_NODE" -ge "$NODE_MAJOR" ]; then
  ok "node $(node -v)"
elif [ "$SKIP_APT" -eq 1 ]; then
  warn "node ${CURRENT_NODE:-absent} is below $NODE_MAJOR and --skip-apt was given"
else
  # Ubuntu ships a node too old for Remotion; NodeSource is the vendor's own repo.
  curl -fsSL "https://deb.nodesource.com/setup_${NODE_MAJOR}.x" | sudo -E bash - >/dev/null
  sudo apt-get install -y -qq nodejs
  ok "node $(node -v)"
fi

# ── ffmpeg ──────────────────────────────────────────────────────────────────

say "ffmpeg"
# Deliberately the vendored static build rather than apt's: delivery QC scores
# VMAF, and a distro ffmpeg without libvmaf would drop that check silently.
if [ -x vendor/ffbin/bin/ffmpeg ]; then
  ok "vendored ffmpeg present"
else
  bash scripts/get-ffmpeg.sh
fi
vendor/ffbin/bin/ffmpeg -version 2>/dev/null | grep -q -- --enable-libvmaf \
  && ok "libvmaf available (delivery QC can score)" \
  || warn "vendored ffmpeg has no libvmaf — VMAF scoring will be unavailable"

PROFILE_LINE="export PATH=\"$ROOT/vendor/ffbin/bin:\$PATH\""
if ! grep -Fqx "$PROFILE_LINE" "$HOME/.profile" 2>/dev/null; then
  printf '\n# ViralReel: vendored ffmpeg with libvmaf (docs/15)\n%s\n' "$PROFILE_LINE" >> "$HOME/.profile"
  ok "added vendored ffmpeg to PATH in ~/.profile (new shells)"
fi
export PATH="$ROOT/vendor/ffbin/bin:$PATH"

# ── control server ──────────────────────────────────────────────────────────

say "Studio control server"
# Its own venv, not system python: the MCP SDK pulls pydantic and starlette, and
# Ubuntu 24.04 refuses pip installs into the system interpreter (PEP 668).
if [ ! -x server/.venv/bin/python ]; then
  python3 -m venv server/.venv
fi
server/.venv/bin/pip install --quiet --upgrade pip
if server/.venv/bin/pip install --quiet -r server/requirements.txt; then
  ok "MCP SDK installed ($(server/.venv/bin/pip show mcp 2>/dev/null | awk '/^Version/{print $2}'))"
  # Import the module rather than trust the install: a partial wheel still
  # reports as installed and then fails at session start.
  if server/.venv/bin/python -c "from mcp.server import MCPServer" 2>/dev/null; then
    ok "control server imports — .mcp.json will load it in Claude Code"
  else
    warn "MCP SDK installed but does not import — re-run: server/.venv/bin/pip install -r server/requirements.txt"
  fi
else
  warn "could not install the MCP SDK — the studio tools will not appear in Claude Code"
fi

# ── claude code (optional) ──────────────────────────────────────────────────

if [ "$WITH_CLAUDE" -eq 1 ]; then
  say "Claude Code CLI"
  if command -v claude >/dev/null 2>&1; then
    ok "claude $(claude --version 2>/dev/null | head -1)"
  else
    curl -fsSL https://claude.ai/install.sh | bash
    export PATH="$HOME/.local/bin:$PATH"
    command -v claude >/dev/null && ok "installed $(claude --version 2>/dev/null | head -1)" \
      || warn "installer finished but 'claude' is not on PATH yet — open a new shell"
  fi
  cat <<'EOF'

  Remote Control needs an interactive claude.ai login once — it cannot be
  scripted, and API keys are rejected. In this directory run:

      claude          # then: /login   (and accept the workspace trust prompt)

EOF
fi

# ── platform modules ────────────────────────────────────────────────────────

if [ "$PROFILE" != "none" ]; then
  say "Studio platform modules (profile: $PROFILE)"
  warn "this clones and builds a lot — expect tens of minutes and ~26GB for 'all'"
  bash scripts/studio/install.sh --profile "$PROFILE" || warn "some modules failed — see the output above, then re-run"

  # Measured on this repo: whisperx re-resolved to a CUDA torch and carried
  # 4.7GB of nvidia wheels, argos-translate held 3.4GB of cuda-toolkit reached
  # through a dependency torch never touches. On a CPU host that is 8GB that
  # cannot execute a single kernel. The pruner no-ops on a GPU host.
  say "Removing CUDA payload from a CPU-only host"
  bash scripts/studio/prune-cuda.sh --all || warn "prune reported a problem — see above"
fi

# ── services ────────────────────────────────────────────────────────────────

if [ "$WITH_SERVICES" -eq 1 ]; then
  say "Services"
  if [ -d /run/systemd/system ]; then
    sudo bash install/services/install-services.sh $([ "$WITH_CLAUDE" -eq 1 ] && echo --with-remote-control)
  else
    warn "systemd is not running — enable it first, then re-run with --with-services:"
    echo "      printf '[boot]\\nsystemd=true\\n' | sudo tee -a /etc/wsl.conf"
    echo "      # then in Windows PowerShell:  wsl --shutdown    (and reopen the distro)"
  fi
fi

# ── verdict ─────────────────────────────────────────────────────────────────

say "Host report"
python3 scripts/studio/hostinfo.py || true

echo ""
if python3 scripts/studio/hostinfo.py --assert-ready >/dev/null 2>&1; then
  printf '\033[32mHost is ready.\033[0m  Next: python3 scripts/studio/jobd.py enqueue doctor\n'
else
  printf '\033[33mHost is not fully ready — see the blocking items above.\033[0m\n'
fi

cat <<'EOF'

Two ways to reach this machine from elsewhere (docs/15):

  claude.ai/code   Remote Control. Nothing to expose; log in once with
                   `claude` then start viralreel-remote-control.

  claude.ai chat   The custom connector. Needs a public HTTPS URL and a
                   passphrase, in this order:

                     server/.venv/bin/python server/studio_auth.py set-passphrase
                     bash install/tunnel/expose.sh --tailscale
                     make connector URL=https://<the-url-it-printed>

EOF
