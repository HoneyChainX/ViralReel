#!/usr/bin/env bash
# Thin wrapper: verify the studio platform (manifest validity, cost audit, module checks).
#   bash scripts/studio/doctor.sh [--profile ...]        # exit 1 on any red check
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
exec python3 scripts/studio/platform.py doctor "$@"
