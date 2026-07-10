"""Provenance and public-schema checks for symbolic roadmap output."""

from __future__ import annotations

import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from encoders.pipeline import ROADMAP_SYSTEMS, SYSTEM_PROVENANCE  # noqa: E402
from engine import compute_unified_signature  # noqa: E402
from report import generate_report  # noqa: E402


class SymbolicContractTests(unittest.TestCase):
    def test_every_runtime_source_id_has_a_human_readable_catalog_entry(self):
        path = os.path.join(ROOT, "docs", "symbolic-systems-provenance.md")
        with open(path, encoding="utf-8") as handle:
            catalog = handle.read()
        for metadata in SYSTEM_PROVENANCE.values():
            for source_id in metadata["source_ids"]:
                with self.subTest(source_id=source_id):
                    self.assertIn(f"`{source_id}`", catalog)

    def test_public_schema_exposes_the_symbolic_encoder_envelope(self):
        with open(os.path.join(ROOT, "schemas", "identity-signature.schema.json"), encoding="utf-8") as handle:
            schema = json.load(handle)
        envelope = schema["$defs"]["symbolic_encoder_envelope"]
        self.assertEqual(envelope["required"], ["system", "phase", "status", "interpretation_level", "provenance", "data"])
        self.assertEqual(envelope["properties"]["provenance"]["required"], ["manifest_version", "convention", "source_ids", "input_mode"])
        self.assertIn("encoders", schema["properties"])

    def test_long_report_explains_extension_scope_and_resonance_boundary(self):
        signature = compute_unified_signature({"id": "test:capt", "text": "CAPT"})
        report = generate_report(signature)
        self.assertIn("provenance-aware symbolic extensions", report["markdown"])
        self.assertIn("excluded from the composite resonance score", report["markdown"])

    def test_long_report_contains_an_untruncated_extension_registry(self):
        signature = compute_unified_signature({"id": "test:capt", "text": "CAPT"})
        markdown = generate_report(signature)["markdown"]
        self.assertIn("Complete computed data", markdown)
        for system in ROADMAP_SYSTEMS:
            with self.subTest(system=system):
                self.assertIn(system, markdown)

    def test_unified_signature_is_strict_json_serializable(self):
        signature = compute_unified_signature({"id": "test:unicode", "text": "محمد"})
        json.dumps(signature, ensure_ascii=False, allow_nan=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
