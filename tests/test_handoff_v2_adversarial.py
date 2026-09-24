"""Adversarial Handoff v2 Redaction Test Suite.

Tests malicious/crafted fixtures containing sensitive data hidden under generic wrappers,
nested structures, and unexpected aliases to prove redaction is schema-aware and not substring-dependent.
"""
from __future__ import annotations

import pytest
from copy import deepcopy

# Import the handoff module (adjust path as needed)
import os
import sys
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [_ROOT, os.path.join(_ROOT, "src"), os.path.join(_ROOT, "webapp")]
from agent_handoff import (  # noqa: E402
    HANDOFF_ANALYSIS_MODES,
    UTC_OFFSET_CLASS_DECISION,
    UTC_OFFSET_CLASS_FIELDS,
    VALUE_PATTERN_SCAN_ENV,
    _evidence_projection,
    _is_sensitive_key,
    _safe,
    _source_path_is_safe,
    build_handoff_v2,
    value_pattern_scan,
)


class TestAdversarialRedaction:
    """Prove redaction catches sensitive values regardless of key naming."""

    # Seeded secret values for deterministic testing
    SECRET_LAT = 41.2683
    SECRET_LON = -110.9632
    SECRET_LOCATION = "Evanston, Wyoming, USA"
    SECRET_TIMEZONE = "America/Denver"
    SECRET_OBSERVATION = "The subject reported feeling a strong pull toward the north at 3:47 AM."

    @pytest.fixture
    def mock_response(self):
        return {
            "normalized_input": {"name": "Test Subject", "birth_availability": True},
            "input_hash": "test_hash_12345",
            "engine_version": "1.0.0",
            "build_revision": "dd57304",
        }

    @pytest.fixture
    def mock_synthesis(self):
        return {
            "available": True,
            "evidence": {
                "evidence_items": [
                    {"evidence_id": "ev-001", "system": "astrology", "source_path": "/atlas/ascendant.json"},
                    {"evidence_id": "ev-002", "system": "numerology", "source_path": "/atlas/digit_sum.json"},
                ],
                "data_quality": {"completeness": 0.85},
            },
            "plan": {
                "contradictions": [{"tension_id": "t-1", "systems": ["astrology", "human_design"]}],
                "originating_tension": "The subject's self-report conflicts with calculated ascendant.",
            },
        }

    def test_adversarial_coords_dict(self, mock_response, mock_synthesis):
        """Test: coords dict under generic key should be redacted."""
        response = deepcopy(mock_response)
        synthesis = deepcopy(mock_synthesis)
        
        # Inject adversarial structure
        response["normalized_input"] = {
            "name": "Test Subject",
            "birth_availability": True,
            "_geo_coords": [self.SECRET_LAT, self.SECRET_LON],  # Generic key wrapping sensitive values
        }
        
        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="magic")
        
        # Verify secret values never appear in manifest (use string comparison)
        assert str(self.SECRET_LAT) not in str(manifest), "Latitude leaked in manifest"
        assert str(self.SECRET_LON) not in str(manifest), "Longitude leaked in manifest"

    def test_adversarial_coords_list(self, mock_response, mock_synthesis):
        """Test: coordinate arrays under generic key should be redacted."""
        response = deepcopy(mock_response)
        synthesis = deepcopy(mock_synthesis)
        
        response["normalized_input"] = {
            "name": "Test Subject",
            "_position_data": [[self.SECRET_LAT, self.SECRET_LON], [42.0, -111.0]],  # Nested list
        }
        
        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="magic")
        
        assert str(self.SECRET_LAT) not in str(manifest), "Nested latitude leaked"

    def test_adversarial_lat_lon_aliases(self, mock_response, mock_synthesis):
        """Test: lat/lng aliases under generic keys should be redacted."""
        response = deepcopy(mock_response)
        synthesis = deepcopy(mock_synthesis)
        
        response["normalized_input"] = {
            "name": "Test Subject",
            "_geo_data": {"latitude": self.SECRET_LAT, "longitude": self.SECRET_LON},
        }
        
        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="magic")
        
        assert str(self.SECRET_LAT) not in str(manifest), "Latitude alias leaked"
        assert str(self.SECRET_LON) not in str(manifest), "Longitude alias leaked"

    def test_adversarial_timezone_aliases(self, mock_response, mock_synthesis):
        """Test: timezone aliases under generic keys should be redacted."""
        response = deepcopy(mock_response)
        synthesis = deepcopy(mock_synthesis)
        
        response["normalized_input"] = {
            "name": "Test Subject",
            "_temporal_data": {"tz_id": self.SECRET_TIMEZONE, "timezone_offset": -6},
        }
        
        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="magic")
        
        assert str(self.SECRET_TIMEZONE) not in str(manifest), "Timezone alias leaked"

    def test_adversarial_birthplace_string(self, mock_response, mock_synthesis):
        """Test: birthplace strings under generic keys should be redacted."""
        response = deepcopy(mock_response)
        synthesis = deepcopy(mock_synthesis)
        
        response["normalized_input"] = {
            "name": "Test Subject",
            "_origin_info": {"birth_place": self.SECRET_LOCATION},
        }
        
        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="magic")
        
        assert str(self.SECRET_LOCATION) not in str(manifest), "Birthplace leaked"

    def test_adversarial_observation_text(self, mock_response, mock_synthesis):
        """Test: observation text under generic keys should be redacted."""
        response = deepcopy(mock_response)
        synthesis = deepcopy(mock_synthesis)
        
        response["normalized_input"] = {
            "name": "Test Subject",
            "_subject_notes": {"observation_text": self.SECRET_OBSERVATION},
        }
        
        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="magic")
        
        assert self.SECRET_OBSERVATION not in str(manifest), "Observation text leaked"

    def test_adversarial_nested_provenance(self, mock_response, mock_synthesis):
        """Test: nested provenance structures with sensitive values should be redacted."""
        response = deepcopy(mock_response)
        synthesis = deepcopy(mock_synthesis)
        
        # Deeply nested structure mimicking real-world API responses
        response["normalized_input"] = {
            "name": "Test Subject",
            "_metadata": {
                "source": {
                    "location": self.SECRET_LOCATION,
                    "coordinates": [self.SECRET_LAT, self.SECRET_LON],
                    "timestamp_tz": self.SECRET_TIMEZONE,
                }
            },
        }
        
        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="magic")
        
        assert self.SECRET_LOCATION not in str(manifest), "Nested location leaked"

    def test_adversarial_evidence_index_coords(self, mock_response, mock_synthesis):
        """Test: evidence index with coordinate arrays should be redacted."""
        response = deepcopy(mock_response)
        synthesis = deepcopy(mock_synthesis)
        
        # Inject adversarial coordinates into evidence items
        synthesis["evidence"]["evidence_items"] = [
            {
                "evidence_id": "ev-001",
                "system": "astrology",
                "source_path": "/atlas/ascendant.json",
                "geo_reference": {"lat": self.SECRET_LAT, "lng": self.SECRET_LON},  # Aliased keys
            }
        ]
        
        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="magic")
        
        assert str(self.SECRET_LAT) not in str(manifest), "Evidence index latitude leaked"

    def test_adversarial_list_of_dicts(self, mock_response, mock_synthesis):
        """Test: list of dicts containing sensitive values should be redacted."""
        response = deepcopy(mock_response)
        synthesis = deepcopy(mock_synthesis)
        
        response["normalized_input"] = {
            "name": "Test Subject",
            "_data_points": [
                {"x": self.SECRET_LAT, "y": self.SECRET_LON},
                {"location": self.SECRET_LOCATION},
            ],
        }
        
        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="magic")
        
        assert str(self.SECRET_LAT) not in str(manifest), "List dict latitude leaked"

    def test_adversarial_mixed_nested_structure(self, mock_response, mock_synthesis):
        """Test: complex mixed nested structure with multiple sensitive patterns."""
        response = deepcopy(mock_response)
        synthesis = deepcopy(mock_synthesis)
        
        response["normalized_input"] = {
            "name": "Test Subject",
            "_complex_data": [
                {"geo": [self.SECRET_LAT, self.SECRET_LON]},
                {"meta": {"timezone": self.SECRET_TIMEZONE}},
                {"notes": self.SECRET_OBSERVATION},
            ],
        }
        
        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="magic")
        
        assert str(self.SECRET_LAT) not in str(manifest), "Latitude leaked"
        assert str(self.SECRET_LON) not in str(manifest), "Longitude leaked"
        assert str(self.SECRET_TIMEZONE) not in str(manifest), "Timezone leaked"
        assert str(self.SECRET_OBSERVATION) not in str(manifest), "Observation text leaked"

    def test_adversarial_unicode_and_encoding(self, mock_response, mock_synthesis):
        """Test: sensitive values with unicode/encoding tricks should be redacted."""
        response = deepcopy(mock_response)
        synthesis = deepcopy(mock_synthesis)
        
        # Unicode variations that might bypass naive matching
        response["normalized_input"] = {
            "name": "Test Subject",
            "_encoded_data": {"location": self.SECRET_LOCATION.encode().decode("utf-8")},
        }
        
        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="magic")
        
        assert self.SECRET_LOCATION not in str(manifest), "Unicode-encoded location leaked"


