#!/usr/bin/env python3
"""
Append a publish event to content/publish_log.json — the file gate check C6 reads.

This writer exists because the Fable-5 review proved C6 was theatre: nothing wrote
the log, so the 2/day cap — the mitigation for the one risk rated Fatal — passed
unconditionally forever. The cap is only as real as this file.

Usage:
  python3 scripts/log_publish.py --slug four-k-tv           # record a publish (UTC now)
  python3 scripts/log_publish.py --slug four-k-tv --retract # mark it retracted

Retraction exists for the corrections/cap collision: a video unlisted under the
corrections policy (docs/05-compliance.md) no longer occupies a cap slot, so its
replacement re-render can publish the same day. gate.py's C6 skips retracted rows.

In manual-first mode the founder (or the Claude-Chrome upload runbook) runs this
as the LAST step of an upload — see handoffs/upload-episode.md. Stdlib only.
"""

import argparse
import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG = ROOT / "content" / "publish_log.json"


def load():
    if not LOG.exists():
        return []
    try:
        return json.loads(LOG.read_text())
    except json.JSONDecodeError:
        print(f"refusing to touch malformed {LOG} — fix it by hand", file=sys.stderr)
        sys.exit(2)


def main():
    ap = argparse.ArgumentParser(description="Record a publish (or retraction) in the C6 log")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--retract", action="store_true",
                    help="mark the most recent entry for this slug as retracted")
    args = ap.parse_args()

    rows = load()

    if args.retract:
        for row in reversed(rows):
            if row.get("slug") == args.slug and not row.get("retracted"):
                row["retracted"] = True
                row["retracted_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
                break
        else:
            print(f"no active entry for {args.slug} to retract", file=sys.stderr)
            sys.exit(1)
    else:
        episode = ROOT / "content" / "episodes" / args.slug
        if not episode.is_dir():
            print(f"no episode at {episode} — refusing to log a publish for it", file=sys.stderr)
            sys.exit(1)
        rows.append({
            "slug": args.slug,
            "published_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        })

    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_text(json.dumps(rows, indent=2) + "\n")
    verb = "retracted" if args.retract else "logged publish of"
    print(f"{verb} {args.slug}  ({sum(1 for r in rows if not r.get('retracted'))} active entries)")


if __name__ == "__main__":
    main()
