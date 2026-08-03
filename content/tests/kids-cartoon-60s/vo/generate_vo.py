#!/usr/bin/env python3
"""Kokoro VO for the kids-cartoon test — one wav per narration line + a timing manifest.

Voice-director notes: storybook read, warm female voice (af_heart), default pace.
Kokoro is the platform's CPU-viable free TTS (config/platform.yaml, voice profile).
"""
import json
import pathlib

import soundfile as sf
from kokoro import KPipeline

OUT = pathlib.Path(__file__).parent
LINES = [
    ("l1", "Once upon a time, in a big sandy desert, there lived a little camel named Cami."),
    ("l2", "Cami loved to bounce. Boing! Boing! Boing!"),
    ("l3", "One sunny day, Cami found something amazing. The great, big, blue sea!"),
    ("l4", "Splash! Up popped a friendly fish named Finn."),
    ("l5", "Hello, said Finn. Let's play!"),
    ("l6", "They bounced a big beach ball, all afternoon long."),
    ("l7", "And as the sun went down, the two new best friends danced by the sea."),
    ("l8", "The end. See you next time, little star!"),
]

pipeline = KPipeline(lang_code="a")  # American English
manifest = []
for key, text in LINES:
    chunks = [audio for (_, _, audio) in pipeline(text, voice="af_heart")]
    import numpy as np
    audio = np.concatenate(chunks) if len(chunks) > 1 else chunks[0]
    path = OUT / f"{key}.wav"
    sf.write(str(path), audio, 24000)
    dur = round(len(audio) / 24000, 2)
    manifest.append({"key": key, "text": text, "file": path.name, "duration_s": dur})
    print(f"{key}: {dur:>5}s  {text[:50]}")

(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
print("VO_DONE")