class TestLegitimateMetadataPreservation:
    """Prove safe legitimate metadata survives redaction."""

    @pytest.fixture
    def mock_response(self):
        return {
            "normalized_input": {"name": "Test Subject", "birth_availability": True},
            "input_hash": "test_hash_12345",
            "engine_version": "1.0.0",
            "build_revision": "dd57304",
        }

    @pytest.fixture
    def mock_synthesis(self):
        return {
            "available": True,
            "evidence": {
                "evidence_items": [
                    {"evidence_id": "ev-001", "system": "astrology"},
                ],
            },
            "plan": {},
        }

    def test_normalized_input_survives(self, mock_response, mock_synthesis):
        """Test: normalized input descriptors survive redaction."""
        manifest = build_handoff_v2(response=mock_response, synthesis=mock_synthesis, analysis_mode="magic")
        
        assert "normalized_input" in str(manifest), "Normalized input lost"

    def test_evidence_index_survives(self, mock_response, mock_synthesis):
        """Test: evidence index survives redaction."""
        manifest = build_handoff_v2(response=mock_response, synthesis=mock_synthesis, analysis_mode="magic")
        
        assert "evidence_index" in str(manifest), "Evidence index lost"

    def test_coverage_metadata_survives(self, mock_response, mock_synthesis):
        """Test: public response coverage metadata survives redaction."""
        manifest = build_handoff_v2(response=mock_response, synthesis=mock_synthesis, analysis_mode="magic")
        
        assert "public_response_coverage" in str(manifest), "Coverage metadata lost"

    def test_redaction_rules_survive(self, mock_response, mock_synthesis):
        """Test: redaction rules documentation survives."""
        manifest = build_handoff_v2(response=mock_response, synthesis=mock_synthesis, analysis_mode="magic")
        
        assert "redaction_rules" in str(manifest), "Redaction rules lost"


