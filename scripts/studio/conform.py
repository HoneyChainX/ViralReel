#!/usr/bin/env python3
"""Conform — link independently produced scene-videos into one complete film.

The assembly contract (docs/12-film-assembly.md): every scene is produced by whatever
lane suits it — sourced footage, Remotion animation, generative engines on a GPU host —
and lands as an ordinary video file. A film manifest (studio/film/<slug>.yaml) declares
the order, trims, and transitions. This tool does the editorial mechanics:

  conform.py validate <film.yaml>   every scene exists; probe specs vs the delivery spec
  conform.py timeline <film.yaml>   emit an OpenTimelineIO .otio (interchange artifact)
  conform.py render   <film.yaml>   normalize scenes -> stitch -> loudness -> QC report

Design choices, stated plainly:
  * The spine is the manifest + ffmpeg, with OTIO as the interchange artifact — not the
    render path. A YAML file a human can read and an agent can edit beats a binary NLE
    project as the source of truth at this studio's scale.
  * Scenes are normalized to the delivery spec BEFORE stitching (fit: crop|pad, fps,
    48k stereo audio — silence synthesized when a scene has none), so heterogeneous
    lanes always conform.
  * A `cut` is a 1-frame xfade in the stitch graph — one uniform graph instead of two
    code paths; invisible at 30fps and documented here rather than hidden.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FFDIR = ROOT / "vendor" / "ffbin" / "bin"
FFMPEG = str(FFDIR / "ffmpeg") if (FFDIR / "ffmpeg").exists() else "ffmpeg"
FFPROBE = str(FFDIR / "ffprobe") if (FFDIR / "ffprobe").exists() else "ffprobe"
OTIO_PY = ROOT / "vendor" / "otio" / ".venv" / "bin" / "python"

CUT_DUR = 1 / 30  # a cut is a one-frame xfade — one uniform stitch graph


def load_film(path: Path) -> dict:
    film = yaml.safe_load(path.read_text())
    problems = []
    d = film.get("delivery", {})
    for key in ("width", "height", "fps"):
        if key not in d:
            problems.append(f"delivery.{key} missing")
    scenes = film.get("scenes", [])
    if len(scenes) < 1:
        problems.append("no scenes")
    seen = set()
    for s in scenes:
        sid = s.get("id", "<missing>")
        if sid in seen:
            problems.append(f"duplicate scene id {sid}")
        seen.add(sid)
        if "source" not in s:
            problems.append(f"{sid}: source missing")
        tr = s.get("transition_out", {"type": "cut"})
        if tr.get("type") not in ("cut", "xfade"):
            problems.append(f"{sid}: transition_out.type must be cut|xfade")
    if problems:
        for p in problems:
            print(f"manifest error: {p}", file=sys.stderr)
        sys.exit(1)
    return film


def probe(path: Path) -> dict:
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries",
         "format=duration:stream=codec_type,width,height,avg_frame_rate",
         "-of", "json", str(path)],
        capture_output=True, text=True)
    if out.returncode != 0:
        return {}
    data = json.loads(out.stdout)
    info = {"duration": float(data.get("format", {}).get("duration", 0) or 0),
            "has_audio": False, "width": None, "height": None}
    for st in data.get("streams", []):
        if st.get("codec_type") == "video" and info["width"] is None:
            info["width"], info["height"] = st.get("width"), st.get("height")
        if st.get("codec_type") == "audio":
            info["has_audio"] = True
    return info


def scene_window(scene: dict, src_info: dict) -> tuple[float, float]:
    t_in = float(scene.get("in", 0.0))
    t_out = float(scene.get("out", src_info["duration"]))
    return t_in, max(0.0, t_out - t_in)


# ── validate ────────────────────────────────────────────────────────────────

def validate(film: dict, film_path: Path, quiet: bool = False) -> list[dict]:
    d = film["delivery"]
    rows, missing = [], 0
    for s in film["scenes"]:
        src = ROOT / s["source"]
        if not src.exists():
            rows.append({"id": s["id"], "ok": False, "why": f"missing file {s['source']}"})
            missing += 1
            continue
        info = probe(src)
        _, dur = scene_window(s, info)
        note = []
        if (info["width"], info["height"]) != (d["width"], d["height"]):
            note.append(f"{info['width']}x{info['height']}→conform")
        if not info["has_audio"]:
            note.append("no audio→silence")
        rows.append({"id": s["id"], "ok": True, "dur": round(dur, 2),
                     "why": ", ".join(note) or "spec-clean"})
    if not quiet:
        for r in rows:
            mark = "✓" if r["ok"] else "✗"
            print(f"{mark} {r['id']:<12} {r.get('dur', '—'):>7}  {r['why']}")
    if missing:
        print(f"\n{missing} scene(s) missing — produce them first; conform links, it does not create.")
        sys.exit(1)
    return rows


# ── timeline (OTIO interchange) ─────────────────────────────────────────────

def timeline(film: dict, film_path: Path) -> int:
    if not OTIO_PY.exists():
        print("OTIO venv not installed (vendor/otio) — timeline skipped; render does not need it.")
        return 0
    scenes = []
    for s in film["scenes"]:
        info = probe(ROOT / s["source"])
        t_in, dur = scene_window(s, info)
        scenes.append({"id": s["id"], "source": str(ROOT / s["source"]),
                       "in": t_in, "dur": dur})
    fps = film["delivery"]["fps"]
    out_path = film_path.with_suffix(".otio")
    script = f"""
