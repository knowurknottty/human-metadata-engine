"""Public report order, epistemic metadata, export safety, and replay checks."""

from __future__ import annotations

import os
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "webapp"), str(ROOT / "src")]

from server import analyze  # noqa: E402


class PublicReportStructureTests(unittest.TestCase):
    def test_magic_report_has_required_order_and_epistemic_contract(self):
        result = analyze({"name": "Kirk Evan Brown", "mode": "magic"})
        report = result["report"]
        headings = [
            "Identity and input summary",
            "Data quality and calculation coverage",
            "Plain-English overview",
            "Deterministic name calculations",
            "Astronomical birth-chart calculations",
            "Human Design or related derived systems",
            "User-supplied psychology",
            "Cross-system synthesis",
            "Agreements, tensions, and contradictions",
            "Provenance, limitations, and reproduction details",
        ]
        offsets = [report["markdown"].index(title) for title in headings]
        self.assertEqual(offsets, sorted(offsets))
        self.assertEqual(report["sections"], list(range(1, 11)))
        for section in report["section_metadata"]:
            self.assertEqual(
                set(section),
                {"section", "title", "category", "evidence_level", "confidence", "deterministic", "scientific_validation", "provenance", "limitations"},
            )
            self.assertTrue(section["provenance"])
            self.assertTrue(section["limitations"])

    def test_public_magic_report_avoids_legacy_overclaims_and_bulk_boilerplate(self):
        markdown = analyze({"name": "Kirk Evan Brown", "mode": "magic"})["report"]["markdown"]
        for unsupported in (
            "quantity of divine energy",
            "deep name in the Pythagorean-mystical sense",
            "reveals your destiny",
            "only empirically-grounded section",
            "far more often than chance would suggest",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)
        # The compact calculation report remains bounded; the requested long-form
        # reading is an explicit additional section, not repeated filler.
        base, narrative = markdown.split("## Human Metadata Narrative", 1)
        self.assertLess(len(base.split()), 1200)
        self.assertIn("The language of your name", narrative)
        self.assertIn("Your name-derived tarot archetype", narrative)
        self.assertIn("not a percentage of accuracy", markdown)

    def test_same_request_replays_identically_and_export_contains_versions(self):
        request = {"name": "Ada Lovelace", "aliases": ["Ada King"], "mode": "magic"}
        first = analyze(request)
        second = analyze(request)
        self.assertEqual(first, second)
        self.assertEqual(first["report"]["metadata"]["reproducibility_id"], first["input_hash"])
        for field in (
            "report_schema_version", "analysis_schema_version", "engine_version",
            "convention_set_version", "build_revision", "reproducibility_id",
        ):
            self.assertIn(field, first["report"]["metadata"])
        self.assertEqual(first["application_version"], "1.0.0")
        self.assertIn("# Human Metadata Engine Report — Ada Lovelace", first["report"]["markdown"])
        self.assertIn("Other names: **Ada King**", first["report"]["markdown"])

    def test_aliases_are_markdown_escaped_in_export(self):
        result = analyze({"name": "Ada Lovelace", "aliases": ["Ada *King*"], "mode": "data"})
        markdown = result["report"]["markdown"]
        self.assertIn("# Human Metadata Engine Data Report — Ada Lovelace", markdown)
        self.assertIn(r"Other names: **Ada \*King\***", markdown)

    def test_browser_markdown_renderer_escapes_before_formatting(self):
        script = (ROOT / "webapp" / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn("const inline = (s) => esc(s)", script)
        self.assertNotIn("innerHTML = STATE.result.report.markdown", script)


if __name__ == "__main__":
    unittest.main(verbosity=2)
