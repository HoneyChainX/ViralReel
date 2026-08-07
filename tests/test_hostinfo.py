"""Host profiling, and the import hazard that comes with this repo's layout.

scripts/studio/platform.py sits next to every other studio module and shares its
name with the stdlib. Any code that reaches those modules by putting their
directory on sys.path shadows `platform` for everything imported afterwards —
which is how a working MCP server turns into "cannot import name 'BaseModel'
from 'pydantic'", an error that names neither culprit. The guards below keep
that from coming back.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "scripts" / "studio"


def load(name: str):
    """Load a studio module the safe way — by path, never via sys.path."""
    spec = importlib.util.spec_from_file_location(f"t_{name}", STUDIO / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


hostinfo = load("hostinfo")


class Profile(unittest.TestCase):
    def test_collect_shape(self):
        p = hostinfo.collect()
        for key in ("os", "cpu", "memory", "disk", "gpu", "tools",
                    "services", "readiness"):
            self.assertIn(key, p)

    def test_json_serialisable(self):
        """The MCP status tool and --json both depend on this."""
        import json
        json.dumps(hostinfo.collect())

    def test_os_detection_does_not_use_stdlib_platform(self):
        """hostinfo must survive being run from inside scripts/studio/."""
        self.assertIn(hostinfo.detect_os()["system"], ("Linux", "Darwin", "Windows"))

    def test_readiness_blocks_on_missing_tools(self):
        profile = {
            "os": {"posix_stack_ok": True},
            "cpu": {"count": 8},
            "memory": {"total_gb": 32},
            "disk": {"free_gb": 500},
            "gpu": {"present": True, "gpus": []},
            "tools": {},                       # nothing installed
            "services": {"systemd": True, "units": {}},
        }
        r = hostinfo.readiness(profile)
        self.assertFalse(r["ready"])
        for tool in ("git", "python3", "node", "ffmpeg"):
            self.assertTrue(any(tool in b for b in r["blocking"]),
                            f"missing {tool} should block")

    def test_readiness_blocks_native_windows(self):
        """The stack is POSIX; native Windows must be refused, not warned about."""
        profile = {
            "os": {"posix_stack_ok": False},
            "cpu": {"count": 8}, "memory": {"total_gb": 32},
            "disk": {"free_gb": 500}, "gpu": {"present": False},
            "tools": {t: {"present": True, "libvmaf": True}
                      for t in ("git", "python3", "node", "ffmpeg")},
            "services": {"systemd": True, "units": {}},
        }
        r = hostinfo.readiness(profile)
        self.assertFalse(r["ready"])
        self.assertTrue(any("WSL2" in b for b in r["blocking"]))

    def test_low_disk_blocks_but_medium_disk_only_warns(self):
        def profile_with(free_gb):
            return {
                "os": {"posix_stack_ok": True},
                "cpu": {"count": 8}, "memory": {"total_gb": 32},
                "disk": {"free_gb": free_gb}, "gpu": {"present": True, "gpus": []},
                "tools": {t: {"present": True, "libvmaf": True}
                          for t in ("git", "python3", "node", "ffmpeg")},
                "services": {"systemd": True, "units": {}},
            }
        self.assertFalse(hostinfo.readiness(profile_with(2))["ready"])
        medium = hostinfo.readiness(profile_with(25))
        self.assertTrue(medium["ready"])
        self.assertTrue(any("vendor install" in w for w in medium["warnings"]))

    def test_missing_libvmaf_warns(self):
        profile = {
            "os": {"posix_stack_ok": True},
            "cpu": {"count": 8}, "memory": {"total_gb": 32},
            "disk": {"free_gb": 500}, "gpu": {"present": True, "gpus": []},
            "tools": {t: {"present": True} for t in ("git", "python3", "node", "ffmpeg")},
            "services": {"systemd": True, "units": {}},
        }
        r = hostinfo.readiness(profile)
        self.assertTrue(any("libvmaf" in w for w in r["warnings"]))


class ImportHygiene(unittest.TestCase):
    """The landmine guards."""

    def test_studio_dir_shadows_stdlib_platform(self):
        """Documents the hazard: if this ever stops being true, the guards below
        can be relaxed. Until then, nothing may put this directory on sys.path."""
        self.assertTrue((STUDIO / "platform.py").is_file())

    def test_no_shipped_module_puts_studio_on_syspath(self):
        """Parsed, not grepped — a docstring explaining the hazard is not a
        violation of it."""
        import ast

        offenders = []
        # Tests are NOT exempt. One of ours mutated sys.path, which shadowed
        # stdlib `platform`, which broke pydantic for every module imported
        # after it — and the visible symptom was the OAuth suite silently
        # skipping rather than anything failing.
        for py in (list((ROOT / "server").rglob("*.py")) + list(STUDIO.glob("*.py"))
                   + list((ROOT / "tests").glob("*.py"))):
            try:
                tree = ast.parse(py.read_text(errors="ignore"))
            except SyntaxError as e:
                offenders.append(f"{py.relative_to(ROOT)}: does not parse: {e}")
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                fn = node.func
                if not isinstance(fn, ast.Attribute) or fn.attr not in ("insert", "append"):
                    continue
                target = fn.value
                if (isinstance(target, ast.Attribute) and target.attr == "path"
                        and isinstance(target.value, ast.Name) and target.value.id == "sys"):
                    offenders.append(
                        f"{py.relative_to(ROOT)}:{node.lineno}: mutates sys.path")
        self.assertEqual(offenders, [],
                         "load studio modules by path (importlib), never by "
                         "mutating sys.path:\n" + "\n".join(offenders))

    def test_hostinfo_runs_from_inside_its_own_directory(self):
        """The worst case: cwd is scripts/studio, so '' on sys.path shadows
        stdlib platform. hostinfo must still work."""
        r = subprocess.run([sys.executable, "hostinfo.py", "--json"],
                           cwd=STUDIO, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-500:])
        self.assertIn('"readiness"', r.stdout)

    def test_jobd_runs_from_inside_its_own_directory(self):
        r = subprocess.run([sys.executable, "jobd.py", "recipes"],
                           cwd=STUDIO, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-500:])
        self.assertIn("film-render", r.stdout)


if __name__ == "__main__":
    unittest.main()
