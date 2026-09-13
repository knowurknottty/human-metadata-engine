"""Versioned timing artifacts derived from a frozen natal signature.

Timing outputs are deterministic calculations under explicit conventions. They
are kept outside the static identity signature and are never counted as an
independent confirmation of the natal systems they depend on.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from encoders.jyotish import compute_jyotish
from system_contracts import system_result

VIMSHOTTARI_SEQUENCE = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
]
VIMSHOTTARI_YEARS = {
    "Ketu": 7.0, "Venus": 20.0, "Sun": 6.0, "Moon": 10.0, "Mars": 7.0,
    "Rahu": 18.0, "Jupiter": 16.0, "Saturn": 19.0, "Mercury": 17.0,
}
NAKSHATRA_SPAN = 360.0 / 27.0
CONVENTIONAL_YEAR_DAYS = 365.2425


def _birth_utc(birth: dict[str, Any]) -> datetime:
    offset = timezone(timedelta(hours=float(birth["timezone_offset"])))
    local = datetime(
        int(birth["year"]), int(birth["month"]), int(birth["day"]),
        int(birth["hour"]), int(birth["minute"]), tzinfo=offset,
    )
    return local.astimezone(timezone.utc)


def _parse_as_of(value: date | datetime | str | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    if isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc) if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    raise TypeError("as_of must be date, datetime, ISO-8601 string, or None")


def compute_vimshottari(
    birth: dict[str, Any],
    *,
    as_of: date | datetime | str | None = None,
) -> dict[str, Any]:
    natal = compute_jyotish(birth)
    base_kwargs = dict(
        system_version="vimshottari-v1",
        tradition="Jyotish / Vimshottari Dasha",
        convention="lahiri-nakshatra-mean-tropical-year-v1",
        artifact_class="timing",
        epistemic_class="deterministic_calculation",
        dependency_roots=["birth_instant"],
        input_dependencies=[
            "birth.date", "birth.local_time", "birth.utc_offset",
            "birth.coordinates", "moon.sidereal_longitude", "as_of(optional)",
        ],
        source_ids=["SRC-JYOTISH-VIMSHOTTARI", "SRC-JYOTISH-NAKSHATRA"],
        sensitivity="personal",
        license_info={
            "calculation_code": "project-authored",
            "third_party_dependencies": ["pyswisseph AGPL-3.0-or-later"],
        },
    )
    if natal.get("status") != "computed":
        return system_result(
            "vimshottari", calculation={}, status="input_insufficient",
            limitations=["Vimshottari requires the same complete birth inputs as the sidereal Moon calculation."],
            **base_kwargs,
        )

    moon = natal["calculation"]["planets"]["Moon"]
    nak = moon["nakshatra"]
    lord = nak["ruler"]
    lord_index = VIMSHOTTARI_SEQUENCE.index(lord)
    remaining_fraction = max(
        0.0, min(1.0, (NAKSHATRA_SPAN - float(nak["degree_within"])) / NAKSHATRA_SPAN)
    )
    balance_years = VIMSHOTTARI_YEARS[lord] * remaining_fraction
    birth_utc = _birth_utc(birth)

    periods: list[dict[str, Any]] = []
    cursor = birth_utc
    elapsed_years = 0.0
    sequence_index = lord_index
    first = True
    while elapsed_years < 120.0 - 1e-9:
        period_lord = VIMSHOTTARI_SEQUENCE[sequence_index % len(VIMSHOTTARI_SEQUENCE)]
        nominal = balance_years if first else VIMSHOTTARI_YEARS[period_lord]
        nominal = min(nominal, 120.0 - elapsed_years)
        end = cursor + timedelta(days=nominal * CONVENTIONAL_YEAR_DAYS)
        periods.append({
            "lord": period_lord,
            "duration_years": round(nominal, 9),
            "start_utc": cursor.isoformat().replace("+00:00", "Z"),
            "end_utc": end.isoformat().replace("+00:00", "Z"),
            "partial_at_birth": first,
        })
        cursor = end
        elapsed_years += nominal
        sequence_index += 1
        first = False

    as_of_utc = _parse_as_of(as_of)
    active = None
    if as_of_utc is not None and as_of_utc >= birth_utc:
        for period in periods:
            start = datetime.fromisoformat(period["start_utc"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(period["end_utc"].replace("Z", "+00:00"))
            if start <= as_of_utc < end:
                active = dict(period)
                break

    calculation = {
        "birth_moon": {
            "longitude": moon["longitude"], "nakshatra": nak["name"],
            "nakshatra_ruler": lord, "degree_within_nakshatra": nak["degree_within"],
        },
        "birth_dasha_balance": {
            "lord": lord, "remaining_fraction": round(remaining_fraction, 9),
            "remaining_years": round(balance_years, 9),
        },
        "sequence": list(VIMSHOTTARI_SEQUENCE),
        "nominal_years": dict(VIMSHOTTARI_YEARS),
        "year_length_days": CONVENTIONAL_YEAR_DAYS,
        "mahadasha_periods": periods,
        "as_of_utc": as_of_utc.isoformat().replace("+00:00", "Z") if as_of_utc else None,
        "active_mahadasha": active,
    }
    return system_result(
        "vimshottari", calculation=calculation,
        limitations=[
            "This artifact computes period boundaries; it does not predict events or outcomes.",
            "Calendar dates use a disclosed mean tropical year of 365.2425 days; traditions using another year convention will differ slightly.",
            "The schedule inherits uncertainty from the supplied birth time, timezone, coordinates, ayanamsa, and Moon longitude.",
        ],
        **base_kwargs,
    )


__all__ = ["compute_vimshottari", "VIMSHOTTARI_SEQUENCE", "VIMSHOTTARI_YEARS"]
