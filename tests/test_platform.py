"""Platform manifest invariants.

These tests protect the studio-platform doctrine (docs/10, DECISIONS D8) the same way
test_gate.py protects the publish gate: mechanically. If one fails, the manifest is
attempting something the platform forbids — fix the manifest, never the test.
"""
import pathlib
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config" / "platform.yaml"


class TestPlatformManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = yaml.safe_load(MANIFEST.read_text())
        cls.modules = cls.data["modules"]

    def test_manifest_parses_and_has_modules(self):
        self.assertGreaterEqual(len(self.modules), 10)

    def test_module_ids_unique(self):
        ids = [m["id"] for m in self.modules]
        self.assertEqual(len(ids), len(set(ids)), "duplicate module ids")

    def test_required_keys_present(self):
        for m in self.modules:
            for key in ("id", "repo", "profile", "role", "license", "cost", "gpu"):
                self.assertIn(key, m, f"{m.get('id')}: missing '{key}'")

    def test_profiles_are_declared(self):
        declared = set(self.data["profiles"])
        for m in self.modules:
            self.assertIn(m["profile"], declared,
                          f"{m['id']}: profile '{m['profile']}' not declared")

    def test_cost_and_gpu_vocabulary(self):
        for m in self.modules:
            self.assertIn(m["cost"], {"free", "freemium", "paid"}, m["id"])
            self.assertIn(m["gpu"], {"none", "optional", "required"}, m["id"])

    def test_paid_modules_are_disabled(self):
        """The load-bearing invariant: a paid module can never ship enabled.

        Enabling one is a per-project founder edit (DECISIONS D8). The runtime loader
        (scripts/studio/platform.py) enforces this too; this test keeps the invariant
        even if that loader is ever rewritten.
        """
        for m in self.modules:
            if m["cost"] == "paid":
                self.assertFalse(m.get("enabled", False),
                                 f"{m['id']} is paid AND enabled — forbidden")

    def test_desktop_modules_have_no_install_cmd(self):
        for m in self.modules:
            if m.get("install") == "desktop":
                self.assertNotIn("install_cmd", m,
                                 f"{m['id']}: desktop modules are human-installed")

    def test_doctor_check_shapes(self):
        for m in self.modules:
            for c in m.get("doctor", []):
                self.assertIn(c.get("type"), {"dir", "file", "cmd"},
                              f"{m['id']}: bad doctor check type {c}")
                key = {"dir": "path", "file": "path", "cmd": "run"}[c["type"]]
                self.assertIn(key, c, f"{m['id']}: doctor check missing '{key}'")

    def test_loader_rejects_enabled_paid_module(self):
        """The runtime loader must hard-fail on a paid+enabled manifest, not warn."""
        import copy
        import importlib.util
        import tempfile

        spec = importlib.util.spec_from_file_location(
            "studio_platform", ROOT / "scripts" / "studio" / "platform.py")
        sp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sp)

        bad = copy.deepcopy(self.data)
        for m in bad["modules"]:
            if m["cost"] == "paid":
                m["enabled"] = True
                break
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            yaml.safe_dump(bad, f)
        original = sp.MANIFEST
        try:
            sp.MANIFEST = pathlib.Path(f.name)
            with self.assertRaises(SystemExit):
                sp.load_manifest()
        finally:
            sp.MANIFEST = original
            pathlib.Path(f.name).unlink(missing_ok=True)


class TestRalphGuardrails(unittest.TestCase):
    """The loop harness must keep its protections. Same fix-the-code rule applies."""

    def setUp(self):
        self.runner = (ROOT / "ralph" / "ralph.sh").read_text()

    def test_runner_protects_the_gate(self):
        for path in ("scripts/gate.py", "tests/", "docs/05-compliance.md"):
            self.assertIn(path, self.runner, f"ralph.sh no longer protects {path}")

    def test_runner_is_bounded(self):
        self.assertIn("MAX_ITER", self.runner)
        self.assertNotIn("while :", self.runner, "unbounded loop reintroduced")

    def test_every_job_forbids_gate_edits(self):
        for prompt in (ROOT / "ralph" / "jobs").glob("*/PROMPT.md"):
            text = prompt.read_text()
            self.assertIn("scripts/gate.py", text,
                          f"{prompt}: job prompt lost the gate prohibition")


if __name__ == "__main__":
    unittest.main()
