from __future__ import annotations

import json
import math
from pathlib import Path

from encoders.bazi import compute_bazi
from encoders.jyotish import _dasamsa, _nakshatra, _navamsha, compute_jyotish
from encoders.maya_classical import compute_classical_maya
from signature_v3 import compute_signature_v3
from system_contracts import summarize_systems
from timing_v1 import VIMSHOTTARI_SEQUENCE, compute_vimshottari


ROOT = Path(__file__).resolve().parents[1]
BIRTH = {
    "year": 2000, "month": 1, "day": 7,
    "hour": 12, "minute": 0, "timezone_offset": 8,
    "location": "Beijing, China", "lat": 39.9042, "lon": 116.4074,
    "time_accuracy": "exact",
}


def test_bazi_known_reference_day_and_month():
    result = compute_bazi(BIRTH)
    assert result["contract_version"] == "system-result-v2"
    assert result["dependency_roots"] == ["birth_instant"]
    calc = result["calculation"]
    assert calc["pillars"]["year"]["stem"] == "Ji"
    assert calc["pillars"]["year"]["branch"] == "Mao"
    assert calc["pillars"]["month"]["stem"] == "Ding"
    assert calc["pillars"]["month"]["branch"] == "Chou"
    assert calc["pillars"]["day"]["stem"] == "Jia"
    assert calc["pillars"]["day"]["branch"] == "Zi"
    assert calc["day_master"] == {"stem": "Jia", "element": "Wood", "polarity": "Yang"}
    assert calc["five_phase_distribution_basis"]["complete"] is True
    assert math.isclose(sum(calc["five_phase_distribution"].values()), 1.0, abs_tol=1e-5)


def test_unknown_birth_time_keeps_bazi_date_pillars_without_guessing_hour():
    unknown = {**BIRTH, "time_accuracy": "unknown"}
    unknown.pop("hour")
    unknown.pop("minute")
    result = compute_bazi(unknown)
    assert result["status"] == "computed"
    assert result["dependency_roots"] == ["birth_date"]
    calc = result["calculation"]
    assert calc["pillars"]["hour"] is None
    assert calc["pillars"]["year"]["stem"] == "Ji"
    assert calc["pillars"]["month"]["stem"] == "Ding"
    assert calc["pillars"]["day"]["stem"] == "Jia"
    assert calc["five_phase_distribution_basis"]["complete"] is False
    assert calc["five_phase_distribution_basis"]["available_pillars"] == ["year", "month", "day"]
    assert calc["solar_longitude"] is None
    assert calc["solar_longitude_range"] is not None


def test_unknown_birth_time_refuses_jyotish_and_vimshottari():
    unknown = {**BIRTH, "time_accuracy": "unknown"}
    for result in (compute_jyotish(unknown), compute_vimshottari(unknown)):
        assert result["status"] == "input_insufficient"
        assert result["calculation"] == {}


def test_nakshatra_navamsha_and_dasamsa_boundaries():
    assert _nakshatra(0.0)["name"] == "Ashwini"
    assert _nakshatra(0.0)["pada"] == 1
    assert _nakshatra((360 / 27) - 1e-8)["pada"] == 4
    assert _nakshatra(360 / 27)["name"] == "Bharani"
    assert _navamsha(0.0)["sign"] == "Aries"
    assert _navamsha(30.0)["sign"] == "Capricorn"
    assert _navamsha(60.0)["sign"] == "Libra"
    assert _dasamsa(0.0)["sign"] == "Aries"
    assert _dasamsa(3.0)["sign"] == "Taurus"
    assert _dasamsa(30.0)["sign"] == "Capricorn"
    assert _dasamsa(35.0)["sign"] == "Aquarius"


def test_jyotish_lahiri_projection_is_reproducible_and_requests_speed():
    first = compute_jyotish(BIRTH)
    second = compute_jyotish(BIRTH)
    assert first == second
    calc = first["calculation"]
    assert calc["ayanamsa"]["name"] == "Lahiri"
    assert 22.0 < calc["ayanamsa"]["degrees"] < 25.0
    assert len(calc["planets"]) == 10
    assert calc["planets"]["Saturn"]["retrograde"] is True
    assert calc["planets"]["Saturn"]["speed_longitude"] < 0
    assert calc["moon_nakshatra"]["name"] in {
        item["nakshatra"]["name"] for item in calc["planets"].values()
    }