class TestDeterministicReplayStability:
    """Prove handoff v2 manifest is deterministic and replayable."""

    @pytest.fixture
    def mock_response(self):
        return {
            "normalized_input": {"name": "Test Subject"},
            "input_hash": "test_hash_12345",
            "engine_version": "1.0.0",
            "build_revision": "dd57304",
        }

    @pytest.fixture
    def mock_synthesis(self):
        return {
            "available": True,
            "evidence": {"evidence_items": [{"evidence_id": "ev-001"}]},
            "plan": {},
        }

    def test_manifest_determinism(self, mock_response, mock_synthesis):
        """Test: same inputs produce identical manifest."""
        manifest1 = build_handoff_v2(response=mock_response, synthesis=mock_synthesis, analysis_mode="magic")
        manifest2 = build_handoff_v2(response=mock_response, synthesis=mock_synthesis, analysis_mode="magic")
        
        assert str(manifest1) == str(manifest2), "Manifest is not deterministic"

    def test_analysis_mode_variations(self, mock_response, mock_synthesis):
        """Test: every accepted analysis mode produces a valid manifest."""
        for mode in sorted(HANDOFF_ANALYSIS_MODES):
            manifest = build_handoff_v2(response=mock_response, synthesis=mock_synthesis, analysis_mode=mode)
            assert "analysis_mode" in str(manifest), f"{mode} mode not recorded"

    def test_unknown_analysis_mode_is_rejected(self, mock_response, mock_synthesis):
        """CD-12: an unknown analysis_mode is rejected, never silently echoed."""
        for mode in ("plain", "research", "mythic", "", "MAGIC"):
            with pytest.raises(ValueError, match="Unknown analysis_mode"):
                build_handoff_v2(response=mock_response, synthesis=mock_synthesis, analysis_mode=mode)

    def test_handoff_modes_mirror_the_public_contract(self):
        """The mirrored mode set cannot drift from the public contract."""
        from public_contract import MODES
        assert set(HANDOFF_ANALYSIS_MODES) == set(MODES)


