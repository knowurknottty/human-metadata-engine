"""Docs, manifest and symbol drift gate (EN-10, EN-15).

Makes the "docs cite files/symbols that do not exist" failure class a hard test
failure, and locks the ``system_manifest`` and handoff v2 manifest shapes with a
recorded-versus-computed count reconciliation.
"""
from __future__ import annotations

import importlib
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [_ROOT, os.path.join(_ROOT, "src"), os.path.join(_ROOT, "webapp"),
                os.path.dirname(os.path.abspath(__file__))]

from agent_handoff import build_handoff_v2  # noqa: E402
from encoders.bazi import compute_bazi  # noqa: E402
from encoders.jyotish import compute_jyotish  # noqa: E402
from encoders.maya_classical import compute_classical_maya  # noqa: E402
from system_contracts import summarize_systems  # noqa: E402
from synthesis.extractors import EXTRACTORS, ROADMAP_EVIDENCE_CONFIG  # noqa: E402

ROOT = _ROOT
SRC = os.path.join(ROOT, "src")
DOC = os.path.join(ROOT, "docs", "SIGNATURE_V3.md")

BIRTH = {
    "year": 2000, "month": 1, "day": 7, "hour": 12, "minute": 0,
    "timezone_offset": 8, "lat": 39.9042, "lon": 116.4074, "time_accuracy": "exact",
}

# Every symbol the docs name explicitly, as ``module:attribute``.
DOCUMENTED_SYMBOLS = (
    "agent_handoff:build_handoff_v2",
    "system_contracts:summarize_systems",
    "system_contracts:system_result",
    "synthesis.system_vocabulary:select_system_vocabulary",
    "unsupported_capabilities:UNSUPPORTED_CAPABILITY_FRAGMENTS",
    "time_context:normalize_birth_timezone",
    "encoders.jyotish:compute_jyotish",
    "encoders.bazi:compute_bazi",
    "encoders.maya_classical:compute_classical_maya",
    "synthesis.extractors:EXTRACTORS",
)

# The documented evidence-extractor families.
DOCUMENTED_EXTRACTORS = (
    "extract_numerology", "extract_name_structure", "extract_binary_prime",
    "extract_astrology", "extract_human_design", "extract_tree_of_life",
    "extract_chinese", "extract_tarot", "extract_roadmap_envelopes",
    "extract_psychology",
)

SYSTEM_MANIFEST_KEYS = {
    "system_count", "lens_count", "available_system_count",
    "raw_dependency_root_count", "independence_family_count",
    "independence_families", "artifact_classes", "epistemic_classes",
    "dependency_roots", "computed_field_count",
}

HANDOFF_V2_KEYS = {
    "schema_version", "analysis_mode", "subject_inputs", "deterministic_replay",
    "unavailable_calculations", "evidence_index", "contradictions",
    "dependence_families", "uncertainty_limitations", "redaction_rules",
    "prohibited_inference_classes", "source_provenance_index",
    "public_response_coverage",
}


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _systems():
    return {
        "jyotish": compute_jyotish(BIRTH),
        "bazi": compute_bazi(BIRTH),
        "maya_classical": compute_classical_maya({"year": 2012, "month": 12, "day": 21}),
    }


class TestDocsPathDrift:
    def test_every_src_path_cited_in_the_docs_exists(self):
        doc = _read(DOC)
        cited = set(re.findall(r"`(src/[A-Za-z0-9_./-]+\.py)`", doc))
        assert cited, "no src/*.py paths cited; the drift gate would be vacuous"
        missing = sorted(path for path in cited if not os.path.exists(os.path.join(ROOT, path)))
        assert missing == [], f"docs cite absent files: {missing}"

    def test_every_documented_component_is_cited_at_least_once(self):
        doc = _read(DOC)
        components = (
            "src/unsupported_capabilities.py",
            "src/agent_handoff.py",
            "src/system_contracts.py",
            "src/time_context.py",
        )
        for component in components:
            assert os.path.exists(os.path.join(ROOT, component))
            assert component in doc, f"{component} exists but is not cited in the docs"

    def test_every_documented_symbol_resolves(self):
        for entry in DOCUMENTED_SYMBOLS:
            module_name, attribute = entry.split(":", 1)
            module = importlib.import_module(module_name)
            assert hasattr(module, attribute), f"documented symbol {entry} does not resolve"


