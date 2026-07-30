#!/usr/bin/env python3
"""
Regression tests for the publish gate.

The gate is the only real logic in this repo and the only thing standing between
a bad number and YouTube. A test that merely asserts "the gate ran" is worthless —
these assert the verdict of every individual check, on both a compliant episode
and a deliberately non-compliant one.

Stdlib only, matching the gate itself. Run: python3 -m unittest discover tests -v
"""

import json
import pathlib
import re
import shutil
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "gate.py"
EPISODES = ROOT / "content" / "episodes"
FIXTURE = EPISODES / "_selftest"
NEGATIVE = EPISODES / "_negtest"
PUBLISH_LOG = ROOT / "content" / "publish_log.json"
VIDEO = ROOT / "out" / "_selftest.mp4"

HAVE_FFMPEG = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def run_gate(slug):
    """Run the gate and return its parsed gate.json."""
    proc = subprocess.run(
        [sys.executable, str(GATE), "--slug", slug],
        capture_output=True, text=True, cwd=ROOT, timeout=180,
    )
    report = EPISODES / slug / "gate.json"
    if not report.exists():
        raise AssertionError(f"gate wrote no report for {slug}\n{proc.stdout}\n{proc.stderr}")
    return json.loads(report.read_text()), proc


def verdicts(report):
    return {c["id"]: c["result"] for c in report["checks"]}


def make_video(path, width=1080, height=1920, seconds=38):
    """Synthesize a delivery-spec video so C9 can be tested for real."""
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-f", "lavfi", "-i", f"color=c=black:s={width}x{height}:r=30:d={seconds}",
         "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
         "-shortest", "-t", str(seconds),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
         str(path)],
        check=True, capture_output=True, timeout=300,
    )


class GateTestBase(unittest.TestCase):
    def setUp(self):
        self._log_backup = PUBLISH_LOG.read_bytes() if PUBLISH_LOG.exists() else None

    def tearDown(self):
        shutil.rmtree(NEGATIVE, ignore_errors=True)
        if self._log_backup is not None:
            PUBLISH_LOG.write_bytes(self._log_backup)
        elif PUBLISH_LOG.exists():
            PUBLISH_LOG.unlink()


class TestCompliantEpisode(GateTestBase):
    """The fixture is compliant in every respect except the render, which is
    gitignored. With a synthesized render present, the gate must PASS outright."""

    @unittest.skipUnless(HAVE_FFMPEG, "ffmpeg/ffprobe not installed")
    def test_full_pass_with_render(self):
        make_video(VIDEO)
        try:
            report, proc = run_gate("_selftest")
            v = verdicts(report)
            failed = [k for k, r in v.items() if r != "PASS"]
            self.assertEqual(report["verdict"], "PASS",
                             f"expected PASS, failing checks: {failed}\n{proc.stdout}")
            self.assertEqual(len(v), 10, "all ten checks must be evaluated")
            self.assertEqual(proc.returncode, 0)
        finally:
            VIDEO.unlink(missing_ok=True)

    def test_missing_render_fails_c9_only(self):
        VIDEO.unlink(missing_ok=True)
        report, proc = run_gate("_selftest")
        v = verdicts(report)
        self.assertEqual(v["C9"], "FAIL", "missing render must fail delivery QC")
        self.assertEqual(report["verdict"], "FAIL")
        self.assertNotEqual(proc.returncode, 0, "a failing gate must exit non-zero")
        for cid in ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C10"):
            self.assertEqual(v[cid], "PASS", f"{cid} regressed on the compliant fixture")

    @unittest.skipUnless(HAVE_FFMPEG, "ffmpeg/ffprobe not installed")
    def test_c9_rejects_wrong_aspect(self):
        make_video(VIDEO, width=1920, height=1080)   # landscape
        try:
            report, _ = run_gate("_selftest")
            self.assertEqual(verdicts(report)["C9"], "FAIL", "16:9 must be rejected")
        finally:
            VIDEO.unlink(missing_ok=True)

    @unittest.skipUnless(HAVE_FFMPEG, "ffmpeg/ffprobe not installed")
    def test_c9_rejects_overlong(self):
        make_video(VIDEO, seconds=75)                # past the 50s ceiling
        try:
            report, _ = run_gate("_selftest")
            self.assertEqual(verdicts(report)["C9"], "FAIL", "75s must be rejected")
        finally:
            VIDEO.unlink(missing_ok=True)