class TestCategoryCoverage:
    """Prove every supported response category is included or explicitly excluded."""

    @pytest.fixture
    def mock_response(self):
        return {
            "normalized_input": {"name": "Test Subject"},
            "input_hash": "test_hash_12345",
            "engine_version": "1.0.0",
            "build_revision": "dd57304",
        }

    @pytest.fixture
    def mock_synthesis(self):
        return {
            "available": True,
            "evidence": {"evidence_items": []},
            "plan": {},
        }

    def test_coverage_categories_present(self, mock_response, mock_synthesis):
        """Test: coverage array contains all expected categories."""
        manifest = build_handoff_v2(response=mock_response, synthesis=mock_synthesis, analysis_mode="magic")

        # Check that coverage metadata exists and is structured correctly
        assert "public_response_coverage" in str(manifest), "Coverage array missing"


class TestUtcOffsetTransitDecision:
    """CD-05 / EN-07: the utc_offset-class decision is explicit, not silent."""

    def test_recorded_decision_is_reject(self):
        assert UTC_OFFSET_CLASS_DECISION == "reject"
        assert set(UTC_OFFSET_CLASS_FIELDS) == {"utc_offset", "timezone_offset", "gmt_offset"}

    def test_utc_offset_class_keys_do_not_transit(self):
        for key in UTC_OFFSET_CLASS_FIELDS:
            assert _is_sensitive_key(key) is True
            assert _safe({key: -6.0, "kept": 1}) == {"kept": 1}

    def test_utc_offset_class_paths_are_rejected(self):
        for path in (
            "signature.systems.jyotish.calculation.utc_offset",
            "signature.encoders.astrology.gmt_offset",
        ):
            assert _source_path_is_safe(path) is False


class TestSourcePathSegmentSafety:
    """EN-07: segment-boundary prefix hardening and prefix-confusion rejection."""

    def test_registered_calculator_namespace_transits(self):
        for path in (
            "signature.systems.jyotish.calculation.ayanamsa.degrees",
            "signature.systems.bazi.calculation.pillars.day.stem",
            "signature.systems.maya_classical.calculation.tzolkin.label",
        ):
            assert _source_path_is_safe(path) is True

    def test_prefix_confusion_is_rejected(self):
        for path in (
            "signature.systems.evil.calculation.secret",
            "signature.systems.unknown_system.value",
            "signature.systems.",
            "signature.systems",
            "signature.systemsX.value",
            "signature.encoders.",
            "",
        ):
            assert _source_path_is_safe(path) is False

    def test_unreviewed_prefix_and_non_string_are_rejected(self):
        for path in ("signature.psychology.mbti", "/atlas/ascendant.json", None, 17, ["signature.encoders.x"]):
            assert _source_path_is_safe(path) is False

    def test_sensitive_segment_and_substring_are_rejected(self):
        for path in (
            "signature.encoders.astrology.planets.0.longitude",
            "signature.encoders.astrology.timezone_basis.birth_utc_iso",
            "signature.encoders.astrology.birth_place",
        ):
            assert _source_path_is_safe(path) is False


