#!/usr/bin/env python3
"""
The Price Archaeology publish gate.

Runs the ten checks in docs/05-compliance.md against a finished episode and
writes gate.json. Any FAIL blocks publish.

There is deliberately no --force flag. If you need to ship something this gate
rejects, fix the episode or change the rule in docs/05-compliance.md as a
documented decision. The value of the gate is entirely in its exceptionlessness.

Stdlib only — the gate must run even when nothing else is installed.
"""

import argparse
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys
from difflib import SequenceMatcher

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Mirrors config/channel.yaml. Kept here so the gate has no YAML dependency;
# scripts/doctor.sh warns if the two drift.
LIMITS = {
    "sources_per_claim": 2,
    "primary_sources_required": 1,
    # Lowered from 0.70 after empirical probing: legitimate on-beat scripts measured
    # a max pairwise similarity of 0.216 while a lazy noun-swap measured 0.762 — a
    # wide empty band. 0.50 keeps zero measured false-positive risk while cutting the
    # evasion margin. The mechanical check is a tripwire, not the defence: the
    # compliance-officer's semantic review is load-bearing (a one-word-per-sentence
    # pad scores 0.000 here and must be caught by the agent, not this number).
    "template_similarity_max": 0.50,
    "hard_cap_per_day": 2,
    "duration": (25.0, 50.0),
    "resolution": (1080, 1920),
    "allowed_licenses": {
        "public-domain", "cc0", "cc-by-4.0", "cc-by-sa-4.0", "pexels-license",
    },
}

# C8 — editorial bounds. Mechanical causes only; no partisan framing, no
# medical/financial advice. See docs/02-channel-bible.md §7.
#
# Rewritten after probing found the originals both leaked and over-fired: bare
# "conservative" flagged "a conservative estimate" (a phrase this channel will use
# weekly), while plural party language sailed through. Parties are matched in any
# number; liberal/conservative only when qualifying a political noun; medical and
# financial patterns are advice-shaped rather than bare verbs. These regexes catch
# the obvious; script-editor and compliance-officer own the judgement calls.
BANNED_PATTERNS = [
    (r"\b(democrats?|republicans?|gop|dems|left[- ]wing|right[- ]wing)\b", "partisan framing"),
    (r"\b(liberal|conservative)s?\s+(party|parties|politicians?|polic(?:y|ies)|agenda|government|administration|voters?)\b",
     "partisan framing"),
    (r"\b(biden|trump)\b|administration'?s fault|thanks to the president", "political blame"),
    (r"\byou should (invest|buy)\b|\bbuy the dip\b|\bfinancial advice\b|\bguaranteed returns?\b",
     "financial advice"),
    (r"\bthis (cures?|treats?|prevents?)\b|\bmedically proven\b|\bclinically proven\b", "medical claim"),
]


class Result:
    def __init__(self):
        self.checks = []

    def add(self, cid, ok, note):
        self.checks.append({"id": cid, "result": "PASS" if ok else "FAIL", "note": note})
        colour = "\033[32mPASS\033[0m" if ok else "\033[31mFAIL\033[0m"
        print(f"  {colour}  {cid}  {note}")
        return ok


def load_json(path):
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"  \033[31mmalformed JSON\033[0m {path}: {e}")
        return None


def sentence_signature(text):
    """Structural fingerprint of a script: the shape, not the topic.

    C7 targets what YouTube's mass-production detection targets — the same
    skeleton with the nouns swapped. So we compare sentence-length patterns
    and opening words, and deliberately ignore the subject matter.
    """
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    return [(len(s.split()), s.split()[0].lower() if s.split() else "") for s in sentences]


def similarity(a, b):
    return SequenceMatcher(None, [str(x) for x in a], [str(x) for x in b]).ratio()


