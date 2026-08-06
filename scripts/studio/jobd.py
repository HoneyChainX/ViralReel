#!/usr/bin/env python3
"""The job queue — how a render outlives the conversation that asked for it.

A remote operator cannot hold a six-hour Cycles render open on an MCP call, and
this studio has already learned the hard way that a detached process is only as
durable as the shell that spawned it. So work is enqueued, not executed: the
caller gets an id back immediately and a supervised worker runs the job to
completion whether or not anyone is still watching.

    jobd.py enqueue render-film -p film=keeper     # -> job id, returns at once
    jobd.py worker                                 # the supervised loop (systemd)
    jobd.py status [ID] | logs ID [--tail N] | cancel ID | list | reap

SECURITY: a job is never a command string. Recipes in config/jobs.yaml declare a
fixed argv, and only the parameter slots they name can be filled — each against
its own regex. There is no shell, no interpolation into the command name, and no
recipe that takes free text. That is what makes it safe to expose remotely.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import signal
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VAR = ROOT / "var"
DB_PATH = VAR / "jobs.db"
LOG_DIR = VAR / "logs"
RECIPES = ROOT / "config" / "jobs.yaml"

QUEUED, RUNNING, SUCCEEDED, FAILED, CANCELLED, INTERRUPTED = (
    "queued", "running", "succeeded", "failed", "cancelled", "interrupted")
TERMINAL = {SUCCEEDED, FAILED, CANCELLED, INTERRUPTED}

# Progress lines the engines already print. We surface the last one rather than
# inventing a percentage — a real "Fra:212/384" is worth more than a fake bar.
PROGRESS_PATTERNS = [
    re.compile(r"Fra:\d+.*"),                 # Blender Cycles
    re.compile(r"frame=\s*\d+.*"),            # ffmpeg
    re.compile(r"Rendered \d+/\d+.*"),        # Remotion
    re.compile(r"\d+%\|.*"),                  # tqdm
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ── recipes ─────────────────────────────────────────────────────────────────

class RecipeError(Exception):
    pass


def load_recipes(path: Path | None = None) -> dict[str, dict]:
    import yaml  # deliberately late: hostinfo/bootstrap run before deps exist
    p = path or RECIPES
    if not p.is_file():
        raise RecipeError(f"no recipe file at {p}")
    data = yaml.safe_load(p.read_text()) or {}
    jobs = {}
    for r in data.get("jobs", []):
        rid = r.get("id")
        if not rid:
            raise RecipeError("a recipe has no id")
        if not isinstance(r.get("argv"), list) or not r["argv"]:
            raise RecipeError(f"recipe {rid}: argv must be a non-empty list")
        # The command itself must be literal. Allowing a placeholder in argv[0]
        # would turn the allowlist into arbitrary execution.
        if "{" in r["argv"][0]:
            raise RecipeError(f"recipe {rid}: argv[0] must be a literal command")
        declared = {p_["name"] for p_ in r.get("params", [])}
        for slot in re.findall(r"\{(\w+)\}", " ".join(r["argv"])):
            if slot not in declared:
                raise RecipeError(f"recipe {rid}: argv uses undeclared param {slot!r}")
        for p_ in r.get("params", []):
            if "pattern" not in p_:
                raise RecipeError(f"recipe {rid}: param {p_.get('name')} has no pattern")
            re.compile(p_["pattern"])  # fail loudly at load, not at run
        jobs[rid] = r
    if not jobs:
        raise RecipeError(f"{p} declares no jobs")
    return jobs


def build_argv(recipe: dict, params: dict[str, str]) -> list[str]:
    """Validate params against the recipe and fill only the declared slots."""
    spec = {p["name"]: p for p in recipe.get("params", [])}
    for name in params:
        if name not in spec:
            raise RecipeError(f"unknown parameter {name!r} for job {recipe['id']}")
    resolved: dict[str, str] = {}
    for name, p in spec.items():
        if name in params:
            value = str(params[name])
        elif "default" in p:
            value = str(p["default"])
        elif p.get("required", True):
            raise RecipeError(f"missing required parameter {name!r}")
        else:
            continue
        if not re.fullmatch(p["pattern"], value):
            raise RecipeError(
                f"parameter {name}={value!r} rejected by pattern {p['pattern']}")
        resolved[name] = value

    argv: list[str] = []
    for token in recipe["argv"]:
        slots = re.findall(r"\{(\w+)\}", token)
        if not slots:
            argv.append(token)
            continue
        # An optional param with no value drops its whole token, so a recipe can
        # declare `--flag {opt}` without emitting a dangling flag.
        if any(s not in resolved for s in slots):
            continue
        argv.append(re.sub(r"\{(\w+)\}", lambda m: resolved[m.group(1)], token))
    return argv


# ── store ───────────────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  recipe     TEXT NOT NULL,
  params     TEXT NOT NULL DEFAULT '{}',
  argv       TEXT NOT NULL,
  state      TEXT NOT NULL,
  pid        INTEGER,
  exit_code  INTEGER,
  note       TEXT,
  requested_by TEXT,
  created_at TEXT NOT NULL,
  started_at TEXT,
  ended_at   TEXT
);
CREATE INDEX IF NOT EXISTS jobs_state ON jobs(state);
"""


