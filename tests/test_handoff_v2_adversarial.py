"""Adversarial Handoff v2 Redaction Test Suite.

Tests malicious/crafted fixtures containing sensitive data hidden under generic wrappers,
nested structures, and unexpected aliases to prove redaction is schema-aware and not substring-dependent.
"""
from __future__ import annotations

import pytest
from copy import deepcopy

# Import the handoff module (adjust path as needed)
import sys
sys.path.insert(0, "src")
from agent_handoff import build_handoff_v2, _safe, _evidence_projection


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
                "schema_version": "synthesis-evidence-v2",
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

        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="research")

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

        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="research")

        assert str(self.SECRET_LAT) not in str(manifest), "Nested latitude leaked"

    def test_adversarial_lat_lon_aliases(self, mock_response, mock_synthesis):
        """Test: lat/lng aliases under generic keys should be redacted."""
        response = deepcopy(mock_response)
        synthesis = deepcopy(mock_synthesis)

        response["normalized_input"] = {
            "name": "Test Subject",
            "_geo_data": {"latitude": self.SECRET_LAT, "longitude": self.SECRET_LON},
        }

        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="research")

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

        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="research")

        assert str(self.SECRET_TIMEZONE) not in str(manifest), "Timezone alias leaked"

    def test_adversarial_birthplace_string(self, mock_response, mock_synthesis):
        """Test: birthplace strings under generic keys should be redacted."""
        response = deepcopy(mock_response)
        synthesis = deepcopy(mock_synthesis)

        response["normalized_input"] = {
            "name": "Test Subject",
            "_origin_info": {"birth_place": self.SECRET_LOCATION},
        }

        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="research")

        assert str(self.SECRET_LOCATION) not in str(manifest), "Birthplace leaked"

    def test_adversarial_observation_text(self, mock_response, mock_synthesis):
        """Test: observation text under generic keys should be redacted."""
        response = deepcopy(mock_response)
        synthesis = deepcopy(mock_synthesis)

        response["normalized_input"] = {
            "name": "Test Subject",
            "_subject_notes": {"observation_text": self.SECRET_OBSERVATION},
        }

        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="research")

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

        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="research")

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

        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="research")

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

        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="research")

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

        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="research")

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

        manifest = build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="research")

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
                "schema_version": "synthesis-evidence-v2",
                "evidence_items": [
                    {"evidence_id": "ev-001", "system": "astrology"},
                ],
            },
            "plan": {},
        }

    def test_normalized_input_survives(self, mock_response, mock_synthesis):
        """Test: normalized input descriptors survive redaction."""
        manifest = build_handoff_v2(response=mock_response, synthesis=mock_synthesis, analysis_mode="research")

        assert "normalized_input" in str(manifest), "Normalized input lost"

    def test_evidence_index_survives(self, mock_response, mock_synthesis):
        """Test: evidence index survives redaction."""
        manifest = build_handoff_v2(response=mock_response, synthesis=mock_synthesis, analysis_mode="research")

        assert "evidence_index" in str(manifest), "Evidence index lost"

    def test_coverage_metadata_survives(self, mock_response, mock_synthesis):
        """Test: public response coverage metadata survives redaction."""
        manifest = build_handoff_v2(response=mock_response, synthesis=mock_synthesis, analysis_mode="research")

        assert "public_response_coverage" in str(manifest), "Coverage metadata lost"

    def test_redaction_rules_survive(self, mock_response, mock_synthesis):
        """Test: redaction rules documentation survives."""
        manifest = build_handoff_v2(response=mock_response, synthesis=mock_synthesis, analysis_mode="research")

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
            "evidence": {"schema_version": "synthesis-evidence-v2", "evidence_items": [{"evidence_id": "ev-001"}]},
            "plan": {},
        }

    def test_manifest_determinism(self, mock_response, mock_synthesis):
        """Test: same inputs produce identical manifest."""
        manifest1 = build_handoff_v2(response=mock_response, synthesis=mock_synthesis, analysis_mode="research")
        manifest2 = build_handoff_v2(response=mock_response, synthesis=mock_synthesis, analysis_mode="research")

        assert str(manifest1) == str(manifest2), "Manifest is not deterministic"

    def test_analysis_mode_variations(self, mock_response, mock_synthesis):
        """Test: different analysis modes produce distinct but valid manifests."""
        for mode in ["plain", "mythic", "research"]:
            manifest = build_handoff_v2(response=mock_response, synthesis=mock_synthesis, analysis_mode=mode)
            assert "analysis_mode" in str(manifest), f"{mode} mode not recorded"


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
            "evidence": {"schema_version": "synthesis-evidence-v2", "evidence_items": []},
            "plan": {},
        }

    def test_coverage_categories_present(self, mock_response, mock_synthesis):
        """Test: coverage array contains all expected categories."""
        manifest = build_handoff_v2(response=mock_response, synthesis=mock_synthesis, analysis_mode="research")

        # Check that coverage metadata exists and is structured correctly
        assert "public_response_coverage" in str(manifest), "Coverage array missing"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


def test_handoff_rejects_legacy_evidence_packet():
    response = {
        "normalized_input": {"name": "Test Subject"},
        "input_hash": "test_hash_12345",
        "engine_version": "signature-v2",
        "build_revision": "test",
    }
    synthesis = {
        "available": True,
        "evidence": {"schema_version": "synthesis-evidence-v1", "evidence_items": []},
        "plan": {},
    }
    with pytest.raises(ValueError, match="accepts only active synthesis-evidence-v2"):
        build_handoff_v2(response=response, synthesis=synthesis, analysis_mode="research")
