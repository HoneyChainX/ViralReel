"""The job queue is the remote attack surface — these tests are its lock.

config/jobs.yaml decides what a remote caller can make this machine do. The
suite below asserts two different things, and the second matters more:

  1. jobd's validator behaves (patterns enforced, no shell, no free text)
  2. the recipes we actually ship are safe — every parameter pattern in
     config/jobs.yaml is checked against real traversal and injection strings

So widening a pattern to `.*` for convenience fails CI instead of quietly
opening a shell to the internet.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    """Load by path, never via sys.path.

    Putting scripts/studio on sys.path shadows the stdlib `platform` module for
    everything imported afterwards. In a single-module run that looks harmless;
    under `unittest discover` it broke pydantic for the tests that load later,
    which silently SKIPPED the entire OAuth suite instead of failing. A guard
    that only watched shipped code missed it, so it now watches tests too.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        f"t_{name}", ROOT / "scripts" / "studio" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


jobd = _load("jobd")

# Values a hostile caller would try. None may ever satisfy a shipped pattern.
HOSTILE = [
    "../../etc/passwd", "..%2f..%2fetc", "/etc/shadow", "~/.ssh/id_rsa",
    "a; rm -rf /", "a && curl http://evil", "a | nc evil 1234", "a`whoami`",
    "a$(whoami)", "a\nrm -rf /", "a\x00b", "-rf", "--upload-file",
    "$(cat /etc/passwd)", "'; DROP TABLE jobs; --", "*", "?", "a b",
]


def write_recipes(tmp: Path, body: str) -> Path:
    p = tmp / "jobs.yaml"
    p.write_text(body)
    return p


class RecipeValidation(unittest.TestCase):
    """Malformed recipes must fail at load, not at run."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_undeclared_slot_rejected(self):
        p = write_recipes(self.tmp, """
version: 1
jobs:
  - id: bad
    argv: ["echo", "{nope}"]
""")
        with self.assertRaises(jobd.RecipeError):
            jobd.load_recipes(p)

    def test_param_without_pattern_rejected(self):
        p = write_recipes(self.tmp, """
version: 1
jobs:
  - id: bad
    argv: ["echo", "{x}"]
    params:
      - name: x
""")
        with self.assertRaises(jobd.RecipeError):
            jobd.load_recipes(p)

    def test_placeholder_command_rejected(self):
        """argv[0] parameterised would be arbitrary execution wearing a costume."""
        p = write_recipes(self.tmp, """
version: 1
jobs:
  - id: bad
    argv: ["{cmd}", "hello"]
    params:
      - name: cmd
        pattern: "^.*$"
""")
        with self.assertRaises(jobd.RecipeError):
            jobd.load_recipes(p)

    def test_empty_argv_rejected(self):
        p = write_recipes(self.tmp, """
version: 1
jobs:
  - id: bad
    argv: []