class TestNonCompliantEpisode(GateTestBase):
    """Seed one violation per check and assert the gate catches each. If any of
    these starts passing, the gate has silently stopped protecting the channel."""

    def build_negative(self):
        shutil.copytree(FIXTURE, NEGATIVE)

        ev = json.loads((NEGATIVE / "evidence.json").read_text())
        ev["artifact"]["path"] = "assets/does-not-exist.png"      # C1
        ev["claims"][0]["sources"] = ev["claims"][0]["sources"][:1]  # C2
        (NEGATIVE / "evidence.json").write_text(json.dumps(ev))

        plan = json.loads((NEGATIVE / "scene_plan.json").read_text())
        plan["scenes"][0].pop("citation", None)                   # C3
        (NEGATIVE / "scene_plan.json").write_text(json.dumps(plan))

        (NEGATIVE / "assets" / "unlicensed-clip.mp4").write_text("stray")  # C4

        pkg = json.loads((NEGATIVE / "packaging.json").read_text())
        pkg["ai_disclosure"] = False                              # C5
        pkg["privacy_status"] = "public"                          # C10
        (NEGATIVE / "packaging.json").write_text(json.dumps(pkg))

        # C7: an exact structural copy of the fixture script, plus C8 language.
        script = (NEGATIVE / "script.md").read_text()
        script += "\nThis is guaranteed return territory and the Republican tariff is to blame.\n"
        (NEGATIVE / "script.md").write_text(script)

    def test_every_violation_is_caught(self):
        self.build_negative()
        report, _ = run_gate("_negtest")
        v = verdicts(report)
        expected_failures = {
            "C1": "missing research artifact",
            "C2": "under-sourced claim",
            "C3": "uncited price scene",
            "C4": "unlicensed asset",
            "C5": "AI disclosure off",
            "C7": "templated script",
            "C8": "partisan + financial-advice language",
            "C10": "public upload",
        }
        for cid, why in expected_failures.items():
            self.assertEqual(v[cid], "FAIL", f"{cid} did not catch: {why}")
        self.assertEqual(report["verdict"], "FAIL")

    def test_failures_route_to_owning_agent(self):
        self.build_negative()
        report, _ = run_gate("_negtest")
        owners = report["owner_to_fix"]
        self.assertEqual(owners["C2"], "trend-archaeologist")
        self.assertEqual(owners["C4"], "archive-sourcer")
        self.assertEqual(owners["C7"], "script-editor")
        for cid in report["blocking"]:
            self.assertIn(cid, owners, f"{cid} blocks but names no owner to fix it")

    def test_disallowed_license_is_rejected(self):
        self.build_negative()
        lic = json.loads((NEGATIVE / "licenses.json").read_text())
        lic.append({
            "file": "assets/unlicensed-clip.mp4",
            "source_url": "https://youtube.com/watch?v=whatever",
            "license": "all-rights-reserved",
            "attribution": "n/a",
            "used_for": "should never render",
        })
        (NEGATIVE / "licenses.json").write_text(json.dumps(lic))
        report, _ = run_gate("_negtest")
        self.assertEqual(verdicts(report)["C4"], "FAIL",
                         "a recorded but disallowed license must still fail")


class TestThroughputCap(GateTestBase):
    """C6 caps the channel at 2 published/day. Raising throughput is the single
    behaviour that got 16 channels deleted this year — see docs/05-compliance.md."""

    def test_cap_blocks_third_publish_in_24h(self):
        import datetime as dt
        now = dt.datetime.now(dt.timezone.utc)
        PUBLISH_LOG.parent.mkdir(parents=True, exist_ok=True)
        PUBLISH_LOG.write_text(json.dumps([
            {"slug": "a", "published_at": (now - dt.timedelta(hours=2)).isoformat()},
            {"slug": "b", "published_at": (now - dt.timedelta(hours=5)).isoformat()},
        ]))
        report, _ = run_gate("_selftest")
        self.assertEqual(verdicts(report)["C6"], "FAIL", "3rd publish in 24h must be blocked")

    def test_stale_entries_do_not_count(self):
        import datetime as dt
        now = dt.datetime.now(dt.timezone.utc)
        PUBLISH_LOG.write_text(json.dumps([
            {"slug": "a", "published_at": (now - dt.timedelta(hours=30)).isoformat()},
            {"slug": "b", "published_at": (now - dt.timedelta(days=4)).isoformat()},
        ]))
        report, _ = run_gate("_selftest")
        self.assertEqual(verdicts(report)["C6"], "PASS", "entries older than 24h must not count")


class TestNoBypass(unittest.TestCase):
    """docs/05-compliance.md promises there is no override. Assert the code keeps
    that promise — a bypass added later would make every PASS meaningless."""

    def test_no_bypass_flag_registered(self):
        # Scan for argparse registrations and env-var reads, not prose — the
        # gate's own docstring mentions --force in order to say it doesn't exist.
        source = GATE.read_text()
        registered = set(re.findall(r"add_argument\(\s*[\"'](--[\w-]+)", source))
        for bypass in ("--force", "--skip", "--no-verify", "--override", "--yes"):
            self.assertNotIn(bypass, registered,
                             f"a bypass flag ({bypass}) was added to the gate")
        for env in ("SKIP_GATE", "GATE_BYPASS", "FORCE_PUBLISH"):
            self.assertNotIn(env, source, f"an env-var bypass ({env}) was added")

    def test_gate_accepts_only_expected_flags(self):
        source = GATE.read_text()
        registered = set(re.findall(r"add_argument\(\s*[\"'](--[\w-]+)", source))
        self.assertEqual(registered, {"--slug", "--require-pass"},
                         "the gate's interface changed; review it for a bypass")

    def test_require_pass_exits_nonzero_on_fail(self):
        VIDEO.unlink(missing_ok=True)
        proc = subprocess.run(
            [sys.executable, str(GATE), "--slug", "_selftest", "--require-pass"],
            capture_output=True, text=True, cwd=ROOT, timeout=180,
        )
        self.assertNotEqual(proc.returncode, 0,
                            "make publish must be blocked when the gate fails")


class TestRepoIntegrity(unittest.TestCase):
    def test_all_json_parses(self):
        skip = {"node_modules", ".git", "vendor", ".venv"}
        for path in ROOT.rglob("*.json"):
            if skip & set(path.parts):
                continue
            with self.subTest(file=str(path.relative_to(ROOT))):
                json.loads(path.read_text())

    def test_every_agent_has_frontmatter(self):
        agents = sorted((ROOT / ".claude" / "agents").glob("*.md"))
        self.assertGreaterEqual(len(agents), 14, "the studio is 14 agents")
        for a in agents:
            with self.subTest(agent=a.name):
                text = a.read_text()
                self.assertTrue(text.startswith("---\n"), "missing frontmatter")
                fm = text.split("---", 2)[1]
                self.assertIn("name:", fm)
                self.assertIn("description:", fm)
                self.assertIn(f"name: {a.stem}", fm, "frontmatter name must match filename")


if __name__ == "__main__":
    unittest.main(verbosity=2)