def test_system_manifest_separates_lenses_roots_and_independence_families():
    systems = {
        "bazi": compute_bazi(BIRTH),
        "jyotish": compute_jyotish(BIRTH),
        "maya": compute_classical_maya(BIRTH),
    }
    manifest = summarize_systems(systems)
    assert manifest["system_count"] == 3
    assert manifest["lens_count"] == 3
    assert manifest["dependency_roots"]["birth_instant"] == 2
    assert manifest["dependency_roots"]["birth_date"] == 1
    assert manifest["raw_dependency_root_count"] == 2
    assert manifest["independence_families"]["birth"] == 3
    assert manifest["independence_family_count"] == 1


def test_system_result_envelope_tracks_inputs_sensitivity_license_and_schema_shape():
    result = compute_jyotish(BIRTH)
    assert result["sensitivity"] == "personal"
    assert result["input_dependencies"] == [
        "birth.coordinates", "birth.date", "birth.local_time", "birth.utc_offset"
    ]
    assert result["license"]["calculation_code"] == "project-authored"
    assert result["license"]["third_party_dependencies"] == ["pyswisseph AGPL-3.0-or-later"]
    schema = json.loads((ROOT / "schemas" / "system-result-v2.schema.json").read_text(encoding="utf-8"))
    required = set(schema["required"])
    assert required <= set(result)
    assert set(result) <= set(schema["properties"])
    assert schema["properties"]["contract_version"]["const"] == "system-result-v2"


def test_vimshottari_is_separate_timing_artifact_with_120_year_sequence():
    result = compute_vimshottari(BIRTH, as_of="2001-01-07T00:00:00Z")
    assert result["artifact_class"] == "timing"
    assert result["dependency_roots"] == ["birth_instant"]
    calc = result["calculation"]
    assert calc["sequence"] == VIMSHOTTARI_SEQUENCE
    assert sum(calc["nominal_years"].values()) == 120.0
    assert calc["birth_dasha_balance"]["lord"] == calc["birth_moon"]["nakshatra_ruler"]
    assert abs(sum(p["duration_years"] for p in calc["mahadasha_periods"]) - 120.0) < 1e-6
    assert calc["active_mahadasha"] is not None


def test_signature_v3_keeps_legacy_surface_and_separates_timing():
    identity = {"id": "human:test", "text": "Test Person", "birth": BIRTH}
    without = compute_signature_v3(identity, snapshot_fn=None)
    assert without["contract_version"] == "signature-v3"
    assert without["legacy_contract_version"] == "signature-v2"
    assert {"bazi", "jyotish", "maya_classical"} <= set(without["systems"])
    assert "bazi" not in without["encoders"]
    assert without["timing"] == {}
    assert without["convergence_policy"]["unit"] == "dependency_family"
    assert without["convergence_policy"]["timing_excluded_from_static_convergence"] is True

    with_timing = compute_signature_v3(
        identity, snapshot_fn=None, include_timing=True, as_of="2001-01-07T00:00:00Z"
    )
    assert "vimshottari" in with_timing["timing"]
    assert "vimshottari" not in with_timing["systems"]
    assert with_timing["artifacts"]["timing"]["vimshottari"]["artifact_class"] == "timing"


def test_classical_maya_2012_reference_anchor():
    result = compute_classical_maya({"year": 2012, "month": 12, "day": 21})
    calc = result["calculation"]
    assert calc["long_count"]["notation"] == "13.0.0.0.0"
    assert calc["tzolkin"]["label"] == "4 Ajaw"
    assert calc["haab"]["label"] == "3 K'ank'in"
    assert calc["lord_of_night"] == "G9"


# ---------------------------------------------------------------------------
# R4: per-system disclosure (EN-02), golden provenance headers (EN-04), and
# timezone fallback / environment provenance (EN-14).
# ---------------------------------------------------------------------------

