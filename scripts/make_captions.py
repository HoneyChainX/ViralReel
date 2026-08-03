#!/usr/bin/env python3
"""
Generate captions.json for an episode from script.md + scene_plan.json.

Most Shorts are watched muted, so burned captions are delivery spec (bible §5,
gate C9 policy). Without word-level timings from the TTS, chunks are allocated
proportionally by word count inside each beat's time window — beat boundaries
come from the scene plan, so captions stay in sync with the cuts even when the
read drifts a little inside a beat. Draft-grade by design; word-timed captions
arrive with the ElevenLabs voice (its API returns alignment).

Usage: python3 scripts/make_captions.py --slug four-k-tv [--max-words 7]
"""

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

BEATS = ["ARTIFACT", "GAP", "EXCAVATION", "VERDICT", "HANDOFF"]


def beat_text(script: str) -> dict:
    """Pull spoken text per beat out of script.md. Beat headers look like
    **[ARTIFACT 0:00-0:03]** or **[ARTIFACT]** — accept both."""
    out = {}
    pattern = re.compile(r"\*\*\[(%s)[^\]]*\]\*\*" % "|".join(BEATS))
    parts = pattern.split(script)
    # parts: [pre, BEAT, text, BEAT, text, ...]
    for i in range(1, len(parts) - 1, 2):
        beat, text = parts[i], parts[i + 1]
        # stop at the next section marker (--- or ## Source map)
        text = re.split(r"\n---|\n## ", text)[0]
        text = re.sub(r"\[(PAUSE|EMPHASIS)\]", " ", text)
        text = re.sub(r"[*_#>`]", "", text)
        text = " ".join(text.split())
        if text:
            out[beat] = text
    return out


def chunk(text: str, max_words: int):
    words = text.split()
    # prefer breaking at sentence ends when they land inside the window
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= max_words or w.rstrip('"”').endswith((".", "?", "!")):
            chunks.append(" ".join(cur))
            cur = []
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--max-words", type=int, default=7)
    args = ap.parse_args()

    ep = ROOT / "content" / "episodes" / args.slug
    script = (ep / "script.md").read_text()
    plan = json.loads((ep / "scene_plan.json").read_text())

    # beat windows from the actual scene plan (min in, max out per beat)
    windows = {}
    for s in plan["scenes"]:
        b = s.get("beat", "").upper()
        if b not in BEATS:
            continue
        lo, hi = windows.get(b, (s["in"], s["out"]))
        windows[b] = (min(lo, s["in"]), max(hi, s["out"]))

    texts = beat_text(script)
    missing = [b for b in texts if b not in windows]
    if missing:
        print(f"beats in script but not in scene plan: {missing}", file=sys.stderr)

    captions = []
    for beat, text in texts.items():
        if beat not in windows:
            continue
        lo, hi = windows[beat]
        chunks = chunk(text, args.max_words)
        total_words = sum(len(c.split()) for c in chunks) or 1
        t = lo
        span = hi - lo
        for c in chunks:
            frac = len(c.split()) / total_words
            end = min(hi, t + frac * span)
            captions.append({"text": c, "start": round(t, 2), "end": round(end, 2)})
            t = end

    (ep / "captions.json").write_text(json.dumps(captions, indent=2) + "\n")
    print(f"{len(captions)} caption chunks -> {ep / 'captions.json'}")


if __name__ == "__main__":
    main()