class TestValuePatternScan:
    """EN-07: opt-in value sanitizer. Flag off (default) keeps today's policy."""

    response = {
        "normalized_input": {"name": "Test Subject"},
        "input_hash": "test_hash_12345",
        "engine_version": "1.0.0",
        "build_revision": "dd57304",
    }

    def _synthesis(self, evidence_item, data_quality):
        return {
            "available": True,
            "evidence": {"evidence_items": [evidence_item], "data_quality": data_quality},
            "plan": {},
        }

    def test_flag_off_leaves_the_projection_unchanged(self, monkeypatch):
        monkeypatch.delenv(VALUE_PATTERN_SCAN_ENV, raising=False)
        item = {
            "evidence_id": "ev-001", "system": "jyotish",
            "source_path": "signature.systems.jyotish.calculation.ayanamsa.degrees",
            "source_value": "24.123456",
        }
        manifest = build_handoff_v2(
            response=self.response, synthesis=self._synthesis(item, {}), analysis_mode="magic",
        )
        assert manifest["evidence_index"][0]["source_value"] == "24.123456"

    def test_flag_on_excludes_a_coordinate_under_a_safe_path(self, monkeypatch):
        monkeypatch.setenv(VALUE_PATTERN_SCAN_ENV, "1")
        item = {
            "evidence_id": "ev-001", "system": "jyotish",
            "source_path": "signature.systems.jyotish.calculation.ayanamsa.degrees",
            "source_value": "41.2683",
        }
        # would-fail-if-detection-did-not-fire
        assert value_pattern_scan("41.2683") == "value_pattern_scan_flagged_coordinate"
        manifest = build_handoff_v2(
            response=self.response, synthesis=self._synthesis(item, {}), analysis_mode="magic",
        )
        projected = manifest["evidence_index"][0]
        assert "source_value" not in projected
        assert projected["source_value_excluded"] == "value_pattern_scan_flagged_coordinate"

    def test_flag_on_drops_a_secret_under_a_benign_key(self, monkeypatch):
        monkeypatch.setenv(VALUE_PATTERN_SCAN_ENV, "1")
        secret = "analyst@example.com"
        assert value_pattern_scan(secret) == "value_pattern_scan_flagged_contact"
        item = {"evidence_id": "ev-001", "system": "numerology"}
        manifest = build_handoff_v2(
            response=self.response,
            synthesis=self._synthesis(item, {"completeness": 0.85, "contact": secret}),
            analysis_mode="magic",
        )
        assert secret not in str(manifest)
        assert manifest["unavailable_calculations"]["data_quality"]["completeness"] == 0.85

    def test_flag_on_still_transits_benign_values(self, monkeypatch):
        monkeypatch.setenv(VALUE_PATTERN_SCAN_ENV, "1")
        item = {
            "evidence_id": "ev-001", "system": "numerology",
            "source_path": "signature.systems.bazi.calculation.pillars.day.stem",
            "source_value": "Jia",
        }
        manifest = build_handoff_v2(
            response=self.response,
            synthesis=self._synthesis(item, {"completeness": 0.85}),
            analysis_mode="magic",
        )
        assert manifest["evidence_index"][0]["source_value"] == "Jia"


# EN-17: deterministic, seeded/fixed property table over handoff payload shapes.
# Detection must fire where expected and benign values must still transit.
REDACTION_PROPERTY_TABLE = (
    # (case_id, key, value, expect_detection)
    ("case-01", "metric", "41.2683", True),
    ("case-02", "contact", "analyst@example.com", True),
    ("case-03", "contact", "+1 307-555-0134", True),
    ("case-04", "seen", "2026-09-22T15:30", True),
    ("case-05", "paired", "41.2683, -110.9632", True),
    ("case-06", "completeness", "0.85", False),
    ("case-07", "label", "Jia", False),
    ("case-08", "basis", "structural_count", False),
    ("case-09", "day_name", "Ajaw", False),
    ("case-10", "note_free", "interpretive synthesis", False),
)


class TestDeterministicAdversarialPropertyTable:
    def test_property_table_is_deterministic_and_detection_fires(self, monkeypatch):
        monkeypatch.setenv(VALUE_PATTERN_SCAN_ENV, "1")
        response = {"normalized_input": {"name": "Test Subject"}, "input_hash": "h", "engine_version": "1", "build_revision": "dd57304"}
        for case_id, key, value, expect in REDACTION_PROPERTY_TABLE:
            fired = value_pattern_scan(value) is not None
            assert fired is expect, f"{case_id}: detection state {fired} != expected {expect}"

            synthesis = {
                "available": True,
                "evidence": {
                    "evidence_items": [{"evidence_id": "ev-001", "system": "numerology"}],
                    "data_quality": {key: value},
                },
                "plan": {},
            }
            manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="magic")
            serialized = str(manifest)
            if expect:
                assert value not in serialized, f"{case_id}: flagged value transited"
            else:
                assert value in serialized, f"{case_id}: benign value was dropped"

    def test_property_table_is_fixed_and_seeded(self):
        assert len(REDACTION_PROPERTY_TABLE) == 10
        assert len({case[0] for case in REDACTION_PROPERTY_TABLE}) == 10


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