def connect() -> sqlite3.Connection:
    VAR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
    c.row_factory = sqlite3.Row
    # WAL lets the MCP server read status while the worker writes.
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA busy_timeout=30000")
    c.executescript(SCHEMA)
    return c


def log_path(job_id: int) -> Path:
    return LOG_DIR / f"job-{job_id:06d}.log"


def enqueue(recipe_id: str, params: dict, requested_by: str = "cli",
            recipes: dict | None = None) -> int:
    recipes = recipes or load_recipes()
    if recipe_id not in recipes:
        raise RecipeError(f"unknown job {recipe_id!r} — known: {', '.join(sorted(recipes))}")
    argv = build_argv(recipes[recipe_id], params)
    with connect() as c:
        cur = c.execute(
            "INSERT INTO jobs(recipe, params, argv, state, requested_by, created_at)"
            " VALUES (?,?,?,?,?,?)",
            (recipe_id, json.dumps(params), json.dumps(argv), QUEUED, requested_by, now()))
        return int(cur.lastrowid)


def get(job_id: int) -> dict | None:
    with connect() as c:
        row = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    return dict(row) if row else None


def listing(limit: int = 20, state: str | None = None) -> list[dict]:
    q = "SELECT * FROM jobs"
    args: list = []
    if state:
        q += " WHERE state=?"
        args.append(state)
    q += " ORDER BY id DESC LIMIT ?"
    args.append(limit)
    with connect() as c:
        return [dict(r) for r in c.execute(q, args).fetchall()]


def progress_of(job_id: int) -> str | None:
    """Last engine-emitted progress line, read from the tail of the log."""
    p = log_path(job_id)
    if not p.is_file():
        return None
    try:
        with p.open("rb") as f:
            f.seek(0, os.SEEK_END)
            back = min(f.tell(), 16384)
            f.seek(-back, os.SEEK_END)
            tail = f.read().decode("utf-8", "replace")
    except Exception:
        return None
    for line in reversed(tail.splitlines()):
        for pat in PROGRESS_PATTERNS:
            m = pat.search(line)
            if m:
                return m.group(0)[:200]
    return None


def tail_log(job_id: int, lines: int = 40) -> str:
    p = log_path(job_id)
    if not p.is_file():
        return ""
    try:
        with p.open("rb") as f:
            f.seek(0, os.SEEK_END)
            back = min(f.tell(), 256 * 1024)
            f.seek(-back, os.SEEK_END)
            text = f.read().decode("utf-8", "replace")
    except Exception as e:
        return f"<log unreadable: {e}>"
    return "\n".join(text.splitlines()[-lines:])


def _alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def cancel(job_id: int) -> str:
    job = get(job_id)
    if not job:
        return "no such job"
    if job["state"] in TERMINAL:
        return f"already {job['state']}"
    with connect() as c:
        if job["state"] == QUEUED:
            c.execute("UPDATE jobs SET state=?, ended_at=?, note=? WHERE id=?",
                      (CANCELLED, now(), "cancelled before start", job_id))
            return "cancelled (was queued)"
        # The worker starts each job in its own session, so one signal to the
        # negative pid reaches ffmpeg/Blender children too — no orphans.
        if _alive(job["pid"]):
            try:
                os.killpg(job["pid"], signal.SIGTERM)
            except OSError:
                pass
        c.execute("UPDATE jobs SET state=?, ended_at=?, note=? WHERE id=?",
                  (CANCELLED, now(), "cancelled by operator", job_id))
    return "cancelled (signalled)"


