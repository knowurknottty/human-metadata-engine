from __future__ import annotations

from datetime import datetime, timedelta, timezone

from signature_v3 import compute_signature_v3
from zodiacal_releasing_v2 import (
    ZR_LEVEL_UNIT_DAYS,
    _apply_spirit_same_sign_rule,
    _generate_subperiods,
    compute_zodiacal_releasing,
)


BIRTH = {
    "year": 2000, "month": 1, "day": 7,
    "hour": 12, "minute": 0, "timezone_offset": 8,
    "timezone_id": "Asia/Shanghai",
    "location": "Beijing, China", "lat": 39.9042, "lon": 116.4074,
    "time_accuracy": "exact",
}


def test_capricorn_l2_matches_published_360_day_loosing_example():
    start = datetime(1974, 11, 10, tzinfo=timezone.utc)
    parent_end = start + timedelta(days=27 * 360)
    rows = _generate_subperiods(9, start, parent_end, 2)
    assert rows[0]["sign"] == "Capricorn"
    assert rows[0]["start_utc"].startswith("1974-11-10")
    assert rows[1]["sign"] == "Aquarius"
    assert rows[1]["start_utc"].startswith("1977-01-28")
    assert rows[11]["sign"] == "Sagittarius"
    assert rows[11]["start_utc"].startswith("1991-03-16")
    assert rows[12]["sign"] == "Cancer"
    assert rows[12]["start_utc"].startswith("1992-03-10")
    assert rows[12]["loosing_of_bond"] is True


def test_recursive_level_units_and_lower_level_loosing():
    assert ZR_LEVEL_UNIT_DAYS == {1: 360.0, 2: 30.0, 3: 2.5, 4: 5.0 / 24.0}
    start = datetime(2000, 1, 1, tzinfo=timezone.utc)
    l2_parent_end = start + timedelta(days=20 * 30)
    l3 = _generate_subperiods(2, start, l2_parent_end, 3)
    assert l3[0]["sign"] == "Gemini"
    assert l3[0]["nominal_duration_days"] == 50.0
    assert l3[12]["sign"] == "Sagittarius"
    assert l3[12]["loosing_of_bond"] is True

    l3_parent_end = start + timedelta(days=20 * 2.5)
    l4 = _generate_subperiods(2, start, l3_parent_end, 4)
    assert l4[0]["sign"] == "Gemini"
    assert abs(l4[0]["nominal_duration_days"] - (100.0 / 24.0)) < 1e-9
    assert l4[12]["sign"] == "Sagittarius"
    assert l4[12]["loosing_of_bond"] is True


def test_same_sign_spirit_rule_moves_release_start_only():
    moved, applied = _apply_spirit_same_sign_rule(4, 4)
    assert applied is True
    assert moved == 5
    unchanged, applied = _apply_spirit_same_sign_rule(4, 7)
    assert applied is False
    assert unchanged == 7


def test_zodiacal_releasing_v2_emits_active_l1_through_l4():
    result = compute_zodiacal_releasing(BIRTH, as_of="2026-09-16T00:00:00Z", lot="spirit")
    assert result["status"] == "computed"
    assert result["system_version"] == "zodiacal-releasing-v2"
    calc = result["calculation"]
    assert calc["calendar_model"] == "idealized_360_day_year_30_day_month_recursive_twelfths"
    assert calc["levels_emitted"] == [1, 2, 3, 4]
    assert calc["active_hierarchy"]["L1"] is not None
    assert calc["active_hierarchy"]["L2"] is not None
    assert calc["active_hierarchy"]["L3"] is not None
    assert calc["active_hierarchy"]["L4"] is not None
    assert calc["level_3_periods_active_parent"]
    assert calc["level_4_periods_active_parent"]
    assert calc["timezone_basis"]["model"] == "iana_zoneinfo"


def test_signature_v3_advertises_deep_zr_and_iana_timing_policy():
    identity = {"id": "human:test", "text": "Test Person", "birth": BIRTH}
    result = compute_signature_v3(
        identity,
        snapshot_fn=None,
        include_timing=True,
        as_of="2026-09-16T00:00:00Z",
        timing_context={"lat": 40.7128, "lon": -74.0060, "timezone_id": "America/New_York"},
    )
    policy = result["timing_policy"]
    assert policy["timezone_model"] == "iana_zoneinfo_preferred_fixed_offset_fallback"
    assert policy["ambiguous_local_time_requires_timezone_fold"] is True
    assert policy["zodiacal_releasing_status"] == "levels_1_through_4_with_loosing_of_bond"
    assert result["timing"]["zodiacal_releasing"]["system_version"] == "zodiacal-releasing-v2"
    assert result["timing"]["annual_profection"]["system_version"] == "annual-profection-v2"
    assert result["timing"]["planetary_hours"]["system_version"] == "planetary-hours-v2"
