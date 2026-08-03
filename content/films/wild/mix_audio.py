#!/usr/bin/env python3
"""WILD audio mix — score + chapter ambience + narration → 180s M4A at -14 LUFS.

Sound map (sound-designer doctrine: contrast, chosen silences, VO wins):
  music    Gymnopédie No.1 (PD) carries 0–166s, crossfades into No.3 for the credits tail
  ambience one bed per 30s chapter, 2.5s fades, low under the score
  VO       12 lines (Kokoro bm_george) at the times in vo/manifest.json
"""
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parents[2]
FF = str(ROOT / "vendor" / "ffbin" / "bin" / "ffmpeg")
A = HERE / "audio"
VO = HERE / "vo"

vo_lines = json.loads((VO / "manifest.json").read_text())

inputs: list[str] = []
def add(path: str, *pre: str) -> int:
    inputs.extend([*pre, "-i", path])
    return (len([x for x in inputs if x == "-i"]) - 1)

g1 = add(str(A / "Satie_Gymnopedie_No_1_performed_by_Michael_Laucke.flac"))
g3 = add(str(A / "Satie_Gymnopedie_No_3_performed_by_Michael_Laucke.flac"))
birds = add(str(A / "Birds_singing_in_garden.ogg"))
forest = add(str(A / "Forest_ambience_%28Gravity_Sound%29.wav"))
pond = add(str(A / "Nature_sounds_ambience_in_a_Dordogne_pond.ogg"))
wind = add(str(A / "Wind_in_forest_%28Gravity_Sound%29.wav"))
waves = add(str(ROOT / "content/tests/desert-sea-15s/assets/Ocean_waves_at_L%C3%A6kjavik_beach%2C_Iceland.webm"), "-stream_loop", "4")

fc: list[str] = []
mix_ins: list[str] = []

# Score: No.1 fades out 162→166; No.3 enters at 160 for the tail — amix overlap = crossfade.
fc.append(f"[{g1}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:166,"
          f"afade=t=in:st=0:d=3,afade=t=out:st=162:d=4,volume=0.45[mus1]")
fc.append(f"[{g3}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:20,"
          f"afade=t=in:st=0:d=4,afade=t=out:st=17:d=3,adelay=160000:all=1,volume=0.4[mus2]")
mix_ins += ["[mus1]", "[mus2]"]

# Ambience: (input, source-offset, chapter-start, label)
amb = [(birds, 8, 0, "a1"), (forest, 0, 30, "a2"), (pond, 0, 60, "a3"),
       (wind, 6, 90, "a4"), (waves, 0, 120, "a5"), (pond, 25, 150, "a6")]
for idx, (inp, off, at, lab) in enumerate(amb):
    fc.append(f"[{inp}:a]aresample=48000,aformat=channel_layouts=stereo,"
              f"atrim={off}:{off+30},asetpts=PTS-STARTPTS,"
              f"afade=t=in:st=0:d=2.5,afade=t=out:st=27.5:d=2.5,"
              f"adelay={at*1000}:all=1,volume=0.28[{lab}]")
    mix_ins.append(f"[{lab}]")

# VO lines.
for i, line in enumerate(vo_lines):
    v = add(str(VO / f"{line['key']}.wav"))
    fc.append(f"[{v}:a]aresample=48000,aformat=channel_layouts=stereo,"
              f"adelay={int(line['at_s']*1000)}:all=1[v{i}]")
    mix_ins.append(f"[v{i}]")

fc.append(f"{''.join(mix_ins)}amix=inputs={len(mix_ins)}:normalize=0,"
          f"loudnorm=I=-14:TP=-1:LRA=13,atrim=0:180,afade=t=out:st=177.5:d=2.5[aout]")

cmd = [FF, "-hide_banner", "-loglevel", "error", "-y", *inputs,
       "-filter_complex", ";".join(fc), "-map", "[aout]",
       "-c:a", "aac", "-b:a", "192k", str(HERE / "wild-audio-180.m4a")]
print("inputs:", len(mix_ins), "streams")
rc = subprocess.run(cmd).returncode
print("MIX_OK" if rc == 0 else f"MIX FAILED rc={rc}")
raise SystemExit(rc)