import hashlib  # noqa: E402

UNKNOWN_BIRTH = {**BIRTH, "time_accuracy": "unknown"}
UNKNOWN_DATE_ONLY = {k: v for k, v in UNKNOWN_BIRTH.items() if k not in {"hour", "minute"}}
MAYA_ANCHOR = {"year": 2012, "month": 12, "day": 21}
MAYA_PRE_CORRELATION = {"year": -3200, "month": 1, "day": 1}

DOC = ROOT / "docs" / "SIGNATURE_V3.md"

# Byte-stable limitations digests, computed from the released wording. A change
# here is a disclosure change and must be re-baselined deliberately with a
# changelog entry (docs/SIGNATURE_V3.md#convention-governance-protocol).
LIMITATIONS_GOLDEN = {
    "jyotish_known": "56c6383c739e5791c2ca5f143391bb551f028e4029461ff5053fe5c62087b78b",
    "jyotish_unknown": "976d87be9cabc85c103470f26af7c9935fa499fa38a88d888e4f53dd25a81efa",
    "bazi_known": "29f8feb6b07530a5bbc04e9af72150679950833520366b3cdbada76cbc837256",
    "bazi_unknown": "9ba5200968da4518c6b5ff00bf42e075a4651343b4f6549aa38117036cdadf54",
    "maya_computed": "b26542dd3d1d11b488b055abd055134bb072f9b8297cb499531362c7d986b2bf",
}


def _limitations_digest(limitations):
    return hashlib.sha256("\n".join(limitations).encode()).hexdigest()


def _timezone_basis(result):
    return result.get("calculation", {}).get("timezone_basis", {})


def _golden_header(result):
    """Fixture provenance header recorded beside every golden."""
    basis = _timezone_basis(result)
    return {
        "system_version": result["system_version"],
        "convention": result["convention"],
        "tzdata_version": basis.get("tzdata_version"),
        "limitations_sha256": _limitations_digest(result["limitations"]),
    }


def _assert_golden_matches(golden, current):
    if golden != current:
        raise AssertionError(
            "Golden provenance drift detected. Re-baseline deliberately and record a "
            "changelog entry (see docs/SIGNATURE_V3.md convention-governance protocol). "
            f"expected={golden} actual={current}"
        )


def test_per_system_disclosure_block_is_present_and_traceable():
    cases = {
        "jyotish": compute_jyotish(BIRTH),
        "bazi": compute_bazi(BIRTH),
        "maya_classical": compute_classical_maya(MAYA_ANCHOR),
    }
    doc = DOC.read_text(encoding="utf-8")
    for system, result in cases.items():
        disclosure = result["interpretation"]["disclosure"]
        assert set(disclosure) == {"convention", "approximation_precision", "precision_basis"}
        assert disclosure["convention"] == result["convention"]
        assert disclosure["approximation_precision"] in {"undisclosed", "exact_integer"}
        assert isinstance(disclosure["approximation_precision"], str)
        # The label is traceable to the implementation docs.
        assert result["convention"] in doc, f"{system} convention not documented"
        assert disclosure["approximation_precision"] in doc


def test_disclosure_never_claims_birth_precision_true_solar_or_a_scalar():
    for result in (
        compute_jyotish(BIRTH),
        compute_bazi(BIRTH),
        compute_classical_maya(MAYA_ANCHOR),
    ):
        disclosure = result["interpretation"]["disclosure"]
        assert not isinstance(disclosure["approximation_precision"], (int, float))
        for key in disclosure:
            assert "true_solar" not in key
            assert "23:00" not in key
            assert "rollover" not in key
            assert "birth_precision" not in key
            assert "confidence" not in key


def test_disclosure_strings_are_byte_stable():
    for factory in (lambda: compute_jyotish(BIRTH), lambda: compute_bazi(BIRTH),
                    lambda: compute_classical_maya(MAYA_ANCHOR)):
        first, second = factory(), factory()
        assert first["interpretation"]["disclosure"] == second["interpretation"]["disclosure"]


