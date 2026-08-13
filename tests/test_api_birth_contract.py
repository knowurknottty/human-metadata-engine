"""Ensure the legacy API cannot silently discard birth information."""

from __future__ import annotations

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from api import _identity_from_encode_request  # noqa: E402


class APIBirthContractTests(unittest.TestCase):
    def canonical_birth(self):
        return {
            "year": 1985, "month": 6, "day": 15,
            "hour": 10, "minute": 30, "timezone_offset": -7,
            "location": "Portland, Oregon, USA", "lat": 45.5152,
            "lon": -122.6765, "time_accuracy": "provided",
        }

    def test_canonical_birth_object_reaches_engine_identity(self):
        identity = _identity_from_encode_request({"name": "Example", "birth": self.canonical_birth()})
        self.assertEqual(identity["birth"]["year"], 1985)
        self.assertEqual(identity["birth"]["time_accuracy"], "provided")

    def test_legacy_birth_fields_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "canonical 'birth' object"):
            _identity_from_encode_request({"name": "Example", "birth_date": "1985-06-15"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
