import json, pathlib
import numpy as np, soundfile as sf
from kokoro import KPipeline
OUT = pathlib.Path(__file__).parent
LINES = [
    ("l1",  1.5, "Every evening, the sea asks the same question."),
    ("l2",  7.0, "I put on the coat. I bank the stove. I answer."),
    ("l3", 14.0, "My father rowed this water. His father cut these steps."),
    ("l4", 23.5, "The crossing is short. It only feels like a life."),
    ("l5", 29.5, "Halfway out, the sun lets go of the day."),
    ("l6", 35.0, "And the water holds the last of it, the way I hold his name."),
    ("l7", 44.5, "The tower waits. It has never once waited badly."),
    ("l8", 50.0, "One match. One wick. One turn of the little wheel."),
    ("l9", 55.0, "And the light goes out across the water — so nobody else has to ask."),
]
p = KPipeline(lang_code="b")
man = []
for k, at, text in LINES:
    chunks = [a for (_, _, a) in p(text, voice="bm_george", speed=0.9)]
    a = np.concatenate(chunks) if len(chunks) > 1 else chunks[0]
    sf.write(str(OUT / f"{k}.wav"), a, 24000)
    man.append({"key": k, "at_s": at, "duration_s": round(len(a)/24000, 2), "text": text})
    print(k, at, round(len(a)/24000, 2))
(OUT / "manifest.json").write_text(json.dumps(man, indent=2))
print("VO_DONE")
