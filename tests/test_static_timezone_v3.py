from __future__ import annotations

import math

from encoders.bazi import compute_bazi
from encoders.jyotish import compute_jyotish


def _ny_birth(**overrides):
    value = {
        "year": 2024,
        "month": 7,
        "day": 1,
        "hour": 12,
        "minute": 0,
        "timezone_id": "America/New_York",
        "timezone_offset": -5,
        "lat": 40.7128,
        "lon": -74.0060,
        "time_accuracy": "exact",
    }
    value.update(overrides)
    return value


def test_static_system_versions_record_zone_aware_contracts():
    birth = _ny_birth()
    bazi = compute_bazi(birth)
    jyotish = compute_jyotish(birth)
    assert bazi["system_version"] == "bazi-v2"
    assert jyotish["system_version"] == "jyotish-v3"
    assert bazi["calculation"]["timezone_basis"]["model"] == "iana_zoneinfo"
    assert jyotish["calculation"]["timezone_basis"]["model"] == "iana_zoneinfo"


def test_iana_zone_overrides_stale_numeric_offset_for_static_calculation():
    iana = _ny_birth(timezone_offset=-5)
    fixed = dict(iana)
    fixed.pop("timezone_id")
    fixed["timezone_offset"] = -4

    bazi_iana = compute_bazi(iana)
    bazi_fixed = compute_bazi(fixed)
    jyotish_iana = compute_jyotish(iana)
    jyotish_fixed = compute_jyotish(fixed)

    bazi_basis = bazi_iana["calculation"]["timezone_basis"]
    jyotish_basis = jyotish_iana["calculation"]["timezone_basis"]
    assert bazi_basis["effective_offset_hours"] == -4.0
    assert jyotish_basis["effective_offset_hours"] == -4.0
    assert bazi_basis["supplied_offset_mismatch"] is True
    assert jyotish_basis["supplied_offset_mismatch"] is True
    assert math.isclose(
        bazi_iana["calculation"]["solar_longitude"],
        bazi_fixed["calculation"]["solar_longitude"],
        abs_tol=1e-6,
    )
    assert math.isclose(
        jyotish_iana["calculation"]["planets"]["Sun"]["longitude"],
        jyotish_fixed["calculation"]["planets"]["Sun"]["longitude"],
        abs_tol=1e-6,
    )


def test_ambiguous_fall_back_birth_requires_fold_in_static_systems():
    ambiguous = _ny_birth(year=2024, month=11, day=3, hour=1, minute=30)
    ambiguous.pop("timezone_offset")
    for result in (compute_bazi(ambiguous), compute_jyotish(ambiguous)):
        assert result["status"] == "input_insufficient"
        assert "ambiguous" in result["limitations"][0].lower()

    fold0 = {**ambiguous, "timezone_fold": 0}
    fold1 = {**ambiguous, "timezone_fold": 1}
    first = compute_jyotish(fold0)
    second = compute_jyotish(fold1)
    assert first["status"] == "computed"
    assert second["status"] == "computed"
    assert first["calculation"]["timezone_basis"]["fold"] == 0
    assert second["calculation"]["timezone_basis"]["fold"] == 1
    assert first["calculation"]["timezone_basis"]["birth_utc_iso"] != second["calculation"]["timezone_basis"]["birth_utc_iso"]


def test_nonexistent_spring_forward_birth_fails_closed_in_static_systems():
    gap = _ny_birth(year=2024, month=3, day=10, hour=2, minute=30)
    gap.pop("timezone_offset")
    for result in (compute_bazi(gap), compute_jyotish(gap)):
        assert result["status"] == "input_insufficient"
        assert "does not exist" in result["limitations"][0]


def test_unknown_time_bazi_uses_zone_rules_across_transition_day():
    birth = {
        "year": 2024,
        "month": 3,
        "day": 10,
        "timezone_id": "America/New_York",
        "time_accuracy": "unknown",
    }
    result = compute_bazi(birth)
    assert result["status"] == "computed"
    calc = result["calculation"]
    assert calc["pillars"]["hour"] is None
    basis = calc["timezone_basis"]
    assert basis["model"] == "iana_zoneinfo"
    assert basis["day_start_effective_offset_hours"] == -5.0
    assert basis["day_end_effective_offset_hours"] == -4.0