def reap() -> list[int]:
    """Clear jobs left mid-flight by a worker that died.

    We do not try to re-adopt a live orphan: its output stream belonged to the
    dead worker, so we could never report its exit honestly. Killing is the
    truthful option, and it is safe here because our long renders are written as
    resumable chunks (they restart by counting the frames already on disk).
    """
    reaped = []
    with connect() as c:
        for row in c.execute("SELECT * FROM jobs WHERE state=?", (RUNNING,)).fetchall():
            if _alive(row["pid"]):
                try:
                    os.killpg(row["pid"], signal.SIGTERM)
                except OSError:
                    pass
            c.execute("UPDATE jobs SET state=?, ended_at=?, note=? WHERE id=?",
                      (INTERRUPTED, now(), "worker restarted while this job was running",
                       row["id"]))
            reaped.append(row["id"])
    return reaped


# ── worker ──────────────────────────────────────────────────────────────────

def _claim() -> dict | None:
    """Take the oldest queued job. IMMEDIATE holds the write lock so two
    workers can never claim the same row."""
    with connect() as c:
        try:
            c.execute("BEGIN IMMEDIATE")
            row = c.execute(
                "SELECT * FROM jobs WHERE state=? ORDER BY id LIMIT 1", (QUEUED,)).fetchone()
            if not row:
                c.execute("COMMIT")
                return None
            c.execute("UPDATE jobs SET state=?, started_at=? WHERE id=?",
                      (RUNNING, now(), row["id"]))
            c.execute("COMMIT")
            return dict(row)
        except sqlite3.OperationalError:
            return None


def run_job(job: dict, recipes: dict) -> int:
    argv = json.loads(job["argv"])
    recipe = recipes.get(job["recipe"], {})
    timeout = int(recipe.get("timeout", 6 * 3600))
    lp = log_path(job["id"])

    env = dict(os.environ)
    # Every recipe runs from the repo root with the vendored ffmpeg reachable,
    # so a job behaves the same whether a human or the queue started it.
    ffbin = ROOT / "vendor" / "ffbin" / "bin"
    if ffbin.is_dir():
        env["PATH"] = f"{ffbin}{os.pathsep}{env.get('PATH', '')}"

    with lp.open("w", buffering=1) as log:
        log.write(f"# job {job['id']} · {job['recipe']} · {now()}\n")
        log.write(f"# argv: {' '.join(argv)}\n\n")
        log.flush()
        try:
            proc = subprocess.Popen(
                argv, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                env=env, start_new_session=True)
        except FileNotFoundError as e:
            log.write(f"\n# FAILED to start: {e}\n")
            with connect() as c:
                c.execute("UPDATE jobs SET state=?, ended_at=?, note=? WHERE id=?",
                          (FAILED, now(), f"could not start: {e}", job["id"]))
            return 127

        with connect() as c:
            c.execute("UPDATE jobs SET pid=? WHERE id=?", (proc.pid, job["id"]))

        try:
            rc = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            log.write(f"\n# TIMEOUT after {timeout}s — terminating\n")
            _terminate(proc)
            rc = proc.wait()
            with connect() as c:
                c.execute("UPDATE jobs SET state=?, exit_code=?, ended_at=?, note=? WHERE id=?",
                          (FAILED, rc, now(), f"timed out after {timeout}s", job["id"]))
            return rc

    # A cancel already wrote a terminal state; do not overwrite the operator's record.
    current = get(job["id"])
    if current and current["state"] in TERMINAL:
        return rc
    with connect() as c:
        c.execute("UPDATE jobs SET state=?, exit_code=?, ended_at=? WHERE id=?",
                  (SUCCEEDED if rc == 0 else FAILED, rc, now(), job["id"]))
    return rc


def _terminate(proc: subprocess.Popen, grace: float = 15.0) -> None:
    """SIGTERM the group, then SIGKILL what is left. Blender ignores a polite
    ask mid-tile, and a half-killed render holds the CPU we need."""
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except OSError:
        return
    deadline = time.time() + grace
    while time.time() < deadline:
        if proc.poll() is not None:
            return
        time.sleep(0.3)
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except OSError:
        pass


