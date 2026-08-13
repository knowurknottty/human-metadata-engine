"""Public-boundary tests for the validated Human Design adapter."""

from __future__ import annotations

import json
import os
import sys
import unittest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "webapp"))

from engine import compute_unified_signature  # noqa: E402
from server import _disable_unvalidated_human_design, analyze  # noqa: E402
from true_human_design.astronomy import swe  # noqa: E402
from true_human_design.public_adapter import (  # noqa: E402
    calculate_public_human_design,
    unavailable_human_design,
)


BIRTH = {
    "year": 1982,
    "month": 2,
    "day": 4,
    "hour": 1,
    "minute": 42,
    "timezone_offset": -7,
    "location": "private location",
    "lat": 41.2680,
    "lon": -110.9408,
    "time_accuracy": "exact",
}


class AdapterContractTests(unittest.TestCase):
    def test_uncertain_time_is_withheld_without_guessing(self):
        result = unavailable_human_design({**BIRTH, "time_accuracy": "unknown"})
        self.assertFalse(result["available"])
        self.assertEqual(result["status"], "unavailable_uncertain_birth_time")
        self.assertNotIn("type", result)
        self.assertIn("noon", result["reason"])

    def test_fixed_offset_format_is_deterministic(self):
        from true_human_design.public_adapter import _fixed_timezone_name
        self.assertEqual(_fixed_timezone_name(-7), "UTC-07:00")
        self.assertEqual(_fixed_timezone_name(5.5), "UTC+05:30")

    def test_injected_public_engine_is_not_replaced_by_legacy_stub(self):
        def fake_hd(birth, *, subject_id=None):
            return {
                "available": True,
                "status": "provisional_calculation",
                "type": "Projector",
                "channels": [],
                "centers": [],
                "gates": [],
                "profile": [1, 3],
            }

        signature = compute_unified_signature(
            {"id": "test:adapter", "text": "Adapter", "birth": BIRTH},
            human_design_fn=fake_hd,
            snapshot_fn=None,
        )
        _disable_unvalidated_human_design(signature, {"text": "Adapter"})
        self.assertTrue(signature["encoders"]["human_design"]["available"])
        self.assertEqual(signature["encoders"]["human_design"]["status"], "provisional_calculation")
        self.assertEqual(signature["invalidated_dimensions"]["human_design"], 0)


@unittest.skipUnless(swe is not None, "pyswisseph is required for ephemeris adapter tests")
class EphemerisAdapterTests(unittest.TestCase):
    def test_adapter_returns_a_redacted_provenance_labelled_chart(self):
        result = calculate_public_human_design(BIRTH, subject_id="private-anchor")
        self.assertTrue(result["available"])
        self.assertEqual(result["status"], "provisional_calculation")
        self.assertEqual(result["calculation_standard"], "true-human-design-core-v1")
        self.assertEqual(result["timezone_provenance"], "provided_utc_offset")
        self.assertIsNone(result["confidence"])
        serialized = json.dumps(result, sort_keys=True)
        self.assertNotIn("private location", serialized)
        self.assertNotIn("41.268", serialized)
        self.assertNotIn("private-anchor", serialized)
        self.assertNotIn("America/Denver", serialized)
        self.assertIn("calculation_hash", result["true_engine"]["ledger"])

    def test_iana_timezone_is_kept_as_explicit_provenance(self):
        result = calculate_public_human_design({**BIRTH, "timezone_name": "America/Denver"})
        self.assertEqual(result["timezone_provenance"], "explicit_iana")

    def test_public_api_uses_core_chart_and_does_not_invent_legacy_authority(self):
        result = analyze({"name": "Kirk Evan Brown", "birth": BIRTH, "mode": "magic"})
        human_design = result["signature"]["encoders"]["human_design"]
        self.assertTrue(human_design["available"])
        self.assertEqual(human_design["calculation_standard"], "true-human-design-core-v1")
        self.assertEqual(human_design["status"], "provisional_calculation")
        markdown = result["report"]["markdown"]
        self.assertNotIn("the promised signature state", markdown.lower())
        self.assertNotIn("88-days-prior", markdown)


if __name__ == "__main__":
    unittest.main(verbosity=2)
