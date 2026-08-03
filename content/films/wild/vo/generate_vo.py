#!/usr/bin/env python3
"""Kokoro VO for WILD — documentary narration, one wav per line + timing manifest.

voice-director notes: bm_george (British male) — measured, warm, Attenborough-adjacent
without imitating anyone. Slightly slower read suits the format.
"""
import json
import pathlib

import numpy as np
import soundfile as sf
from kokoro import KPipeline

OUT = pathlib.Path(__file__).parent
# (key, chapter, offset_s within film, text)
LINES = [
    ("c1a", 1,   8.0, "As dawn breaks over the savanna, the world wakes slowly, and light returns to the tall grass."),
    ("c1b", 1,  19.0, "The giants are already moving. For them, every day begins with a journey."),
    ("c2a", 2,  38.0, "In the old forest, sunlight falls in ribbons, and every shaft of light is a small stage."),
    ("c2b", 2,  49.0, "Here, the quiet ones make their living. Patient. Watchful. And rarely seen."),
    ("c3a", 3,  68.0, "All life follows the river. It carves the land, and the land leans close to drink."),
    ("c3b", 3,  79.0, "For the fish, the current is both home, and highway."),
    ("c4a", 4,  98.0, "Above the treeline the air thins, and only the boldest travellers remain."),
    ("c4b", 4, 109.0, "An eagle owns this silence. Her kingdom is measured in miles of empty sky."),
    ("c5a", 5, 128.0, "The ocean. The oldest wilderness of all. Beneath its surface, giants glide like slow music."),
    ("c5b", 5, 140.0, "A whale's breath hangs in the air. A flag, raised from another world."),
    ("c6a", 6, 158.0, "And when night falls, the wild does not sleep. It simply changes shifts."),
    ("c6b", 6, 168.0, "Ten thousand small lights carry on the day's unfinished business. The wild endures. And dawn... is never far away."),
]

pipeline = KPipeline(lang_code="b")  # British English for bm_ voices
manifest = []
for key, ch, at, text in LINES:
    chunks = [a for (_, _, a) in pipeline(text, voice="bm_george", speed=0.92)]
    audio = np.concatenate(chunks) if len(chunks) > 1 else chunks[0]
    sf.write(str(OUT / f"{key}.wav"), audio, 24000)
    dur = round(len(audio) / 24000, 2)
    manifest.append({"key": key, "chapter": ch, "at_s": at, "duration_s": dur, "text": text})
    print(f"{key} @{at:>6}s  {dur:>5}s  {text[:46]}")

(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
print("VO_DONE")
