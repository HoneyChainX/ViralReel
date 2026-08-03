#!/usr/bin/env python3
"""DramaClaw seam — health check for the self-hosted script→film engine.

DramaClaw (docs/11) runs as a Docker-hosted FastAPI backend whose inference goes to a
configurable OpenAI-compatible gateway. Two things matter to this studio:

  1. COST: the gateway URL is the entire cost control. Unset gateway = nothing billable.
     This adapter refuses to configure a gateway itself — that is a founder decision
     (DECISIONS D8), so all it does is *report* what the running instance points at.
  2. DRIVING: story-showrunner drives DramaClaw through its own API/skills once a founder
     has stood the stack up (`docker compose up` in vendor/dramaclaw). We deliberately do
     not wrap its full API here until upstream's schema is pinned — a half-guessed client
     is worse than none.

Usage:
  python3 studio/adapters/dramaclaw_client.py --selftest      # is a local instance up?

Environment:
  DRAMACLAW_HOST   default 127.0.0.1:8000
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

HOST = os.environ.get("DRAMACLAW_HOST", "127.0.0.1:8000")
BASE = f"http://{HOST}"


def health() -> dict | None:
    for path in ("/health", "/api/health", "/docs"):
        try:
            with urllib.request.urlopen(f"{BASE}{path}", timeout=5.0) as r:
                body = r.read()
                try:
                    return json.loads(body)
                except json.JSONDecodeError:
                    return {"status": "up", "endpoint": path}
        except (urllib.error.URLError, OSError):
            continue
    return None


def main() -> int:
    if "--selftest" in sys.argv[1:]:
        h = health()
        if h is None:
            # Not running is the normal state on most hosts — the stack is founder-started.
            print(f"dramaclaw selftest: OK — no instance at {BASE} "
                  "(start one: cd vendor/dramaclaw && docker compose up)")
            return 0
        print(f"dramaclaw selftest: OK — instance up at {BASE}: {h}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
