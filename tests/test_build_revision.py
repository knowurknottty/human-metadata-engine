"""Ensure persisted reference artifacts retain the deployed build revision."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from build_famous_people_index import git_revision  # noqa: E402


class BuildRevisionTests(unittest.TestCase):
    def test_environment_revision_overrides_missing_git_metadata(self):
        with patch.dict(os.environ, {"HME_BUILD_REVISION": "reviewed-sha"}):
            self.assertEqual(git_revision(), "reviewed-sha")


if __name__ == "__main__":
    unittest.main(verbosity=2)
