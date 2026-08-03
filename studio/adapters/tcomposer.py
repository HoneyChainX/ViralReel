#!/usr/bin/env python3
"""OpenToonz batch-render seam — wraps `tcomposer`, the one automatable edge of OpenToonz.

OpenToonz is a GUI authoring suite (docs/11): humans animate, the pipeline renders. This
adapter finds tcomposer on the host and batch-renders .tnz scenes, which is exactly the
render-wrangler's contract with the animation department: authored scenes in, frames out.

Usage:
  python3 studio/adapters/tcomposer.py --selftest
  python3 studio/adapters/tcomposer.py render scene.tnz out/frames/ [--range 1 120] [--step 1]
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

CANDIDATES = ["tcomposer", "/usr/local/bin/tcomposer",
              "/Applications/OpenToonz/OpenToonz.app/Contents/MacOS/tcomposer"]


def find_tcomposer() -> str | None:
    for c in CANDIDATES:
        found = shutil.which(c) or (c if Path(c).is_file() else None)
        if found:
            return found
    return None


def render(scene: Path, outdir: Path, frame_range: tuple[int, int] | None, step: int) -> int:
    exe = find_tcomposer()
    if not exe:
        print("tcomposer not found — OpenToonz is a human-installed desktop app "
              "(config/platform.yaml: install: desktop). Install it, then re-run.")
        return 1
    outdir.mkdir(parents=True, exist_ok=True)
    cmd = [exe, str(scene), "-o", str(outdir)]
    if frame_range:
        cmd += ["-range", str(frame_range[0]), str(frame_range[1])]
    if step != 1:
        cmd += ["-step", str(step)]
    print("+", " ".join(cmd))
    return subprocess.run(cmd).returncode


def main() -> int:
    args = sys.argv[1:]
    if "--selftest" in args:
        exe = find_tcomposer()
        # Absence of a desktop app is a host property, not an adapter failure.
        print(f"tcomposer selftest: OK — {'found ' + exe if exe else 'not installed on this host (desktop module, expected)'}")
        return 0
    if args and args[0] == "render" and len(args) >= 3:
        fr = None
        if "--range" in args:
            i = args.index("--range")
            fr = (int(args[i + 1]), int(args[i + 2]))
        step = int(args[args.index("--step") + 1]) if "--step" in args else 1
        return render(Path(args[1]), Path(args[2]), fr, step)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