""")
        with self.assertRaises(jobd.RecipeError):
            jobd.load_recipes(p)

    def test_no_jobs_rejected(self):
        p = write_recipes(self.tmp, "version: 1\njobs: []\n")
        with self.assertRaises(jobd.RecipeError):
            jobd.load_recipes(p)


class ArgvBuilding(unittest.TestCase):
    RECIPE = {
        "id": "demo",
        "argv": ["echo", "--name", "{name}", "--opt", "{opt}"],
        "params": [
            {"name": "name", "pattern": r"^[a-z]{1,10}$"},
            {"name": "opt", "pattern": r"^[0-9]+$", "required": False},
        ],
    }

    def test_valid_substitution(self):
        self.assertEqual(
            jobd.build_argv(self.RECIPE, {"name": "keeper", "opt": "9"}),
            ["echo", "--name", "keeper", "--opt", "9"])

    def test_optional_param_drops_its_token(self):
        """A missing optional must not leave a dangling flag with no value."""
        self.assertEqual(jobd.build_argv(self.RECIPE, {"name": "keeper"}),
                         ["echo", "--name", "keeper", "--opt"])

    def test_missing_required_rejected(self):
        with self.assertRaises(jobd.RecipeError):
            jobd.build_argv(self.RECIPE, {})

    def test_unknown_param_rejected(self):
        with self.assertRaises(jobd.RecipeError):
            jobd.build_argv(self.RECIPE, {"name": "keeper", "sneaky": "1"})

    def test_default_applied(self):
        r = {"id": "d", "argv": ["echo", "{x}"],
             "params": [{"name": "x", "pattern": r"^[a-z]+$", "default": "hi",
                         "required": False}]}
        self.assertEqual(jobd.build_argv(r, {}), ["echo", "hi"])

    def test_hostile_values_rejected(self):
        for bad in HOSTILE:
            with self.subTest(value=bad):
                with self.assertRaises(jobd.RecipeError):
                    jobd.build_argv(self.RECIPE, {"name": bad})


class ShippedRecipes(unittest.TestCase):
    """The real config/jobs.yaml — the file that is actually exposed."""

    @classmethod
    def setUpClass(cls):
        cls.recipes = jobd.load_recipes(ROOT / "config" / "jobs.yaml")

    def test_loads(self):
        self.assertGreater(len(self.recipes), 0)

    def test_every_command_is_literal(self):
        for rid, r in self.recipes.items():
            with self.subTest(job=rid):
                self.assertNotIn("{", r["argv"][0])

    def test_no_shell_interpreter_recipes(self):
        """`bash -c` / `sh -c` would re-open the door the allowlist closes."""
        for rid, r in self.recipes.items():
            with self.subTest(job=rid):
                self.assertNotIn("-c", r["argv"][:2],
                                 f"{rid} runs an inline shell command")

    def test_every_param_rejects_hostile_input(self):
        for rid, r in self.recipes.items():
            for p in r.get("params", []):
                for bad in HOSTILE:
                    with self.subTest(job=rid, param=p["name"], value=bad):
                        args = {q["name"]: q.get("default", "core")
                                for q in r.get("params", [])
                                if q.get("required", True) or "default" in q}
                        args[p["name"]] = bad
                        with self.assertRaises(jobd.RecipeError):
                            jobd.build_argv(r, args)

    def test_no_recipe_writes_to_a_remote(self):
        """Distribution stays manual-first (DECISIONS D1)."""
        forbidden = {"push", "publish", "upload"}
        for rid, r in self.recipes.items():
            with self.subTest(job=rid):
                tokens = {t.strip("-").lower() for t in r["argv"]}
                self.assertFalse(tokens & forbidden,
                                 f"{rid} contains a remote-write verb")

    def test_timeouts_are_bounded(self):
        for rid, r in self.recipes.items():
            with self.subTest(job=rid):
                self.assertLessEqual(int(r.get("timeout", 0)), 86400,
                                     f"{rid} may run longer than a day")


class Lifecycle(unittest.TestCase):
    """Queue → claim → run → terminal state, against a temp database."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self._saved = (jobd.VAR, jobd.DB_PATH, jobd.LOG_DIR, jobd.RECIPES)
        jobd.VAR = self.tmp
        jobd.DB_PATH = self.tmp / "jobs.db"
        jobd.LOG_DIR = self.tmp / "logs"
        jobd.RECIPES = write_recipes(self.tmp, """
version: 1
jobs:
  - id: hello
    argv: ["echo", "hello-{who}"]
    params:
      - name: who
        pattern: "^[a-z]+$"
    timeout: 30
  - id: boom
    argv: ["false"]
    timeout: 30
  - id: missing
    argv: ["definitely-not-a-real-command-xyz"]
    timeout: 30
""")

    def tearDown(self):
        jobd.VAR, jobd.DB_PATH, jobd.LOG_DIR, jobd.RECIPES = self._saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_success_path(self):
        jid = jobd.enqueue("hello", {"who": "world"})
        jobd.worker(once=True)
        job = jobd.get(jid)
        self.assertEqual(job["state"], jobd.SUCCEEDED)
        self.assertEqual(job["exit_code"], 0)
        self.assertIn("hello-world", jobd.tail_log(jid))

    def test_failure_recorded(self):
        jid = jobd.enqueue("boom", {})
        jobd.worker(once=True)
        self.assertEqual(jobd.get(jid)["state"], jobd.FAILED)

    def test_missing_binary_is_failure_not_crash(self):
        jid = jobd.enqueue("missing", {})
        jobd.worker(once=True)
        job = jobd.get(jid)
        self.assertEqual(job["state"], jobd.FAILED)
        self.assertIn("could not start", job["note"])

    def test_unknown_recipe_rejected(self):
        with self.assertRaises(jobd.RecipeError):
            jobd.enqueue("nope", {})

    def test_cancel_before_start(self):
        jid = jobd.enqueue("hello", {"who": "x"})
        jobd.cancel(jid)
        self.assertEqual(jobd.get(jid)["state"], jobd.CANCELLED)
        # A cancelled job must not be picked up afterwards.
        jobd.worker(once=True)
        self.assertEqual(jobd.get(jid)["state"], jobd.CANCELLED)

    def test_claim_is_exclusive(self):
        jid = jobd.enqueue("hello", {"who": "a"})
        first = jobd._claim()
        second = jobd._claim()
        self.assertEqual(first["id"], jid)
        self.assertIsNone(second, "a second worker claimed the same job")

    def test_reap_clears_orphans(self):
        jid = jobd.enqueue("hello", {"who": "a"})
        jobd._claim()                       # now RUNNING, with no live pid
        self.assertEqual(jobd.get(jid)["state"], jobd.RUNNING)
        self.assertEqual(jobd.reap(), [jid])
        self.assertEqual(jobd.get(jid)["state"], jobd.INTERRUPTED)

    def test_argv_is_persisted_as_a_list(self):
        """Stored as JSON so nothing can re-parse it into a shell string."""
        jid = jobd.enqueue("hello", {"who": "x"})
        self.assertIsInstance(json.loads(jobd.get(jid)["argv"]), list)


if __name__ == "__main__":
    unittest.main()