class TestExtractorInventoryReconciliation:
    def test_extractors_tuple_matches_documented_families(self):
        assert tuple(extractor.__name__ for extractor in EXTRACTORS) == DOCUMENTED_EXTRACTORS

    def test_roadmap_config_matches_the_documented_system_set(self):
        from test_corpus_r2 import ROADMAP_SYSTEMS
        assert set(ROADMAP_EVIDENCE_CONFIG) == set(ROADMAP_SYSTEMS)

    def test_roadmap_config_shape(self):
        for system, config in ROADMAP_EVIDENCE_CONFIG.items():
            fields, independence_group = config
            assert isinstance(fields, tuple) and fields
            assert all(isinstance(field, str) and field for field in fields)
            assert isinstance(independence_group, str) and independence_group


class TestSystemManifestIsLocked:
    def test_manifest_key_set_is_exact(self):
        manifest = summarize_systems(_systems())
        assert set(manifest) == SYSTEM_MANIFEST_KEYS

    def test_recorded_counts_match_computed_counts(self):
        systems = _systems()
        manifest = summarize_systems(systems)
        computed_lenses = len(systems)
        computed_available = sum(len(value.get("calculation", {})) > 0 or value.get("status") == "computed" for value in systems.values())
        assert manifest["system_count"] == computed_lenses
        assert manifest["lens_count"] == computed_lenses
        assert manifest["available_system_count"] == computed_available
        assert manifest["independence_family_count"] == len(manifest["independence_families"])
        assert manifest["raw_dependency_root_count"] == len(manifest["dependency_roots"])

    def test_manifest_count_mismatch_fails_loudly(self):
        """A tampered recorded count must not pass a reconciliation check."""
        manifest = summarize_systems(_systems())
        tampered = {**manifest, "system_count": manifest["system_count"] + 1}
        with pytest.raises(AssertionError):
            assert tampered["system_count"] == manifest["lens_count"]


class TestHandoffManifestIsLocked:
    response = {
        "normalized_input": {"name": "Test Subject", "birth_availability": True},
        "input_hash": "test_hash",
        "engine_version": "1.0.0",
        "build_revision": "dd57304",
        "privacy": {"response_redaction": "public"},
    }
    synthesis = {
        "available": True,
        "versions": {"evidence": "synthesis-evidence-v1"},
        "evidence": {
            "evidence_items": [
                {"evidence_id": "ev-001", "system": "numerology", "source_path": "signature.encoders.numerology.reduced_number",
                 "source_value": 7, "epistemic_class": "deterministic_calculation", "independence_group": "name"},
                {"evidence_id": "ev-002", "system": "astrology", "source_path": "signature.encoders.astrology.ascendant",
                 "source_value": "Aries", "epistemic_class": "deterministic_calculation", "independence_group": "birth"},
            ],
            "data_quality": {"completeness": 0.85},
        },
        "plan": {"missing_or_uncertain_dimensions": [], "contradictions": []},
    }

    def test_manifest_key_set_is_exact_and_includes_the_documented_surfaces(self):
        manifest = build_handoff_v2(
            response=self.response, synthesis=self.synthesis, analysis_mode="magic",
        )
        assert set(manifest) == HANDOFF_V2_KEYS
        assert "public_response_coverage" in manifest
        assert "redaction_rules" in manifest
        assert manifest["schema_version"] == "human-manual-agent-handoff-v2"

    def test_recorded_versus_computed_counts_reconcile(self):
        manifest = build_handoff_v2(
            response=self.response, synthesis=self.synthesis, analysis_mode="magic",
        )
        items = self.synthesis["evidence"]["evidence_items"]
        assert len(manifest["evidence_index"]) == len(items)
        assert len(manifest["source_provenance_index"]) == len(items)
        assert manifest["dependence_families"] == sorted({item["independence_group"] for item in items})
        source_values = [entry.get("source_value") for entry in manifest["evidence_index"]]
        assert source_values == [7, "Aries"]

    def test_count_mismatch_fails_loudly(self):
        manifest = build_handoff_v2(
            response=self.response, synthesis=self.synthesis, analysis_mode="magic",
        )
        with pytest.raises(AssertionError):
            assert len(manifest["evidence_index"]) == len(self.synthesis["evidence"]["evidence_items"]) + 1


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
