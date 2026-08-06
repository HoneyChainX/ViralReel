#!/usr/bin/env python3
"""Host profile — what this machine actually is, and what it can actually run.

Every other layer asks this module instead of guessing: the bootstrap scripts
verify their work against it, the studio doctor reports it, and the remote
control server returns it as `studio_status` so the operator can see the state
of a machine they are not sitting in front of.

    python3 scripts/studio/hostinfo.py            # human-readable
    python3 scripts/studio/hostinfo.py --json     # machine-readable
    python3 scripts/studio/hostinfo.py --assert-ready   # exit 1 if unfit to render

Deliberately stdlib-only. This runs before anything is installed — including on
a fresh Windows 11 box where the only Python may be the one the bootstrap just
put there — so it cannot import yaml, psutil, or anything else from the tree.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# NOT stdlib `platform` — scripts/studio/platform.py is this file's neighbour and
# shadows it whenever a script in this directory is run directly. sys.platform
# and os.uname() carry everything we need and cannot be shadowed.
_SYSTEM = {"linux": "Linux", "win32": "Windows", "cygwin": "Windows",
           "darwin": "Darwin"}.get(sys.platform, sys.platform)


def _uname(field: str) -> str:
    try:
        return getattr(os.uname(), field)
    except Exception:
        return ""

# A render host that cannot hold the working set thrashes instead of rendering.
# 8 GB is the floor a 1080p Cycles chunk + a Remotion Chromium + ffmpeg fit in;
# below 40 GB free there is no room for a vendor tree (26 GB) plus renders.
MIN_RAM_GB = 8
MIN_FREE_GB_INSTALL = 40
MIN_FREE_GB_RENDER = 10


def _run(cmd: list[str], timeout: int = 10) -> str:
    """Best-effort command output. A missing tool is an answer, not an error."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (p.stdout or p.stderr or "").strip()
    except Exception:
        return ""


def _first_line(s: str) -> str:
    return s.splitlines()[0].strip() if s else ""


# ── platform ────────────────────────────────────────────────────────────────

def detect_wsl() -> dict:
    """WSL detection, in the order of decreasing trust.

    WSL_DISTRO_NAME is set by WSL itself; /proc/version carries the Microsoft
    kernel tag. Interop (being able to call .exe) is what actually matters to
    us, because that is how the Linux side reaches Windows power settings and
    the Windows side reaches our services.
    """
    info = {"is_wsl": False, "distro_name": None, "version": None, "interop": False}
    if os.environ.get("WSL_DISTRO_NAME"):
        info["is_wsl"] = True
        info["distro_name"] = os.environ["WSL_DISTRO_NAME"]
    try:
        pv = Path("/proc/version").read_text()
        if "microsoft" in pv.lower():
            info["is_wsl"] = True
            m = re.search(r"WSL(\d)", pv)
            if m:
                info["version"] = int(m.group(1))
    except Exception:
        pass
    if info["is_wsl"]:
        # WSL2 exposes the 9p-mounted Windows drives; WSL1 does too, so use the
        # kernel marker for the version and interop for capability.
        if info["version"] is None:
            info["version"] = 2 if Path("/run/WSL").exists() or Path("/usr/lib/wsl").exists() else 1
        info["interop"] = shutil.which("cmd.exe") is not None
    return info


def detect_os() -> dict:
    wsl = detect_wsl()
    return {
        "system": _SYSTEM,                    # Linux | Windows | Darwin
        "release": _uname("release"),
        "machine": _uname("machine"),
        "distro": _pretty_name(),
        "wsl": wsl,
        # The one flag callers branch on: can we run the POSIX studio stack?
        "posix_stack_ok": _SYSTEM in ("Linux", "Darwin"),
    }


def _pretty_name() -> str | None:
    try:
        for line in Path("/etc/os-release").read_text().splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    return None


# ── resources ───────────────────────────────────────────────────────────────

def detect_cpu() -> dict:
    model = None
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                model = line.split(":", 1)[1].strip()
                break
    except Exception:
        model = _uname("machine") or None
    return {"count": os.cpu_count() or 0, "model": model}


def detect_memory() -> dict:
    total_kb = None
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemTotal:"):
                total_kb = int(line.split()[1])
                break
    except Exception:
        pass
    return {"total_gb": round(total_kb / 1024 / 1024, 1) if total_kb else None}


def detect_disk(path: Path | None = None) -> dict:
    p = path or ROOT
    try:
        u = shutil.disk_usage(p)
        return {
            "path": str(p),
            "total_gb": round(u.total / 1024**3, 1),
            "free_gb": round(u.free / 1024**3, 1),
            "used_pct": round(100 * u.used / u.total) if u.total else None,
        }
    except Exception:
        return {"path": str(p), "total_gb": None, "free_gb": None, "used_pct": None}


