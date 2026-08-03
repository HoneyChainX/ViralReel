#!/usr/bin/env python3
"""Seamless chaining — make N short clips play as ONE continuous shot.

The long-video fix (docs/12 § Seamless chaining): generative engines produce short
segments (Wan ~5s, LTX ~10s). A chain manifest declares segments whose boundary frames
obey the handoff contract:

    the LAST frame of segment N is EXACTLY the FIRST frame of segment N+1

For deterministic renders (Remotion/Blender) that's achieved by overlapping the frame
ranges by one frame. For generative segments it's achieved by conditioning segment N+1
on segment N's last frame (I2V init / Wan FLF2V). Either way this tool is the mechanical
enforcement: it verifies every join (SSIM), drops the duplicated overlap frames, stitches
without any transition, and proves seamlessness (no detectable cut at any join).

  seamless.py handoff <video.mp4> <out.png>     extract the exact last frame (next init)
  seamless.py verify  <chain.yaml>              SSIM every join against the contract
  seamless.py stitch  <chain.yaml>              verify -> dedupe overlaps -> one video + QC

Chains produce PICTURE ONLY (audio is dropped): sound belongs to the continuous shot as
a whole — VO/bed laid over it at the film level — not to the segment seams, where butt
joins click. Deliberate, documented, owned by sound-designer/film-editor.

Chain manifest (studio/film/<slug>.chain.yaml):
  chain:
    slug: my-long-shot
    delivery: {width: 1080, height: 1920, fps: 30}
    handoff:  {mode: exact, overlap_frames: 1, ssim_min: 0.97}
  segments:
    - {id: seg1, source: out/chain/seg1.mp4}
    - {id: seg2, source: out/chain/seg2.mp4}
"""
from __future__ import annotations

import json
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
SCENEDETECT = ROOT / "vendor" / "pyscenedetect" / ".venv" / "bin" / "scenedetect"


def sh(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True)


def duration_of(path: Path) -> float:
    out = sh([FFPROBE, "-v", "error", "-show_entries", "format=duration",
              "-of", "csv=p=0", str(path)])
    return float(out.stdout.strip() or 0)


