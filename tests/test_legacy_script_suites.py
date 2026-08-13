"""Expose legacy executable regression suites to unittest and pytest."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_SUITES = (
    "test_analytics.py",
    "test_claim_compiler.py",
    "test_coherence_gate.py",
    "test_hardening_regression.py",
    "test_sigil.py",
)


class LegacyScriptSuiteTests(unittest.TestCase):
    def _run(self, filename: str) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join([
            str(ROOT / "src"), str(ROOT / "webapp"), env.get("PYTHONPATH", "")
        ])
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tests" / filename)],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"{filename} failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}",
        )


def _make_test(filename: str):
    def test(self):
        self._run(filename)

    test.__name__ = "test_" + filename.removeprefix("test_").removesuffix(".py")
    return test


for _filename in SCRIPT_SUITES:
    setattr(LegacyScriptSuiteTests, "test_" + _filename[5:-3], _make_test(_filename))


if __name__ == "__main__":
    unittest.main(verbosity=2)
