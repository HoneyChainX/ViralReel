#!/usr/bin/env python3
"""Style gate — the mechanical half of taste. Checks copy against studio/rubrics/style-rules.yaml.

Usage:
  style_gate.py check <file.md> [file2 ...]   exit 1 on any violation, listing each
  style_gate.py --selftest                    prove the checker catches seeded violations

This is a CREATIVE quality tool, not the compliance gate (scripts/gate.py) — it guards
against synthetic-sounding copy and generic direction language before a human reads it.
It advises the creative department; it cannot veto anything. Rules live in the rubric
file so taste changes are diffs, not code edits.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / "studio" / "rubrics" / "style-rules.yaml"


def load_rules() -> dict:
    return yaml.safe_load(RULES.read_text())


def check_text(text: str, rules: dict, name: str = "<text>") -> list[str]:
    violations = []
    low = text.lower()
    for phrase in rules.get("banned_phrases", []):
        if phrase.lower() in low:
            violations.append(f"{name}: banned phrase — “{phrase}”")
    for trope in rules.get("banned_visual_tropes", []):
        if trope.lower() in low:
            violations.append(f"{name}: banned visual trope — “{trope}”")

    limits = rules.get("limits", {})
    words = re.findall(r"[A-Za-z’']+", text)
    n_words = max(1, len(words))
    bangs = text.count("!")
    max_bangs = limits.get("max_exclamations_per_100_words")
    if max_bangs is not None and bangs / (n_words / 100) > max_bangs:
        violations.append(f"{name}: {bangs} exclamation marks in {n_words} words "
                          f"(limit {max_bangs}/100 words)")
    caps = [w for w in words if len(w) > 2 and w.isupper()]
    max_caps = limits.get("max_all_caps_words")
    if max_caps is not None and len(caps) > max_caps:
        violations.append(f"{name}: {len(caps)} ALL-CAPS words {caps[:5]} (limit {max_caps})")
    max_sent = limits.get("max_sentence_words")
    if max_sent:
        for s in re.split(r"[.!?]+\s", text):
            sw = len(re.findall(r"[A-Za-z’']+", s))
            if sw > max_sent:
                violations.append(f"{name}: {sw}-word sentence (limit {max_sent}): "
                                  f"“{s.strip()[:60]}…”")
    return violations


def selftest() -> int:
    rules = load_rules()
    dirty = ("Let's delve into this epic drone shot!!! A GAME CHANGER TAPESTRY of "
             "content that will elevate your feed, " + "and " * 40 + "then some.")
    clean = ("At dawn the camel's shadow stretches across cooling sand. "
             "The price on the tag reads four dollars. That number is the story.")
    dirty_v = check_text(dirty, rules, "dirty-fixture")
    clean_v = check_text(clean, rules, "clean-fixture")
    ok = len(dirty_v) >= 4 and clean_v == []
    print(f"style_gate selftest: {'OK' if ok else 'FAIL'} — "
          f"dirty fixture: {len(dirty_v)} violations caught, clean fixture: {len(clean_v)}")
    if not ok:
        for v in dirty_v + clean_v:
            print("  ", v)
    return 0 if ok else 1


def main() -> int:
    args = sys.argv[1:]
    if "--selftest" in args:
        return selftest()
    if args and args[0] == "check" and len(args) > 1:
        rules = load_rules()
        all_v = []
        for path in args[1:]:
            p = Path(path)
            if not p.exists():
                all_v.append(f"{path}: file not found")
                continue
            all_v += check_text(p.read_text(), rules, p.name)
        if all_v:
            print(f"✗ {len(all_v)} style violation(s):")
            for v in all_v:
                print("  ", v)
            return 1
        print("✓ style clean")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
