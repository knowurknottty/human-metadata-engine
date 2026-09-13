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