def test_golden_headers_record_version_convention_tzdata_and_limitations():
    fixtures = {
        "jyotish_known": compute_jyotish(BIRTH),
        "jyotish_unknown": compute_jyotish(UNKNOWN_DATE_ONLY),
        "bazi_known": compute_bazi(BIRTH),
        "bazi_unknown": compute_bazi(UNKNOWN_DATE_ONLY),
        "maya_computed": compute_classical_maya(MAYA_ANCHOR),
    }
    for name, result in fixtures.items():
        header = _golden_header(result)
        assert set(header) == {"system_version", "convention", "tzdata_version", "limitations_sha256"}
        assert header["limitations_sha256"] == LIMITATIONS_GOLDEN[name], f"{name} limitations drifted"
        assert header["tzdata_version"] is None or isinstance(header["tzdata_version"], str)

    tzdata_headers = [_golden_header(fixtures[name])["tzdata_version"] for name in ("jyotish_known", "bazi_known")]
    for value in tzdata_headers:
        assert value is None or value.count(".") == 1


def test_simulated_tzdata_bump_fails_loudly_with_an_actionable_message():
    result = compute_jyotish(BIRTH)
    current = _golden_header(result)
    assert _golden_header(result) == current  # no drift today
    simulated = {**current, "tzdata_version": "9999.1"}
    try:
        _assert_golden_matches(simulated, current)
    except AssertionError as exc:
        assert "changelog" in str(exc)
        assert "docs/SIGNATURE_V3.md" in str(exc)
    else:
        raise AssertionError("golden drift did not fail loudly")


def test_limitations_are_byte_stable_per_calculator():
    assert _limitations_digest(compute_jyotish(BIRTH)["limitations"]) == LIMITATIONS_GOLDEN["jyotish_known"]
    assert _limitations_digest(compute_bazi(BIRTH)["limitations"]) == LIMITATIONS_GOLDEN["bazi_known"]
    assert _limitations_digest(compute_classical_maya(MAYA_ANCHOR)["limitations"]) == LIMITATIONS_GOLDEN["maya_computed"]


def test_invalid_timezone_id_falls_back_to_a_valid_timezone_name():
    birth = {**BIRTH, "timezone_id": "Not/AZone", "timezone_name": "America/Denver"}
    birth.pop("timezone_offset")
    for result in (compute_jyotish(birth), compute_bazi(birth)):
        assert result["status"] == "computed"
        basis = _timezone_basis(result)
        assert basis["model"] == "iana_zoneinfo"
        assert basis["timezone_id"] == "America/Denver"


def test_timezone_meta_label_matches_the_supplied_spelling():
    for spelling in ("timezone_id", "tzid", "timezone_name"):
        birth = {**BIRTH, spelling: "America/Denver"}
        birth.pop("timezone_offset")
        assert _timezone_basis(compute_jyotish(birth))["timezone_id"] == "America/Denver"
        assert _timezone_basis(compute_bazi(birth))["timezone_id"] == "America/Denver"


def test_offset_regression_for_reference_zones():
    expected = {"Asia/Kolkata": 5.5, "America/Denver": -7.0, "Asia/Shanghai": 8.0, "UTC": 0.0}
    for zone, offset in expected.items():
        birth = {**BIRTH, "timezone_id": zone}
        birth.pop("timezone_offset")
        for result in (compute_jyotish(birth), compute_bazi(birth)):
            basis = _timezone_basis(result)
            assert basis["timezone_id"] == zone
            assert basis["effective_offset_hours"] == offset


def test_tzdata_provenance_field_is_always_emitted_and_shape_checked():
    for result in (compute_jyotish(BIRTH), compute_bazi(BIRTH)):
        basis = _timezone_basis(result)
        assert "tzdata_version" in basis
        value = basis["tzdata_version"]
        assert value is None or (isinstance(value, str) and value.replace(".", "").isdigit())
    # A fixed-offset result records no IANA provenance rather than inventing one.
    fixed = {**BIRTH}
    fixed.pop("timezone_offset")
    fixed["timezone_offset"] = 5.5
    assert _timezone_basis(compute_bazi(fixed))["tzdata_version"] is None


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-q"]))
