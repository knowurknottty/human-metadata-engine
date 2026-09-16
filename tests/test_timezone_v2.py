from __future__ import annotations

from datetime import datetime, timezone

import pytest

from time_context import TimezoneResolutionError, resolve_local_datetime, timezone_basis_for_instant
from timing_v2 import compute_annual_profection, compute_planetary_hours


BIRTH_IANA = {
    "year": 2000, "month": 1, "day": 7,
    "hour": 12, "minute": 0,
    "timezone_id": "Asia/Shanghai",
    "location": "Beijing, China", "lat": 39.9042, "lon": 116.4074,
    "time_accuracy": "exact",
}


def test_iana_fall_back_requires_explicit_fold():
    context = {"timezone_id": "America/New_York"}
    with pytest.raises(TimezoneResolutionError, match="ambiguous"):
        resolve_local_datetime(2020, 11, 1, 1, 30, context)

    first = resolve_local_datetime(2020, 11, 1, 1, 30, {**context, "timezone_fold": 0})
    second = resolve_local_datetime(2020, 11, 1, 1, 30, {**context, "timezone_fold": 1})
    assert first["effective_offset_hours"] == -4.0
    assert second["effective_offset_hours"] == -5.0
    assert first["utc_datetime"] != second["utc_datetime"]


def test_iana_spring_gap_fails_closed():
    with pytest.raises(TimezoneResolutionError, match="does not exist"):
        resolve_local_datetime(2020, 3, 8, 2, 30, {"timezone_id": "America/New_York"})


def test_iana_offset_changes_across_dst_transition():
    context = {"timezone_id": "America/New_York"}
    before = datetime(2026, 3, 8, 6, 30, tzinfo=timezone.utc)
    after = datetime(2026, 3, 8, 7, 30, tzinfo=timezone.utc)
    _, before_basis = timezone_basis_for_instant(context, before)
    _, after_basis = timezone_basis_for_instant(context, after)
    assert before_basis["effective_offset_hours"] == -5.0
    assert after_basis["effective_offset_hours"] == -4.0
    assert before_basis["model"] == "iana_zoneinfo"
    assert after_basis["model"] == "iana_zoneinfo"


def test_annual_profection_accepts_iana_birth_without_numeric_offset():
    result = compute_annual_profection(BIRTH_IANA, as_of="2026-01-08T00:00:00Z")
    assert result["status"] == "computed"
    calc = result["calculation"]
    assert calc["birth_timezone_basis"]["model"] == "iana_zoneinfo"
    assert calc["birth_timezone_basis"]["timezone_id"] == "Asia/Shanghai"
    assert calc["completed_civil_years"] == 26


def test_planetary_hours_accepts_iana_context_and_reports_local_events():
    context = {
        "lat": 40.7128,
        "lon": -74.0060,
        "timezone_id": "America/New_York",
    }
    result = compute_planetary_hours(context, as_of="2026-03-08T12:00:00Z")
    assert result["status"] == "computed"
    calc = result["calculation"]
    assert calc["timezone_basis"]["model"] == "iana_zoneinfo"
    assert calc["timezone_basis"]["effective_offset_hours"] == -4.0
    assert "-04:00" in calc["as_of_local"]
    assert calc["sunrise_local"]
    assert calc["sunset_local"]
