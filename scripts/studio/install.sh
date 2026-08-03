#!/usr/bin/env bash
# Thin wrapper: install the studio platform modules for a profile.
#   bash scripts/studio/install.sh [--profile core|distribution|genai|animation|voice|all]
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
exec python3 scripts/studio/platform.py install "$@"