def probe(video):
    """ffprobe -> (width, height, duration). Returns None if unavailable."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-show_entries", "format=duration",
             "-of", "json", str(video)],
            capture_output=True, text=True, timeout=60,
        )
        if out.returncode != 0:
            return None
        data = json.loads(out.stdout)
        stream = data["streams"][0]
        return int(stream["width"]), int(stream["height"]), float(data["format"]["duration"])
    except (FileNotFoundError, KeyError, IndexError, ValueError, subprocess.SubprocessError):
        return None


def run(slug, require_pass=False):
    ep = ROOT / "content" / "episodes" / slug
    if not ep.is_dir():
        print(f"No episode at {ep}", file=sys.stderr)
        return 2

    r = Result()
    evidence = load_json(ep / "evidence.json")
    licenses = load_json(ep / "licenses.json")
    packaging = load_json(ep / "packaging.json")
    script_path = ep / "script.md"
    script = script_path.read_text() if script_path.exists() else ""

    print(f"\nGate — {slug}\n")

    # C1 — original research artifact
    art = (evidence or {}).get("artifact") or {}
    art_path = ep / art.get("path", "") if art.get("path") else None
    r.add("C1", bool(art.get("kind")) and art_path is not None and art_path.exists(),
          f"original research artifact: {art.get('kind') or 'MISSING'}"
          + ("" if art_path and art_path.exists() else " — file not on disk"))

    # C2 — two sources per claim, >=1 primary
    claims = (evidence or {}).get("claims") or []
    bad_claims = []
    for c in claims:
        srcs = c.get("sources") or []
        primary = [s for s in srcs if s.get("kind") == "primary"]
        if len(srcs) < LIMITS["sources_per_claim"] or len(primary) < LIMITS["primary_sources_required"]:
            bad_claims.append(c.get("id", "?"))
    r.add("C2", bool(claims) and not bad_claims,
          f"{len(claims)} claims sourced" if claims and not bad_claims
          else f"under-sourced claims: {bad_claims or 'no claims at all'}")

    # C3 — citation chip on every price scene
    plan = load_json(ep / "scene_plan.json") or {}
    scenes = plan.get("scenes", [])
    price_scenes = [s for s in scenes if s.get("shows_price")]
    uncited = [s.get("id", "?") for s in price_scenes if not s.get("citation")]
    r.add("C3", bool(scenes) and not uncited,
          f"{len(price_scenes)} price scenes all cited" if scenes and not uncited
          else f"uncited price scenes: {uncited or 'no scene plan'}")

    # C4 — asset licenses
    asset_dir = ep / "assets"
    files = {p.name for p in asset_dir.iterdir() if p.is_file()} if asset_dir.is_dir() else set()
    entries = {pathlib.Path(e.get("file", "")).name: e for e in (licenses or [])}
    unlicensed = sorted(files - set(entries))
    bad_lic = [n for n, e in entries.items()
               if (e.get("license", "").lower() not in LIMITS["allowed_licenses"])]
    r.add("C4", bool(files) and not unlicensed and not bad_lic,
          f"{len(files)} assets licensed" if files and not unlicensed and not bad_lic
          else f"unlicensed: {unlicensed} / disallowed: {bad_lic}")

    # C5 — AI disclosure, unconditional
    r.add("C5", bool((packaging or {}).get("ai_disclosure") is True),
          "ai_disclosure: true" if (packaging or {}).get("ai_disclosure") is True
          else "ai_disclosure not set — required on every upload")

    # C6 — throughput cap. The log is written by scripts/log_publish.py as the last
    # step of every upload (see handoffs/upload-episode.md). Retracted rows don't
    # occupy a cap slot: a video unlisted under the corrections policy frees its
    # slot so the corrected re-render can ship the same day.
    log = load_json(ROOT / "content" / "publish_log.json") or []
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=24)
    recent = 0
    for row in log:
        if row.get("retracted"):
            continue
        try:
            if dt.datetime.fromisoformat(row["published_at"].replace("Z", "+00:00")) > cutoff:
                recent += 1
        except (KeyError, ValueError):
            continue
    r.add("C6", recent < LIMITS["hard_cap_per_day"],
          f"{recent} published in trailing 24h (cap {LIMITS['hard_cap_per_day']})")

    # C7 — template similarity against the last 10 scripts
    peers = sorted(
        (p for p in (ROOT / "content" / "episodes").glob("*/script.md") if p.parent.name != slug),
        key=lambda p: p.stat().st_mtime, reverse=True)[:10]
    worst, worst_slug = 0.0, None
    if script:
        sig = sentence_signature(script)
        for p in peers:
            s = similarity(sig, sentence_signature(p.read_text()))
            if s > worst:
                worst, worst_slug = s, p.parent.name
    r.add("C7", bool(script) and worst <= LIMITS["template_similarity_max"],
          f"max structural similarity {worst:.0%}"
          + (f" vs {worst_slug}" if worst_slug else " (no peers yet)")
          + ("" if script else " — no script found"))

    # C8 — editorial bounds
    hits = [label for pat, label in BANNED_PATTERNS if re.search(pat, script, re.I)]
    r.add("C8", not hits, "editorial bounds clean" if not hits else f"detected: {hits}")

    # C9 — delivery QC
    video = ROOT / "out" / f"{slug}.mp4"
    info = probe(video) if video.exists() else None
    if info:
        w, h, dur = info
        lo, hi = LIMITS["duration"]
        okc = (w, h) == LIMITS["resolution"] and lo <= dur <= hi
        r.add("C9", okc, f"{w}x{h}, {dur:.1f}s")
    else:
        r.add("C9", False, "no render at out/%s.mp4 (or ffprobe unavailable)" % slug)

    # C10 — privacy
    r.add("C10", (packaging or {}).get("privacy_status") == "private",
          "privacy=private" if (packaging or {}).get("privacy_status") == "private"
          else "upload privacy must be 'private' — a human flips it public")

    blocking = [c["id"] for c in r.checks if c["result"] == "FAIL"]
    owners = {
        "C1": "trend-archaeologist", "C2": "trend-archaeologist", "C3": "motion-director",
        "C4": "archive-sourcer", "C5": "seo-packager", "C6": "strategy-lead",
        "C7": "script-editor", "C8": "script-editor", "C9": "post-supervisor",
        "C10": "seo-packager",
    }
    verdict = "PASS" if not blocking else "FAIL"
    out = {
        "slug": slug,
        "verdict": verdict,
        "evaluated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "checks": r.checks,
        "blocking": blocking,
        "owner_to_fix": {c: owners[c] for c in blocking},
    }
    (ep / "gate.json").write_text(json.dumps(out, indent=2) + "\n")

    print(f"\n  \033[1mVERDICT: {verdict}\033[0m")
    if blocking:
        print("  Route each failure to its owning agent:")
        for c in blocking:
            print(f"    {c} -> @{owners[c]}")
    print()

    if require_pass and verdict != "PASS":
        print("Publish blocked. Fix the failures above.\n", file=sys.stderr)
        return 1
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Price Archaeology publish gate")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--require-pass", action="store_true",
                    help="exit non-zero unless the verdict is PASS (used by make publish)")
    args = ap.parse_args()
    sys.exit(run(args.slug, args.require_pass))