import opentimelineio as otio
data = {scenes!r}
fps = {fps}
tl = otio.schema.Timeline(name={film.get('title', 'film')!r})
track = otio.schema.Track(name="V1")
tl.tracks.append(track)
for s in data:
    clip = otio.schema.Clip(
        name=s["id"],
        media_reference=otio.schema.ExternalReference(target_url=s["source"]),
        source_range=otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(round(s["in"] * fps), fps),
            duration=otio.opentime.RationalTime(round(s["dur"] * fps), fps)))
    track.append(clip)
otio.adapters.write_to_file(tl, {str(out_path)!r})
print("wrote", {str(out_path)!r})
"""
    return subprocess.run([str(OTIO_PY), "-c", script]).returncode


# ── render ──────────────────────────────────────────────────────────────────

def render(film: dict, film_path: Path) -> int:
    d = film["delivery"]
    W, H, FPS = d["width"], d["height"], d["fps"]
    fit = d.get("fit", "crop")
    lufs = d.get("lufs", -14)
    slug = film.get("slug", film_path.stem)
    out_final = ROOT / "out" / f"{slug}.mp4"
    out_final.parent.mkdir(exist_ok=True)

    validate(film, film_path, quiet=True)

    if fit == "pad":
        vfit = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2")
    else:
        vfit = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"

    tmp = Path(tempfile.mkdtemp(prefix=f"conform-{slug}-"))
    norm, durs = [], []
    print(f"── normalize {len(film['scenes'])} scene(s) → {tmp}")
    for s in film["scenes"]:
        src = ROOT / s["source"]
        info = probe(src)
        t_in, dur = scene_window(s, info)
        dst = tmp / f"{s['id']}.mp4"
        cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
               "-ss", str(t_in), "-t", str(dur), "-i", str(src)]
        if not info["has_audio"]:
            cmd += ["-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo"]
        cmd += ["-filter_complex",
                f"[0:v]{vfit},fps={FPS},format=yuv420p,setsar=1[v];"
                + ("[0:a]" if info["has_audio"] else "[1:a]")
                + "aresample=48000,aformat=channel_layouts=stereo[a]",
                "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-crf", "16", "-preset", "fast",
                "-c:a", "aac", "-b:a", "192k", str(dst)]
        if subprocess.run(cmd).returncode != 0:
            print(f"✗ normalize failed: {s['id']}")
            return 1
        real = probe(dst)["duration"]
        norm.append((s, dst))
        durs.append(real)
        print(f"✓ {s['id']:<12} {real:6.2f}s")

    # Stitch: uniform xfade/acrossfade chain (cut = 1-frame fade).
    n = len(norm)
    if n == 1:
        stitched = norm[0][1]
    else:
        inputs, fc = [], []
        for _, p in norm:
            inputs += ["-i", str(p)]
        offset = 0.0
        for i in range(n - 1):
            tr = norm[i][0].get("transition_out", {"type": "cut"})
            tdur = float(tr.get("dur", 0.5)) if tr.get("type") == "xfade" else CUT_DUR
            offset += durs[i] - tdur
            vin = "[0:v]" if i == 0 else f"[vx{i}]"
            ain = "[0:a]" if i == 0 else f"[ax{i}]"
            fc.append(f"{vin}[{i+1}:v]xfade=transition=fade:duration={tdur:.4f}:offset={offset:.4f}[vx{i+1}]")
            fc.append(f"{ain}[{i+1}:a]acrossfade=d={max(tdur, 0.02):.4f}[ax{i+1}]")
        fc.append(f"[vx{n-1}]format=yuv420p[vout]")
        fc.append(f"[ax{n-1}]loudnorm=I={lufs}:TP=-1:LRA=11[aout]")
        stitched = tmp / "stitched.mp4"
        cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", *inputs,
               "-filter_complex", ";".join(fc),
               "-map", "[vout]", "-map", "[aout]",
               "-c:v", "libx264", "-profile:v", "high", "-crf", "18", "-preset", "medium",
               "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(stitched)]
        print("── stitch")
        if subprocess.run(cmd).returncode != 0:
            print("✗ stitch failed")
            return 1
    subprocess.run(["cp", str(stitched), str(out_final)])

    # QC — measure, never assume.
    info = probe(out_final)
    expected = sum(durs) - sum(
        (float(s.get("transition_out", {}).get("dur", 0.5))
         if s.get("transition_out", {}).get("type") == "xfade" else CUT_DUR)
        for s, _ in norm[:-1])
    ok_dur = abs(info["duration"] - expected) < 0.5
    ebur = subprocess.run(
        [FFMPEG, "-hide_banner", "-i", str(out_final), "-af", "ebur128", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    # ebur128 logs running values per frame; only the LAST "I:" line is the
    # integrated summary — reading the first reports the silence of frame one.
    matches = re.findall(r"I:\s*(-?[\d.]+) LUFS", ebur)
    measured_lufs = float(matches[-1]) if matches else None

    # Cut verification (PySceneDetect): every expected HARD cut in the manifest must
    # have a detected boundary within tolerance. Extra detected boundaries are fine —
    # scenes legitimately contain internal cuts. Xfade joins are not asserted (a
    # dissolve is not a hard boundary). Skipped gracefully when the tool is absent.
    cut_check: dict | None = None
    sd = ROOT / "vendor" / "pyscenedetect" / ".venv" / "bin" / "scenedetect"
    expected_cuts = []
    acc = 0.0
    for i in range(n - 1):
        tr = norm[i][0].get("transition_out", {"type": "cut"})
        tdur = float(tr.get("dur", 0.5)) if tr.get("type") == "xfade" else CUT_DUR
        acc += durs[i] - tdur
        if tr.get("type", "cut") == "cut":
            expected_cuts.append(round(acc, 2))
    if sd.exists():
        out = subprocess.run([str(sd), "-i", str(out_final), "detect-content", "list-scenes", "-n"],
                             capture_output=True, text=True).stdout
        # Table rows: | Scene # | Start Frame | HH:MM:SS.mmm | End Frame | HH:MM:SS.mmm |
        detected = [
            int(h) * 3600 + int(mn) * 60 + float(sec)
            for h, mn, sec in re.findall(
                r"\|\s*\d+\s*\|\s*\d+\s*\|\s*(\d+):(\d+):([\d.]+)\s*\|", out)
        ]
        misses = [c for c in expected_cuts
                  if not any(abs(c - dt) < 0.5 for dt in detected)]
        cut_check = {"expected_hard_cuts": expected_cuts,
                     "detected_boundaries": len(detected),
                     "missed": misses, "ok": not misses}
    report = {
        "film": slug, "output": str(out_final.relative_to(ROOT)),
        "scenes": [s["id"] for s, _ in norm],
        "duration_s": round(info["duration"], 3), "expected_s": round(expected, 3),
        "duration_ok": ok_dur,
        "delivery": f"{info['width']}x{info['height']}@{FPS}",
        "delivery_ok": (info["width"], info["height"]) == (W, H),
        "integrated_lufs": measured_lufs,
        "cut_check": cut_check,
    }
    report_path = film_path.with_suffix(".report.json")
    report_path.write_text(json.dumps(report, indent=2))
    print(f"\n── QC: {json.dumps(report, indent=2)}")
    if cut_check and not cut_check["ok"]:
        print("✗ QC failed — expected hard cut(s) not found at", cut_check["missed"])
        return 1
    if not (ok_dur and report["delivery_ok"]):
        print("✗ QC failed — output kept for inspection, report says why")
        return 1
    print(f"✓ conform complete → {out_final.relative_to(ROOT)}")
    return 0


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in ("validate", "timeline", "render"):
        print(__doc__)
        return 2
    film_path = Path(sys.argv[2]).resolve()
    film = load_film(film_path)
    if sys.argv[1] == "validate":
        validate(film, film_path)
        return 0
    if sys.argv[1] == "timeline":
        return timeline(film, film_path)
    return render(film, film_path)


if __name__ == "__main__":
    sys.exit(main())