def detect_gpu() -> dict:
    """NVIDIA only — the one vendor whose stack our GPU lane (docs/14) targets.

    Under WSL2 the driver lives on the Windows side and nvidia-smi appears in
    /usr/lib/wsl/lib; its presence here is the honest test of whether CUDA work
    can actually run, so we do not special-case the path.
    """
    if not shutil.which("nvidia-smi"):
        return {"present": False, "reason": "nvidia-smi not on PATH"}
    out = _run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader"])
    if not out:
        return {"present": False, "reason": "nvidia-smi present but returned nothing"}
    gpus = []
    for line in out.splitlines():
        parts = [x.strip() for x in line.split(",")]
        if len(parts) >= 3:
            vram = re.sub(r"[^0-9]", "", parts[1])
            gpus.append({
                "name": parts[0],
                "vram_gb": round(int(vram) / 1024, 1) if vram else None,
                "driver": parts[2],
            })
    return {"present": bool(gpus), "gpus": gpus}


# ── tools ───────────────────────────────────────────────────────────────────

def _has_libvmaf(ffmpeg: str) -> bool:
    return "--enable-libvmaf" in _run([ffmpeg, "-version"], timeout=20)


def _ffmpeg_paths() -> tuple[str | None, str | None]:
    """Pick the build that can still do delivery QC.

    Capability beats convenience here. A distro ffmpeg without libvmaf looks
    perfectly healthy and then silently removes the VMAF score from delivery —
    a QC bar that fails open is worse than one that is absent, so a vendored
    build with libvmaf outranks a system build without it.
    """
    sys_ff, sys_fp = shutil.which("ffmpeg"), shutil.which("ffprobe")
    v = ROOT / "vendor" / "ffbin" / "bin"
    vend = (str(v / "ffmpeg"), str(v / "ffprobe")) if \
        ((v / "ffmpeg").is_file() and (v / "ffprobe").is_file()) else None

    if sys_ff and sys_fp:
        if vend and not _has_libvmaf(sys_ff) and _has_libvmaf(vend[0]):
            return vend
        return sys_ff, sys_fp
    if vend:
        return vend
    return sys_ff, sys_fp


def detect_tools() -> dict:
    tools: dict[str, dict] = {}

    def probe(name: str, cmd: list[str], version_re: str = r"(\d+\.\d+(\.\d+)?)"):
        path = shutil.which(cmd[0])
        if not path:
            tools[name] = {"present": False}
            return
        out = _first_line(_run(cmd))
        m = re.search(version_re, out)
        tools[name] = {"present": True, "path": path,
                       "version": m.group(1) if m else None, "raw": out[:120]}

    probe("git", ["git", "--version"])
    probe("python3", ["python3", "--version"])
    probe("node", ["node", "--version"])
    probe("npm", ["npm", "--version"])
    probe("curl", ["curl", "--version"])

    ff, fp = _ffmpeg_paths()
    if ff and fp:
        out = _first_line(_run([ff, "-version"]))
        m = re.search(r"ffmpeg version (\S+)", out)
        tools["ffmpeg"] = {
            "present": True, "path": ff, "ffprobe": fp,
            "version": m.group(1) if m else None,
            "vendored": "vendor/ffbin" in ff,
            # libvmaf backs delivery QC; its absence silently degrades the bar.
            "libvmaf": "--enable-libvmaf" in _run([ff, "-version"]),
        }
    else:
        tools["ffmpeg"] = {"present": False}

    # Blender is a pip wheel (bpy), not a binary — import is the only real test,
    # and it is slow enough that we keep it behind an explicit flag.
    tools["blender_bpy"] = {"present": (ROOT / "vendor" / "blender-headless" / ".venv").is_dir(),
                            "note": "venv presence only; run --deep for an import test"}
    return tools


def detect_blender_deep() -> dict:
    venv_py = ROOT / "vendor" / "blender-headless" / ".venv" / "bin" / "python"
    if not venv_py.is_file():
        return {"present": False, "reason": "no vendor/blender-headless/.venv"}
    out = _run([str(venv_py), "-c", "import bpy; print(bpy.app.version_string)"], timeout=180)
    ok = bool(re.match(r"^\d+\.\d+", out))
    return {"present": ok, "version": out if ok else None, "error": None if ok else out[:200]}


def detect_services() -> dict:
    """Whether this host can run our long jobs as supervised services.

    Without systemd (a bare WSL2 distro before /etc/wsl.conf enables it) a
    background render is only as durable as the shell that launched it — which
    is exactly the failure mode the job queue exists to end.
    """
    has_systemd = Path("/run/systemd/system").is_dir()
    units = {}
    if has_systemd:
        for unit in ("viralreel-jobd.service", "viralreel-mcp.service", "cloudflared.service"):
            state = _run(["systemctl", "is-active", unit]) or "unknown"
            enabled = _run(["systemctl", "is-enabled", unit]) or "unknown"
            units[unit] = {"active": state, "enabled": enabled}
    return {"systemd": has_systemd, "units": units}


# ── verdict ─────────────────────────────────────────────────────────────────