def frames_of(path: Path) -> int:
    """Exact video frame count. Container duration lies (edit lists, padding — Remotion's
    mp4s report ~1.5% high); packets don't."""
    out = sh([FFPROBE, "-v", "error", "-select_streams", "v:0", "-count_packets",
              "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(path)])
    digits = re.sub(r"\D", "", out.stdout)
    return int(digits or 0)


def extract_last_frame(video: Path, out_png: Path) -> None:
    sh([FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
        "-sseof", "-0.2", "-i", str(video), "-update", "1", "-q:v", "1", str(out_png)])


def extract_first_frame(video: Path, out_png: Path) -> None:
    sh([FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(video), "-frames:v", "1", "-q:v", "1", str(out_png)])


def ssim(a: Path, b: Path) -> float:
    out = sh([FFMPEG, "-hide_banner", "-i", str(a), "-i", str(b),
              "-lavfi", "ssim", "-f", "null", "-"])
    m = re.search(r"All:([\d.]+)", out.stderr)
    return float(m.group(1)) if m else 0.0


def load_chain(path: Path) -> dict:
    data = yaml.safe_load(path.read_text())
    chain, segments = data.get("chain", {}), data.get("segments", [])
    problems = []
    if len(segments) < 2:
        problems.append("a chain needs >= 2 segments")
    for s in segments:
        if not (ROOT / s.get("source", "∅")).exists():
            problems.append(f"{s.get('id')}: missing {s.get('source')}")
    for key in ("width", "height", "fps"):
        if key not in chain.get("delivery", {}):
            problems.append(f"chain.delivery.{key} missing")
    if problems:
        for p in problems:
            print(f"chain error: {p}", file=sys.stderr)
        sys.exit(1)
    chain.setdefault("handoff", {})
    chain["handoff"].setdefault("mode", "exact")
    chain["handoff"].setdefault("overlap_frames", 1)
    chain["handoff"].setdefault("ssim_min", 0.97)
    return data


def verify(data: dict, quiet: bool = False) -> list[dict]:
    segs = data["segments"]
    ssim_min = data["chain"]["handoff"]["ssim_min"]
    joins = []
    with tempfile.TemporaryDirectory(prefix="seamless-verify-") as td:
        td = Path(td)
        for i in range(len(segs) - 1):
            a, b = ROOT / segs[i]["source"], ROOT / segs[i + 1]["source"]
            last_a, first_b = td / f"a{i}.png", td / f"b{i}.png"
            extract_last_frame(a, last_a)
            extract_first_frame(b, first_b)
            score = ssim(last_a, first_b)
            ok = score >= ssim_min
            joins.append({"join": f"{segs[i]['id']}→{segs[i+1]['id']}",
                          "ssim": round(score, 4), "ok": ok})
            if not quiet:
                print(f"{'✓' if ok else '✗'} {joins[-1]['join']:<24} SSIM {score:.4f} "
                      f"(contract ≥ {ssim_min})")
    return joins


def stitch(data: dict, chain_path: Path) -> int:
    chain = data["chain"]
    segs = data["segments"]
    d = chain["delivery"]
    overlap = int(chain["handoff"]["overlap_frames"])
    slug = chain.get("slug", chain_path.stem.replace(".chain", ""))
    out_final = ROOT / "out" / f"{slug}.mp4"

    joins = verify(data, quiet=False)
    if not all(j["ok"] for j in joins):
        print("\n✗ handoff contract broken — fix the segments (regenerate the offending "
              "boundary), do not lower ssim_min to pass.")
        return 1

    # Dedupe overlaps and stitch. Segment 1 keeps all frames; segments 2..N drop their
    # first `overlap` frames (they duplicate the previous segment's tail by contract).
    tmp = Path(tempfile.mkdtemp(prefix=f"seamless-{slug}-"))
    parts = []
    for i, s in enumerate(segs):
        src = ROOT / s["source"]
        dst = tmp / f"{i:03d}.mp4"
        vf = f"fps={d['fps']},format=yuv420p,setsar=1"
        if i > 0 and overlap:
            vf = f"select='gte(n\\,{overlap})',setpts=N/({d['fps']}*TB)," + vf
        rc = subprocess.run(
            [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", str(src),
             "-vf", vf, "-an",
             "-c:v", "libx264", "-crf", "16", "-preset", "fast", str(dst)]).returncode
        if rc != 0:
            print(f"✗ segment prep failed: {s['id']}")
            return 1
        parts.append(dst)
    concat_list = tmp / "list.txt"
    concat_list.write_text("".join(f"file '{p}'\n" for p in parts))
    rc = subprocess.run(
        [FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
         "-f", "concat", "-safe", "0", "-i", str(concat_list),
         "-c:v", "libx264", "-profile:v", "high", "-crf", "18", "-preset", "medium",
         "-movflags", "+faststart", str(out_final)]).returncode
    if rc != 0:
        print("✗ concat failed")
        return 1

    # QC 1 — duration arithmetic, in frames (container durations lie; packets don't).
    total_frames = frames_of(out_final)
    expected_frames = sum(frames_of(ROOT / s["source"]) for s in segs) \
        - (len(segs) - 1) * overlap
    total = total_frames / d["fps"]
    expected = expected_frames / d["fps"]
    ok_dur = total_frames == expected_frames

    # QC 2 — INVERTED cut check: seamless means NO detectable boundary at any join.
    seam_check = None
    if SCENEDETECT.exists():
        join_times, acc = [], 0
        for s in segs[:-1]:
            acc += frames_of(ROOT / s["source"]) - overlap
            join_times.append(round(acc / d["fps"], 2))
        out = sh([str(SCENEDETECT), "-i", str(out_final), "detect-content",
                  "list-scenes", "-n"]).stdout
        detected = [int(h) * 3600 + int(mn) * 60 + float(sec)
                    for h, mn, sec in re.findall(
                        r"\|\s*\d+\s*\|\s*\d+\s*\|\s*(\d+):(\d+):([\d.]+)\s*\|", out)]
        leaks = [jt for jt in join_times
                 if any(abs(jt - dt) < 0.4 for dt in detected if dt > 0.01)]
        seam_check = {"join_times": join_times, "visible_seams": leaks, "ok": not leaks}

    report = {
        "chain": slug, "output": str(out_final.relative_to(ROOT)),
        "segments": [s["id"] for s in segs],
        "handoff": chain["handoff"],
        "joins": joins,
        "duration_s": round(total, 3), "expected_s": round(expected, 3),
        "duration_ok": ok_dur,
        "seam_check": seam_check,
        "note": "picture only by design — audio is laid over the continuous shot at film level",
    }
    chain_path.with_suffix(".report.json").write_text(json.dumps(report, indent=2))
    print(f"\n── QC: {json.dumps(report, indent=2)}")
    if not ok_dur or (seam_check and not seam_check["ok"]):
        print("✗ seamless QC failed — see report")
        return 1
    print(f"✓ seamless chain complete → {out_final.relative_to(ROOT)}")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == "handoff":
        extract_last_frame(Path(args[1]), Path(args[2]))
        print(f"last frame → {args[2]}")
        return 0
    if len(args) == 2 and args[0] in ("verify", "stitch"):
        chain_path = Path(args[1]).resolve()
        data = load_chain(chain_path)
        if args[0] == "verify":
            joins = verify(data)
            return 0 if all(j["ok"] for j in joins) else 1
        return stitch(data, chain_path)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