def worker(poll: float = 2.0, once: bool = False) -> int:
    recipes = load_recipes()
    for jid in reap():
        print(f"reaped interrupted job {jid}", flush=True)
    print(f"worker ready · {len(recipes)} recipes · db {DB_PATH}", flush=True)

    stopping = {"now": False}

    def _stop(signum, frame):
        # Finish the job in hand; systemd's TimeoutStopSec decides how long we get.
        stopping["now"] = True
        print(f"signal {signum} — no new jobs will be claimed", flush=True)

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    while not stopping["now"]:
        job = _claim()
        if not job:
            if once:
                return 0
            time.sleep(poll)
            continue
        print(f"job {job['id']} start · {job['recipe']}", flush=True)
        rc = run_job(job, recipes)
        print(f"job {job['id']} end · exit {rc}", flush=True)
        if once:
            return 0
    return 0


# ── cli ─────────────────────────────────────────────────────────────────────

def _kv(pairs: list[str]) -> dict[str, str]:
    out = {}
    for item in pairs or []:
        if "=" not in item:
            raise SystemExit(f"parameter must be key=value, got {item!r}")
        k, v = item.split("=", 1)
        out[k] = v
    return out


def _print_job(j: dict, with_progress: bool = True) -> None:
    line = f"#{j['id']:<5} {j['state']:<11} {j['recipe']:<20} {j['created_at']}"
    if j.get("exit_code") is not None:
        line += f"  exit={j['exit_code']}"
    print(line)
    if j.get("note"):
        print(f"       note: {j['note']}")
    if with_progress and j["state"] == RUNNING:
        p = progress_of(j["id"])
        if p:
            print(f"       {p}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("enqueue", help="queue a job and print its id")
    e.add_argument("recipe")
    e.add_argument("-p", "--param", action="append", metavar="K=V")
    e.add_argument("--by", default="cli")

    s = sub.add_parser("status", help="one job, or a summary")
    s.add_argument("id", nargs="?", type=int)

    lg = sub.add_parser("logs", help="tail a job log")
    lg.add_argument("id", type=int)
    lg.add_argument("--tail", type=int, default=40)

    c = sub.add_parser("cancel", help="stop a job")
    c.add_argument("id", type=int)

    ls = sub.add_parser("list", help="recent jobs")
    ls.add_argument("--limit", type=int, default=20)
    ls.add_argument("--state")

    w = sub.add_parser("worker", help="run the supervised loop")
    w.add_argument("--once", action="store_true", help="drain one job then exit")
    w.add_argument("--poll", type=float, default=2.0)

    sub.add_parser("recipes", help="list the allowlisted jobs")
    sub.add_parser("reap", help="clear jobs orphaned by a dead worker")

    a = ap.parse_args()

    try:
        if a.cmd == "enqueue":
            jid = enqueue(a.recipe, _kv(a.param), requested_by=a.by)
            print(jid)
            return 0

        if a.cmd == "status":
            if a.id:
                j = get(a.id)
                if not j:
                    print(f"no job {a.id}", file=sys.stderr)
                    return 1
                _print_job(j)
                return 0
            for j in listing(10):
                _print_job(j)
            return 0

        if a.cmd == "logs":
            print(tail_log(a.id, a.tail))
            return 0

        if a.cmd == "cancel":
            print(cancel(a.id))
            return 0

        if a.cmd == "list":
            for j in listing(a.limit, a.state):
                _print_job(j, with_progress=False)
            return 0

        if a.cmd == "recipes":
            for rid, r in sorted(load_recipes().items()):
                params = ", ".join(p["name"] for p in r.get("params", [])) or "—"
                print(f"{rid:<22} {r.get('role', '')}\n{'':<22} params: {params}")
            return 0

        if a.cmd == "reap":
            ids = reap()
            print(f"reaped {len(ids)}: {ids}" if ids else "nothing to reap")
            return 0

        if a.cmd == "worker":
            return worker(poll=a.poll, once=a.once)

    except RecipeError as ex:
        print(f"recipe error: {ex}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
