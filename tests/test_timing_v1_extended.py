from __future__ import annotations

import math

import pytest

from encoders.jyotish import compute_jyotish
from signature_v3 import compute_signature_v3
from timing_v1 import (
    compute_annual_profection,
    compute_planetary_hours,
    compute_secondary_progressions,
    compute_solar_arc,
    compute_solar_return,
    compute_transits,
    compute_zodiacal_releasing,
)

BIRTH = {
    "year": 2000, "month": 1, "day": 7,
    "hour": 12, "minute": 0, "timezone_offset": 8,
    "location": "Beijing, China", "lat": 39.9042, "lon": 116.4074,
    "time_accuracy": "exact",
}
AS_OF = "2026-09-15T19:00:00Z"


def test_jyotish_supports_named_lahiri_and_raman_without_blending():
    lahiri = compute_jyotish(BIRTH, ayanamsa="lahiri", lunar_node="mean")
    raman = compute_jyotish(BIRTH, ayanamsa="raman", lunar_node="mean")
    assert lahiri["system_version"] == "jyotish-v2"
    assert raman["system_version"] == "jyotish-v2"
    assert lahiri["calculation"]["ayanamsa"]["name"] == "Lahiri"
    assert raman["calculation"]["ayanamsa"]["name"] == "Raman"
    assert lahiri["convention"] == "lahiri-mean-node-27-nakshatra-v2"
    assert raman["convention"] == "raman-mean-node-27-nakshatra-v2"
    delta = (raman["calculation"]["planets"]["Moon"]["longitude"] - lahiri["calculation"]["planets"]["Moon"]["longitude"]) % 360
    assert 1.0 < delta < 2.0


def test_jyotish_records_mean_or_true_rahu_ketu_convention():
    mean = compute_jyotish(BIRTH, lunar_node="mean")
    true = compute_jyotish(BIRTH, lunar_node="true")
    for result, expected in ((mean, "mean"), (true, "true")):
        nodes = result["calculation"]["lunar_nodes"]
        assert nodes["mode"] == expected
        rahu = nodes["Rahu"]["longitude"]
        ketu = nodes["Ketu"]["longitude"]
        assert math.isclose((ketu - rahu) % 360.0, 180.0, abs_tol=1e-9)
    assert abs(mean["calculation"]["lunar_nodes"]["Rahu"]["longitude"] - true["calculation"]["lunar_nodes"]["Rahu"]["longitude"]) > 0.5


def test_jyotish_rejects_unversioned_convention_names():
    with pytest.raises(ValueError):
        compute_jyotish(BIRTH, ayanamsa="mystery")
    with pytest.raises(ValueError):
        compute_jyotish(BIRTH, lunar_node="blended")


def test_transits_require_explicit_as_of_and_emit_only_calculated_contacts():
    missing = compute_transits(BIRTH, as_of=None)
    assert missing["status"] == "input_insufficient"
    result = compute_transits(BIRTH, as_of=AS_OF)
    assert result["status"] == "computed"
    calc = result["calculation"]
    assert calc["zodiac"] == "tropical"
    assert calc["major_aspect_orb_degrees"] == 1.0
    assert set(calc["natal_positions"]) == set(calc["transit_positions"])
    assert all(contact["orb"] <= 1.0 for contact in calc["contacts"])


def test_secondary_progression_and_solar_arc_share_day_for_year_basis():
    progressed = compute_secondary_progressions(BIRTH, as_of=AS_OF)
    arc = compute_solar_arc(BIRTH, as_of=AS_OF)
    assert progressed["status"] == "computed"
    assert arc["status"] == "computed"
    assert progressed["calculation"]["progressed_ephemeris_utc"].startswith("2000-02-02")
    assert 26.0 < progressed["calculation"]["symbolic_days_after_birth"] < 27.0
    assert 26.0 < arc["calculation"]["solar_arc_degrees"] < 28.0
    assert math.isclose(arc["calculation"]["directed_positions"]["Sun"]["longitude"], arc["calculation"]["progressed_sun_longitude"], abs_tol=1e-6)


def test_solar_return_brackets_as_of_with_exact_sun_crossings():
    result = compute_solar_return(BIRTH, as_of=AS_OF)
    assert result["status"] == "computed"
    calc = result["calculation"]
    assert calc["previous_return_utc"] < AS_OF
    assert calc["next_return_utc"] > AS_OF
    assert calc["previous_return_chart"]["location_basis"] == "birth_coordinates"
    assert len(calc["previous_return_chart"]["house_cusps"]) == 12


def test_annual_profection_is_whole_sign_and_uses_classical_rulers():
    result = compute_annual_profection(BIRTH, as_of=AS_OF)
    assert result["status"] == "computed"
    calc = result["calculation"]
    assert calc["completed_civil_years"] == 26
    assert calc["natal_rising_sign"] == "Aries"
    assert calc["profected_house"] == 3
    assert calc["activated_sign"] == "Gemini"
    assert calc["lord_of_year"] == "Mercury"
    assert calc["ruler_scheme"] == "classical-seven-planet"


def test_planetary_hours_use_environment_context_not_birth_as_evidence():
    context = {"lat": 34.7304, "lon": -86.5861, "timezone_offset": -5}
    result = compute_planetary_hours(context, as_of=AS_OF)
    assert result["status"] == "computed"
    assert result["dependency_roots"] == ["environment_context"]
    calc = result["calculation"]
    assert calc["phase"] in {"day", "night"}
    assert 1 <= calc["planetary_hour_number"] <= 24
    assert calc["ruler"] in calc["chaldean_order"]
    assert calc["hour_start_utc"] <= AS_OF < calc["hour_end_utc"]


def test_zodiacal_releasing_l1_uses_explicit_lots_sect_and_211_year_cycle():
    result = compute_zodiacal_releasing(BIRTH, as_of=AS_OF, lot="spirit")
    assert result["status"] == "computed"
    calc = result["calculation"]
    assert calc["selected_lot"] == "spirit"
    assert calc["sect"] in {"day", "night"}
    assert set(calc["lots"]) == {"fortune", "spirit"}
    assert calc["level_1_cycle_years"] == 211.0
    assert len(calc["level_1_periods"]) == 12
    assert calc["active_level_1"] is not None


def test_signature_v3_emits_dynamic_timing_only_when_explicitly_requested():
    identity = {"id": "human:test", "text": "Test Person", "birth": BIRTH}
    without = compute_signature_v3(identity, snapshot_fn=None)
    assert without["timing"] == {}
    with_timing = compute_signature_v3(
        identity, snapshot_fn=None, include_timing=True, as_of=AS_OF,
        timing_context={"lat": 34.7304, "lon": -86.5861, "timezone_offset": -5},
        jyotish_ayanamsa="raman", jyotish_lunar_node="true",
    )
    assert with_timing["systems"]["jyotish"]["calculation"]["ayanamsa"]["name"] == "Raman"
    assert with_timing["systems"]["jyotish"]["calculation"]["lunar_nodes"]["mode"] == "true"
    assert {"vimshottari", "transits", "secondary_progressions", "solar_arc", "solar_return",
            "annual_profection", "zodiacal_releasing", "planetary_hours"} <= set(with_timing["timing"])
    assert with_timing["timing_policy"]["zodiacal_releasing_status"] == "level_1_only"
    assert with_timing["convergence_policy"]["timing_excluded_from_static_convergence"] is True
