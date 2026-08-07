#!/usr/bin/env python3
"""The studio's control surface — MCP tools for operating this machine remotely.

Two transports, two different jobs:

    python3 server/studio_mcp.py                  # stdio, for Claude Code ON this box
    python3 server/studio_mcp.py --http --port 8787   # for a Claude Code elsewhere

Everything here is fire-and-poll on purpose. Claude.ai gives a tool 300 seconds
and caps a result near 150k characters, so no tool may ever block on a render:
`enqueue` returns a job id immediately and `job_status`/`job_logs` report on it.
The work itself belongs to scripts/studio/jobd.py, which survives the session.

The tools are a thin, typed skin over the job queue and the read-only state of
the repo. They cannot run a command — only name a recipe from config/jobs.yaml
and fill its declared slots — so the blast radius of this server is exactly the
allowlist, whether it is reached over stdio or over the network.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    """Import a studio module by path, WITHOUT putting its directory on sys.path.

    scripts/studio/platform.py shares a name with the stdlib module, so adding
    that directory to sys.path shadows `platform` for everything imported
    afterwards — which silently breaks pydantic, and therefore the MCP SDK, with
    an error that names neither. Loading by file location keeps the collision
    contained to a module we control.
    """
    spec = importlib.util.spec_from_file_location(f"viralreel_{name}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


hostinfo = _load("hostinfo", ROOT / "scripts" / "studio" / "hostinfo.py")
jobd = _load("jobd", ROOT / "scripts" / "studio" / "jobd.py")


def _auth_module():
    """Loaded lazily: the OAuth path pulls in starlette and is only needed when
    the server is actually being exposed."""
    return _load("studio_auth", ROOT / "server" / "studio_auth.py")

from mcp.server import MCPServer  # noqa: E402

INSTRUCTIONS = (
    "Operate the ViralReel render host. Renders are long: enqueue work and "
    "poll it, never wait. Call studio_status first to see whether the host "
    "is healthy and what is already running. Jobs come from a fixed "
    "allowlist — use list_recipes to see what can be run and which "
    "parameters each accepts."
)


class _Registry:
    """Collects tool definitions so the server can be built later.

    The MCPServer has to be constructed with its auth settings, and those are
    not known until the command line is parsed — but the tools below read far
    better as decorators than as a registration list at the bottom of the file.
    This records them and build_server() replays them.
    """

    def __init__(self) -> None:
        self.tools: list[tuple] = []

    def tool(self, **kwargs):
        def decorate(fn):
            self.tools.append((fn, kwargs))
            return fn
        return decorate


server = _Registry()

MAX_CHARS = 100_000     # stay clear of the ~150k client cap, with room for framing


def _clip(text: str, limit: int = MAX_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[-limit:] + f"\n\n[... clipped to the last {limit} characters]"


def _job_line(j: dict) -> str:
    bits = [f"#{j['id']}", j["state"], j["recipe"]]
    if j.get("exit_code") is not None:
        bits.append(f"exit={j['exit_code']}")
    params = json.loads(j.get("params") or "{}")
    if params:
        bits.append(" ".join(f"{k}={v}" for k, v in params.items()))
    line = "  ".join(bits)
    if j["state"] == jobd.RUNNING:
        p = jobd.progress_of(j["id"])
        if p:
            line += f"\n      {p}"
    if j.get("note"):
        line += f"\n      note: {j['note']}"
    return line


# ── read ────────────────────────────────────────────────────────────────────

@server.tool(
    description="Health and current activity of the render host: OS, cores, RAM, "
                "free disk, GPU, tool versions, service state, and the jobs "
                "running or queued right now. Call this first."
)
def studio_status() -> str:
    p = hostinfo.collect()
    r = p["readiness"]
    out = [
        f"host: {p['os']['distro'] or p['os']['system']}"
        + (f" (WSL{p['os']['wsl']['version']})" if p["os"]["wsl"]["is_wsl"] else ""),
        f"cpu: {p['cpu']['count']} cores   ram: {p['memory']['total_gb']} GB   "
        f"disk: {p['disk']['free_gb']} GB free of {p['disk']['total_gb']} GB",
    ]
    g = p["gpu"]
    out.append("gpu: " + (", ".join(f"{d['name']} ({d['vram_gb']} GB)" for d in g["gpus"])
                          if g["present"] else "none"))
    ff = p["tools"].get("ffmpeg", {})
    out.append(f"ffmpeg: {'yes' if ff.get('present') else 'MISSING'}"
               + ("" if not ff.get("present") else
                  f" ({'with' if ff.get('libvmaf') else 'without'} libvmaf)"))
    out.append(f"systemd: {'yes' if p['services']['systemd'] else 'no'}")
    for unit, st in p["services"]["units"].items():
        out.append(f"  {unit}: {st['active']}")

    out.append("")
    out.append("READY" if r["ready"] else "NOT READY")
    for b in r["blocking"]:
        out.append(f"  BLOCKING: {b}")
    for w in r["warnings"]:
        out.append(f"  warning: {w}")

    try:
        active = [j for j in jobd.listing(50)
                  if j["state"] in (jobd.RUNNING, jobd.QUEUED)]
        out.append("")
        out.append(f"jobs active: {len(active)}")
        for j in active[:10]:
            out.append("  " + _job_line(j))
    except Exception as e:
        out.append(f"\njob queue unavailable: {e}")
    return "\n".join(out)


@server.tool(
    description="List the jobs this host is allowed to run, with the parameters "
                "each one accepts. This is a fixed allowlist — nothing outside "
                "it can be executed."
)
def list_recipes() -> str:
    try:
        recipes = jobd.load_recipes()
    except jobd.RecipeError as e:
        return f"recipe file problem: {e}"
    out = []
    for rid, r in sorted(recipes.items()):
        out.append(f"{rid}\n  {r.get('role', '')}")
        for p in r.get("params", []):
            req = "required" if p.get("required", True) and "default" not in p else \
                  f"optional, default {p.get('default')!r}"
            out.append(f"    - {p['name']} ({req}) matching {p['pattern']}")
    return "\n".join(out)


@server.tool(description="Recent jobs, newest first, with their state and progress.")
def list_jobs(limit: int = 15, state: str | None = None) -> str:
    limit = max(1, min(int(limit), 100))
    if state and state not in (jobd.QUEUED, jobd.RUNNING, jobd.SUCCEEDED,
                              jobd.FAILED, jobd.CANCELLED, jobd.INTERRUPTED):
        return (f"unknown state {state!r} — use one of: queued, running, "
                f"succeeded, failed, cancelled, interrupted")
    jobs = jobd.listing(limit, state)
    if not jobs:
        return "no jobs"
    return "\n".join(_job_line(j) for j in jobs)


@server.tool(description="Full detail for one job: state, timings, exit code and latest progress.")
def job_status(job_id: int) -> str:
    j = jobd.get(int(job_id))
    if not j:
        return f"no job {job_id}"
    out = [
        f"job #{j['id']}  {j['state']}",
        f"recipe:    {j['recipe']}",
        f"params:    {j['params']}",
        f"argv:      {' '.join(json.loads(j['argv']))}",
        f"requested: {j['requested_by']} at {j['created_at']}",
    ]
    if j["started_at"]:
        out.append(f"started:   {j['started_at']}")
    if j["ended_at"]:
        out.append(f"ended:     {j['ended_at']}  exit={j['exit_code']}")
    if j["note"]:
        out.append(f"note:      {j['note']}")
    if j["state"] == jobd.RUNNING:
        out.append(f"progress:  {jobd.progress_of(j['id']) or '(no progress line yet)'}")
    return "\n".join(out)


@server.tool(
    description="Tail a job's output log. Use this to diagnose a failure or to "
                "watch a render advance."
)
def job_logs(job_id: int, tail: int = 60) -> str:
    tail = max(1, min(int(tail), 2000))
    text = jobd.tail_log(int(job_id), tail)
    return _clip(text) if text else f"no log for job {job_id} (it may not have started)"


@server.tool(
    description="Film manifests on this host, each with its render state, "
                "duration and whether the cut has been delivered to releases/. "
                "Use the manifest name (left column) as the `film` parameter."
)
def list_films() -> str:
    film_dir = ROOT / "studio" / "film"
    manifests = sorted(p for p in film_dir.glob("*.yaml")
                       if not p.name.endswith(".chain.yaml"))
    if not manifests:
        return "no film manifests in studio/film/"

    rows = []
    for m in manifests:
        name = m.stem
        # The output slug comes from the manifest's `film:` field, not the file
        # name, so trusting the filename would report a delivered film as never
        # rendered — and invite someone to re-run a twelve-hour conform.
        report = film_dir / f"{name}.report.json"
        state, extra = "not rendered", ""
        if report.is_file():
            try:
                d = json.loads(report.read_text())
                out_rel = d.get("output", "")
                dur = d.get("duration_s")
                state = "rendered"
                extra = f"{out_rel}" + (f"  {dur}s" if dur else "")
                if not (ROOT / out_rel).is_file():
                    state = "rendered (master since removed)"
                slug = d.get("film", name)
                delivered = [p.name for p in (ROOT / "releases").glob(f"{slug}*")
                             if p.suffix == ".mp4"]
                if delivered:
                    extra += f"  delivered: {', '.join(delivered)}"
            except Exception as e:
                state, extra = "report unreadable", str(e)[:60]
        rows.append(f"{name:<20} {state:<30} {extra}")

    chains = sorted(p.name[:-len('.chain.yaml')] for p in film_dir.glob("*.chain.yaml"))
    if chains:
        rows.append("")
        rows.append("chains (chain-verify / chain-stitch): " + ", ".join(chains))
    return "\n".join(rows)


@server.tool(
    description="Delivered films in releases/ — the finished, QC-passed cuts."
)
def list_releases() -> str:
    rel = ROOT / "releases"
    if not rel.is_dir():
        return "no releases/ directory"
    rows = []
    for p in sorted(rel.iterdir()):
        if p.is_file():
            rows.append(f"{p.name:<34} {p.stat().st_size / 1024 / 1024:6.1f} MB")
    return "\n".join(rows) if rows else "releases/ is empty"


# ── write ───────────────────────────────────────────────────────────────────

@server.tool(
    description="Queue a job and return its id immediately. Renders take hours; "
                "this never blocks. Poll with job_status. `params` is a mapping "
                "of the recipe's declared parameters, e.g. {\"film\": \"keeper\"}."
)
def enqueue(recipe: str, params: dict | None = None) -> str:
    try:
        jid = jobd.enqueue(recipe, {k: str(v) for k, v in (params or {}).items()},
                           requested_by="mcp")
    except jobd.RecipeError as e:
        return f"rejected: {e}"
    except Exception as e:
        return f"could not queue: {e}"
    return (f"queued job #{jid} ({recipe}). Poll with job_status({jid}); "
            f"follow output with job_logs({jid}).")


@server.tool(description="Stop a queued or running job.")
def cancel_job(job_id: int) -> str:
    return f"job #{job_id}: {jobd.cancel(int(job_id))}"


def build_server(public_url: str | None = None) -> MCPServer:
    """Construct the real server, with OAuth when a public URL is given.

    Without `public_url` this is a local server: stdio, or HTTP on loopback for
    a client on this machine. With one, it becomes its own OAuth authorization
    server so claude.ai will accept it as a custom connector — that is the only
    shape claude.ai takes, short of an authless server anyone who learned the
    URL could drive.
    """
    kwargs = dict(name="viralreel-studio", title="ViralReel Studio",
                  version="1.0.0", instructions=INSTRUCTIONS)

    provider = None
    if public_url:
        from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions
        auth_mod = _auth_module()

        if not auth_mod.has_passphrase():
            raise SystemExit(
                "No studio passphrase is set, so nothing could authorise a connection.\n"
                "Run:  python3 server/studio_auth.py set-passphrase")

        provider = auth_mod.StudioAuthProvider(public_url)
        kwargs["auth_server_provider"] = provider
        kwargs["auth"] = AuthSettings(
            issuer_url=public_url,
            resource_server_url=f"{public_url.rstrip('/')}/mcp",
            # Claude introduces itself by registering dynamically; registration
            # on its own grants nothing, because the consent step still demands
            # the owner's passphrase.
            client_registration_options=ClientRegistrationOptions(enabled=True),
        )

    srv = MCPServer(**kwargs)
    for fn, opts in server.tools:
        srv.add_tool(fn, **opts)

    if provider is not None:
        _attach_consent_route(srv, provider)
    return srv


def _attach_consent_route(srv: MCPServer, provider) -> None:
    """The page where a human proves they own this machine."""
    from starlette.responses import HTMLResponse, RedirectResponse
    auth_mod = _auth_module()

    @srv.custom_route("/consent", methods=["GET", "POST"])
    async def consent(request):  # noqa: ANN001
        if request.method == "GET":
            req_id = request.query_params.get("req", "")
            pending = provider.load_pending(req_id)
            if not pending:
                return HTMLResponse(
                    "<h1>This authorization request expired</h1>"
                    "<p>Start again from Claude's connector settings.</p>", status_code=400)
            return HTMLResponse(auth_mod.render_consent(pending["client_name"], req_id))

        form = await request.form()
        req_id = str(form.get("req", ""))
        pending = provider.load_pending(req_id)
        if not pending:
            return HTMLResponse("<h1>This authorization request expired</h1>", status_code=400)

        locked = auth_mod._locked_out()
        if locked:
            return HTMLResponse(
                auth_mod.render_consent(
                    pending["client_name"], req_id,
                    f"Too many failed attempts. Try again in {locked} seconds."),
                status_code=429)

        if not auth_mod.check_passphrase(str(form.get("passphrase", ""))):
            return HTMLResponse(
                auth_mod.render_consent(pending["client_name"], req_id,
                                        "That passphrase is not right."),
                status_code=401)

        target = provider.complete_consent(req_id)
        if not target:
            return HTMLResponse("<h1>This authorization request expired</h1>", status_code=400)
        return RedirectResponse(target, status_code=302)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--http", action="store_true",
                    help="serve Streamable HTTP instead of stdio")
    ap.add_argument("--host", default="127.0.0.1",
                    help="bind address (default loopback — see docs/15 before widening)")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--public-url", default=os.environ.get("VIRALREEL_PUBLIC_URL"),
                    help="the public HTTPS origin this server is reachable at, e.g. "
                         "https://studio.example.com. Turns on OAuth so claude.ai "
                         "will accept it as a custom connector.")
    a = ap.parse_args()

    if not a.http:
        build_server().run(transport="stdio")
        return 0

    if a.public_url:
        if not a.public_url.startswith("https://"):
            # OAuth over plaintext hands the token to anyone on the path, and the
            # MCP spec requires HTTPS for every authorization endpoint.
            print("--public-url must be https:// — OAuth over http is not acceptable "
                  "and claude.ai will not accept it either.", file=sys.stderr)
            return 2
        a.public_url = a.public_url.rstrip("/")

    srv = build_server(a.public_url)

    if a.public_url:
        print(f"OAuth enabled. Add this URL as a custom connector in Claude:\n"
              f"    {a.public_url}/mcp\n"
              f"Consent page: {a.public_url}/consent", file=sys.stderr)
    elif a.host not in ("127.0.0.1", "localhost", "::1"):
        print(f"WARNING: binding {a.host}:{a.port} beyond loopback with NO "
              f"authentication. Anything that can reach this port can queue jobs "
              f"on this machine. Pass --public-url to enable OAuth (docs/15).",
              file=sys.stderr)

    # host/port are transport kwargs in SDK 2.x — there is no settings.host.
    srv.run(transport="streamable-http", host=a.host, port=a.port,
            streamable_http_path="/mcp")
    return 0


if __name__ == "__main__":
    sys.exit(main())
