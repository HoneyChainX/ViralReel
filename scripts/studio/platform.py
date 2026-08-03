#!/usr/bin/env python3
"""Studio platform manager — installs and verifies the modules in config/platform.yaml.

The manifest is the single source of truth for what this studio integrates: every vendor
repo, its pinned ref, which profile it belongs to, whether it can be driven headlessly,
what it costs, and how to prove it works. Vendors are never forked or patched — they are
cloned to vendor/<id> and configured from outside, the same contract scripts/setup.sh
established for OpenMontage.

Commands:
  platform.py list    [--profile P]      show modules and their state
  platform.py install [--profile P]      clone + install enabled modules for a profile
  platform.py doctor  [--profile P]      verify everything; exit 1 on any red check
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "config" / "platform.yaml"
VENDOR = ROOT / "vendor"

BOLD, GREEN, RED, YELLOW, DIM, OFF = "\033[1m", "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"

COST_CLASSES = {"free", "freemium", "paid"}
GPU_CLASSES = {"none", "optional", "required"}


def load_manifest() -> dict:
    data = yaml.safe_load(MANIFEST.read_text())
    problems = []
    seen = set()
    for m in data.get("modules", []):
        mid = m.get("id", "<missing id>")
        if mid in seen:
            problems.append(f"duplicate module id: {mid}")
        seen.add(mid)
        for key in ("repo", "profile", "role", "license", "cost", "gpu"):
            if key not in m:
                problems.append(f"{mid}: missing required key '{key}'")
        if m.get("cost") not in COST_CLASSES:
            problems.append(f"{mid}: cost must be one of {sorted(COST_CLASSES)}")
        if m.get("gpu") not in GPU_CLASSES:
            problems.append(f"{mid}: gpu must be one of {sorted(GPU_CLASSES)}")
        if m.get("cost") == "paid" and m.get("enabled", False):
            problems.append(
                f"{mid}: paid module enabled by default — forbidden. Paid connectors are "
                "a founder decision made per project, not a manifest default (DECISIONS D8)."
            )
    if problems:
        for p in problems:
            print(f"{RED}manifest error:{OFF} {p}", file=sys.stderr)
        sys.exit(1)
    return data


def selected(data: dict, profile: str | None) -> list[dict]:
    profile = profile or data.get("default_profile", "core")
    if profile == "all":
        return list(data["modules"])
    known = set(data.get("profiles", {}))
    if profile not in known:
        print(f"{RED}unknown profile '{profile}'{OFF} — known: {', '.join(sorted(known))} or 'all'",
              file=sys.stderr)
        sys.exit(1)
    return [m for m in data["modules"] if m["profile"] == profile]


def host_has_gpu() -> bool:
    return shutil.which("nvidia-smi") is not None and subprocess.run(
        ["nvidia-smi", "-L"], capture_output=True).returncode == 0


def sh(cmd: str, cwd: Path | None = None) -> int:
    return subprocess.run(cmd, shell=True, cwd=cwd or ROOT).returncode


def module_dir(m: dict) -> Path:
    return VENDOR / m["id"]


# ── install ─────────────────────────────────────────────────────────────────

def install(data: dict, profile: str | None) -> int:
    gpu = host_has_gpu()
    failures = 0
    for m in selected(data, profile):
        mid = m["id"]
        if not m.get("enabled", False):
            print(f"{DIM}skip {mid} (disabled in manifest){OFF}")
            continue
        if m.get("install") == "desktop":
            print(f"{DIM}skip {mid} (desktop app — human-installed, see notes){OFF}")
            continue
        print(f"{BOLD}==> {mid}{OFF}  {DIM}{m['role']}{OFF}")

        dest = module_dir(m)
        if m.get("repo", "").startswith("http"):
            if (dest / ".git").exists():
                sh("git fetch --depth 1 origin", cwd=dest)
            else:
                if sh(f"git clone --depth 1 {m['repo']} {dest}") != 0:
                    print(f"  {RED}clone failed{OFF}")
                    failures += 1
                    continue
            ref = m.get("ref")
            if ref and ref not in ("main", "master"):
                sh(f"git fetch --depth 1 origin {ref} && git checkout -q {ref}", cwd=dest)

        if m["gpu"] == "required" and not gpu:
            print(f"  {YELLOW}no GPU on this host — installed to code+config level only{OFF}")
            continue

        cmd = m.get("install_cmd")
        if cmd:
            if sh(cmd, cwd=dest if dest.exists() else ROOT) != 0:
                print(f"  {RED}install_cmd failed: {cmd}{OFF}")
                failures += 1
    return 1 if failures else 0


# ── doctor ──────────────────────────────────────────────────────────────────

def run_check(check: dict, m: dict) -> tuple[bool, str]:
    kind = check.get("type")
    if kind == "dir":
        p = ROOT / check["path"]
        return p.is_dir(), f"dir {check['path']}"
    if kind == "file":
        p = ROOT / check["path"]
        return p.is_file(), f"file {check['path']}"
    if kind == "cmd":
        rc = subprocess.run(check["run"], shell=True, cwd=ROOT,
                            capture_output=True, timeout=check.get("timeout", 120)).returncode
        return rc == 0, f"cmd `{check['run']}`"
    return False, f"unknown check type {kind!r}"


def doctor(data: dict, profile: str | None) -> int:
    gpu = host_has_gpu()
    red = 0
    print(f"{BOLD}studio doctor{OFF}  host GPU: {'yes' if gpu else 'no'}\n")

    # Cost audit first — it can fail the run regardless of module state.
    for m in data["modules"]:
        if m.get("cost") == "paid" and m.get("enabled", False):
            print(f"{RED}✗ COST{OFF} paid module '{m['id']}' is enabled — forbidden by default")
            red += 1

    for m in selected(data, profile):
        mid = m["id"]
        if not m.get("enabled", False):
            print(f"{DIM}- {mid:<18} disabled{OFF}")
            continue
        if m["gpu"] == "required" and not gpu:
            checks = [c for c in m.get("doctor", []) if c.get("needs_gpu") is not True]
        else:
            checks = m.get("doctor", [])
        if not checks:
            print(f"{YELLOW}? {mid:<18} no doctor checks declared{OFF}")
            continue
        for c in checks:
            ok, desc = run_check(c, m)
            mark = f"{GREEN}✓{OFF}" if ok else f"{RED}✗{OFF}"
            print(f"{mark} {mid:<18} {desc}")
            red += 0 if ok else 1

    print()
    if red:
        print(f"{RED}{red} red check(s).{OFF} The doctor is loud on purpose — fix or disable, never mute.")
        return 1
    print(f"{GREEN}All green for profile '{profile or data.get('default_profile')}'.{OFF}")
    return 0


# ── list ────────────────────────────────────────────────────────────────────

def list_modules(data: dict, profile: str | None) -> int:
    for m in selected(data, profile):
        state = "enabled " if m.get("enabled") else "disabled"
        installed = "installed" if (module_dir(m) / ".git").exists() else "—"
        print(f"{BOLD}{m['id']:<18}{OFF} {m['profile']:<13} {m['cost']:<9} gpu:{m['gpu']:<9} "
              f"{state} {installed:<10} {DIM}{m['role']}{OFF}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=["list", "install", "doctor"])
    ap.add_argument("--profile", default=None,
                    help="core | genai | animation | distribution | all (default: manifest default)")
    args = ap.parse_args()
    data = load_manifest()
    return {"list": list_modules, "install": install, "doctor": doctor}[args.command](data, args.profile)


if __name__ == "__main__":
    sys.exit(main())
