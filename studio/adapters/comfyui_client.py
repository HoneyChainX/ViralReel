#!/usr/bin/env python3
"""Headless ComfyUI driver — the only sanctioned way this studio talks to ComfyUI.

ComfyUI is the node-graph engine every open model (LTX-2, Wan2.2, image models) plugs
into. Its automation surface is a REST endpoint: POST a workflow JSON graph to /prompt,
poll /history/<prompt_id> for outputs. This client wraps exactly that, stdlib-only, so
render-wrangler and the ralph loops need no extra dependencies.

Usage:
  python3 studio/adapters/comfyui_client.py --selftest            # server reachable + API sane
  python3 studio/adapters/comfyui_client.py --selftest --offline  # import/contract check only
  python3 studio/adapters/comfyui_client.py submit workflow.json  # queue a graph, wait, list outputs

Environment:
  COMFYUI_HOST   default 127.0.0.1:8188
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

HOST = os.environ.get("COMFYUI_HOST", "127.0.0.1:8188")
BASE = f"http://{HOST}"


def _get(path: str, timeout: float = 10.0) -> dict:
    with urllib.request.urlopen(f"{BASE}{path}", timeout=timeout) as r:
        return json.loads(r.read())


def _post(path: str, payload: dict, timeout: float = 30.0) -> dict:
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def submit(workflow: dict, client_id: str | None = None) -> str:
    """Queue a workflow graph; returns the prompt_id."""
    out = _post("/prompt", {"prompt": workflow, "client_id": client_id or uuid.uuid4().hex})
    if "prompt_id" not in out:
        raise RuntimeError(f"ComfyUI rejected the workflow: {out}")
    return out["prompt_id"]


def wait(prompt_id: str, timeout_s: float = 3600.0, poll_s: float = 3.0) -> dict:
    """Block until the prompt completes; returns its history entry (outputs inside)."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        hist = _get(f"/history/{prompt_id}")
        if prompt_id in hist:
            entry = hist[prompt_id]
            status = entry.get("status", {})
            if status.get("completed") or entry.get("outputs"):
                return entry
            if status.get("status_str") == "error":
                raise RuntimeError(f"ComfyUI job {prompt_id} errored: {status}")
        time.sleep(poll_s)
    raise TimeoutError(f"ComfyUI job {prompt_id} did not finish in {timeout_s}s")


def output_files(entry: dict) -> list[str]:
    files = []
    for node_out in entry.get("outputs", {}).values():
        for kind in ("images", "gifs", "videos", "audio"):
            for f in node_out.get(kind, []):
                files.append(f.get("filename", ""))
    return [f for f in files if f]


def selftest(offline: bool) -> int:
    if offline:
        # Contract check only: the module loads and the API shapes are self-consistent.
        assert callable(submit) and callable(wait) and callable(output_files)
        print("comfyui_client offline selftest: OK (module contract only, no server)")
        return 0
    try:
        stats = _get("/system_stats", timeout=5.0)
    except (urllib.error.URLError, OSError) as e:
        print(f"comfyui_client selftest: FAIL — no ComfyUI at {BASE} ({e}).\n"
              "Start it headless:  cd vendor/comfyui && .venv/bin/python main.py --listen")
        return 1
    devices = ", ".join(d.get("name", "?") for d in stats.get("devices", [])) or "none reported"
    print(f"comfyui_client selftest: OK — server {BASE}, devices: {devices}")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "--selftest" in args:
        return selftest(offline="--offline" in args)
    if args and args[0] == "submit" and len(args) > 1:
        wf = json.loads(open(args[1]).read())
        pid = submit(wf)
        print(f"queued {pid}; waiting…")
        entry = wait(pid)
        for f in output_files(entry):
            print(f"output: {f}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
