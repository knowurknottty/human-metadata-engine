"""Runtime packaging contract for mandatory Swiss Ephemeris support."""

from __future__ import annotations

import os
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class EphemerisPackagingTests(unittest.TestCase):
    def test_runtime_configs_require_a_pinned_pyswisseph_build(self):
        with open(os.path.join(ROOT, "requirements.txt"), encoding="utf-8") as handle:
            requirements = handle.read()
        with open(os.path.join(ROOT, "Dockerfile"), encoding="utf-8") as handle:
            dockerfile = handle.read()
        with open(os.path.join(ROOT, "deploy.sh"), encoding="utf-8") as handle:
            deploy = handle.read()
        with open(os.path.join(ROOT, ".github", "workflows", "fly-deploy.yml"), encoding="utf-8") as handle:
            workflow = handle.read()

        self.assertIn("pyswisseph==2.10.3.2", requirements)
        self.assertIn("AS ephemeris-builder", dockerfile)
        self.assertIn("pip wheel", dockerfile)
        self.assertIn("COPY --from=ephemeris-builder", dockerfile)
        self.assertIn("pip install --no-cache-dir /wheels/*", dockerfile)
        self.assertIn("pip install --require-hashes --no-cache-dir -r requirements.txt", deploy)
        self.assertIn("pip install --require-hashes -r requirements.txt", workflow)
        self.assertIn("tools/run_tests.py", deploy)
        self.assertIn("tools/run_tests.py", workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