def readiness(profile: dict) -> dict:
    """Turn the facts into a go/no-go with reasons. Warnings never block."""
    blocking: list[str] = []
    warnings: list[str] = []

    if not profile["os"]["posix_stack_ok"]:
        blocking.append(
            "native Windows Python cannot run the studio stack (bash scripts, "
            "POSIX paths, systemd services) — install under WSL2, see docs/15")

    ram = profile["memory"]["total_gb"]
    if ram is not None and ram < MIN_RAM_GB:
        blocking.append(f"{ram} GB RAM is below the {MIN_RAM_GB} GB floor for 1080p work")

    free = profile["disk"]["free_gb"]
    if free is not None:
        if free < MIN_FREE_GB_RENDER:
            blocking.append(f"{free} GB free — renders need at least {MIN_FREE_GB_RENDER} GB headroom")
        elif free < MIN_FREE_GB_INSTALL:
            warnings.append(f"{free} GB free — a full vendor install wants {MIN_FREE_GB_INSTALL} GB")

    for t in ("git", "python3", "node", "ffmpeg"):
        if not profile["tools"].get(t, {}).get("present"):
            blocking.append(f"{t} missing — run install/wsl/bootstrap.sh")

    if profile["tools"].get("ffmpeg", {}).get("present") and \
            not profile["tools"]["ffmpeg"].get("libvmaf"):
        warnings.append("ffmpeg has no libvmaf — delivery QC cannot score VMAF")

    if not profile["services"]["systemd"]:
        warnings.append(
            "systemd is not running — background jobs will not survive a logout. "
            "Under WSL2 set systemd=true in /etc/wsl.conf and `wsl --shutdown`")

    cpus = profile["cpu"]["count"]
    if cpus and cpus < 4:
        warnings.append(f"{cpus} CPU cores — CPU Cycles renders will be slow; see docs/14 for the GPU path")

    if not profile["gpu"]["present"]:
        warnings.append("no NVIDIA GPU visible — the genai profile stays code-level only (docs/14)")

    return {"ready": not blocking, "blocking": blocking, "warnings": warnings}


def collect(deep: bool = False) -> dict:
    profile = {
        "root": str(ROOT),
        "os": detect_os(),
        "cpu": detect_cpu(),
        "memory": detect_memory(),
        "disk": detect_disk(),
        "gpu": detect_gpu(),
        "tools": detect_tools(),
        "services": detect_services(),
    }
    if deep:
        profile["tools"]["blender_bpy"] = detect_blender_deep()
    profile["readiness"] = readiness(profile)
    return profile


# ── output ──────────────────────────────────────────────────────────────────

BOLD, DIM, RED, YELLOW, GREEN, OFF = "\033[1m", "\033[2m", "\033[31m", "\033[33m", "\033[32m", "\033[0m"


def render_human(p: dict) -> str:
    o = p["os"]
    host = o["distro"] or f"{o['system']} {o['release']}"
    if o["wsl"]["is_wsl"]:
        host += f"  {DIM}(WSL{o['wsl']['version']}: {o['wsl']['distro_name']}){OFF}"
    lines = [f"{BOLD}studio host{OFF}  {host}", ""]

    cpu, mem, disk = p["cpu"], p["memory"], p["disk"]
    lines.append(f"  cpu      {cpu['count']} cores  {DIM}{cpu['model'] or '?'}{OFF}")
    lines.append(f"  memory   {mem['total_gb']} GB")
    lines.append(f"  disk     {disk['free_gb']} GB free of {disk['total_gb']} GB  {DIM}{disk['path']}{OFF}")

    g = p["gpu"]
    if g["present"]:
        for d in g["gpus"]:
            lines.append(f"  gpu      {d['name']}  {d['vram_gb']} GB  {DIM}driver {d['driver']}{OFF}")
    else:
        lines.append(f"  gpu      {DIM}none{OFF}")

    lines.append("")
    for name, t in p["tools"].items():
        if t.get("present"):
            extra = ""
            if name == "ffmpeg":
                extra = "  vendored" if t.get("vendored") else ""
                extra += "  +libvmaf" if t.get("libvmaf") else "  (no libvmaf)"
            lines.append(f"  {GREEN}OK{OFF}    {name} {t.get('version') or ''}{DIM}{extra}{OFF}")
        else:
            lines.append(f"  {RED}--{OFF}    {name} {DIM}absent{OFF}")

    s = p["services"]
    lines.append("")
    lines.append(f"  systemd  {'yes' if s['systemd'] else 'no'}")
    for unit, st in s["units"].items():
        mark = GREEN + "OK" + OFF if st["active"] == "active" else DIM + st["active"] + OFF
        lines.append(f"    {mark}  {unit}  {DIM}({st['enabled']}){OFF}")

    r = p["readiness"]
    lines.append("")
    lines.append(f"{GREEN if r['ready'] else RED}{'READY' if r['ready'] else 'NOT READY'}{OFF}")
    for b in r["blocking"]:
        lines.append(f"  {RED}✗{OFF} {b}")
    for w in r["warnings"]:
        lines.append(f"  {YELLOW}!{OFF} {w}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--deep", action="store_true", help="also import bpy (slow)")
    ap.add_argument("--assert-ready", action="store_true",
                    help="exit 1 if the host cannot render")
    a = ap.parse_args()

    p = collect(deep=a.deep)
    print(json.dumps(p, indent=2) if a.json else render_human(p))
    if a.assert_ready and not p["readiness"]["ready"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
