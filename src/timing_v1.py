"""Versioned timing artifacts derived from explicit astronomical conventions."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

try:
    import swisseph as swe
except ImportError:  # pragma: no cover
    swe = None

from encoders.jyotish import compute_jyotish, SIGNS
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
TROPICAL_PLANETS = {
    "Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3, "Mars": 4,
    "Jupiter": 5, "Saturn": 6, "Uranus": 7, "Neptune": 8, "Pluto": 9,
}
MAJOR_ASPECTS = {0: "Conjunction", 60: "Sextile", 90: "Square", 120: "Trine", 180: "Opposition"}
CLASSICAL_RULERS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
]
CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
WEEKDAY_RULERS = {
    0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter", 4: "Venus", 5: "Saturn", 6: "Sun",
}
ZR_SIGN_YEARS = [15.0, 8.0, 20.0, 25.0, 19.0, 20.0, 8.0, 15.0, 12.0, 27.0, 30.0, 12.0]


def _require_swe() -> None:
    if swe is None:
        raise RuntimeError("Swiss Ephemeris is required for timing calculations.")
    swe.set_ephe_path(None)


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


def _jd_from_datetime(value: datetime) -> float:
    utc = value.astimezone(timezone.utc)
    hour = utc.hour + utc.minute / 60.0 + utc.second / 3600.0 + utc.microsecond / 3_600_000_000.0
    return float(swe.julday(utc.year, utc.month, utc.day, hour))


def _datetime_from_jd(jd: float) -> datetime:
    year, month, day, hour = swe.revjul(jd, swe.GREG_CAL)
    whole_hour = int(hour)
    minute_float = (hour - whole_hour) * 60.0
    minute = int(minute_float)
    second = min(59, int(round((minute_float - minute) * 60.0)))
    return datetime(int(year), int(month), int(day), whole_hour, minute, second, tzinfo=timezone.utc)


def _sign(lon: float) -> dict[str, Any]:
    value = float(lon) % 360.0
    index = int(value // 30.0)
    return {"sign": SIGNS[index], "sign_index": index, "degree": round(value % 30.0, 6), "longitude": round(value, 6)}


def _positions(jd: float) -> dict[str, dict[str, Any]]:
    flags = swe.FLG_MOSEPH | swe.FLG_SPEED
    result: dict[str, dict[str, Any]] = {}
    for name, pid in TROPICAL_PLANETS.items():
        data = swe.calc_ut(jd, pid, flags)[0]
        item = _sign(data[0])
        item["speed_longitude"] = round(float(data[3]), 9)
        item["retrograde"] = float(data[3]) < 0
        result[name] = item
    return result


def _natal_frame(birth: dict[str, Any], *, require_coordinates: bool = False) -> tuple[datetime, float, dict[str, Any]]:
    required = {"year", "month", "day", "hour", "minute", "timezone_offset"}
    if require_coordinates:
        required |= {"lat", "lon"}
    missing = sorted(required - set(birth))
    if missing:
        raise ValueError(f"Missing required birth fields: {', '.join(missing)}")
    if birth.get("time_accuracy") == "unknown":
        raise ValueError("A known birth time is required for this timing artifact.")
    birth_utc = _birth_utc(birth)
    jd = _jd_from_datetime(birth_utc)
    frame: dict[str, Any] = {"planets": _positions(jd)}
    if require_coordinates:
        cusps, ascmc = swe.houses(jd, float(birth["lat"]), float(birth["lon"]), b"P")
        frame["ascendant"] = _sign(ascmc[0])
        frame["midheaven"] = _sign(ascmc[1])
        frame["house_cusps"] = [round(float(value) % 360.0, 6) for value in cusps]
    return birth_utc, jd, frame


def _input_insufficient(system_id: str, version: str, convention: str, source_ids: list[str], message: str,
                        dependency_roots: list[str] | None = None, input_dependencies: list[str] | None = None) -> dict[str, Any]:
    return system_result(
        system_id,
        system_version=version,
        tradition="Astrological timing",
        convention=convention,
        artifact_class="timing",
        epistemic_class="deterministic_calculation",
        dependency_roots=dependency_roots or ["birth_instant"],
        input_dependencies=input_dependencies or ["birth.date", "birth.local_time", "birth.utc_offset", "as_of"],
        calculation={},
        source_ids=source_ids,
        sensitivity="personal",
        license_info={"calculation_code": "project-authored", "third_party_dependencies": ["pyswisseph AGPL-3.0-or-later"]},
        status="input_insufficient",
        limitations=[message],
    )


def compute_vimshottari(
    birth: dict[str, Any], *, as_of: date | datetime | str | None = None, ayanamsa: str = "lahiri",
) -> dict[str, Any]:
    natal = compute_jyotish(birth, ayanamsa=ayanamsa)
    aya_name = ayanamsa.strip().lower()
    base_kwargs = dict(
        system_version="vimshottari-v2",
        tradition="Jyotish / Vimshottari Dasha",
        convention=f"{aya_name}-nakshatra-mean-tropical-year-v2",
        artifact_class="timing",
        epistemic_class="deterministic_calculation",
        dependency_roots=["birth_instant"],
        input_dependencies=["birth.date", "birth.local_time", "birth.utc_offset", "birth.coordinates", "moon.sidereal_longitude", "as_of(optional)"],
        source_ids=["SRC-JYOTISH-VIMSHOTTARI", "SRC-JYOTISH-NAKSHATRA"],
        sensitivity="personal",
        license_info={"calculation_code": "project-authored", "third_party_dependencies": ["pyswisseph AGPL-3.0-or-later"]},
    )
    if natal.get("status") != "computed":
        return system_result("vimshottari", calculation={}, status="input_insufficient",
                             limitations=["Vimshottari requires the same complete birth inputs as the sidereal Moon calculation."], **base_kwargs)
    moon = natal["calculation"]["planets"]["Moon"]
    nak = moon["nakshatra"]
    lord = nak["ruler"]
    lord_index = VIMSHOTTARI_SEQUENCE.index(lord)
    remaining_fraction = max(0.0, min(1.0, (NAKSHATRA_SPAN - float(nak["degree_within"])) / NAKSHATRA_SPAN))
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
        periods.append({"lord": period_lord, "duration_years": round(nominal, 9),
                        "start_utc": cursor.isoformat().replace("+00:00", "Z"),
                        "end_utc": end.isoformat().replace("+00:00", "Z"), "partial_at_birth": first})
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
        "ayanamsa": natal["calculation"]["ayanamsa"],
        "birth_moon": {"longitude": moon["longitude"], "nakshatra": nak["name"], "nakshatra_ruler": lord,
                       "degree_within_nakshatra": nak["degree_within"]},
        "birth_dasha_balance": {"lord": lord, "remaining_fraction": round(remaining_fraction, 9), "remaining_years": round(balance_years, 9)},
        "sequence": list(VIMSHOTTARI_SEQUENCE), "nominal_years": dict(VIMSHOTTARI_YEARS),
        "year_length_days": CONVENTIONAL_YEAR_DAYS, "mahadasha_periods": periods,
        "as_of_utc": as_of_utc.isoformat().replace("+00:00", "Z") if as_of_utc else None, "active_mahadasha": active,
    }
    return system_result("vimshottari", calculation=calculation,
                         limitations=["This artifact computes period boundaries; it does not predict events or outcomes.",
                                      "Calendar dates use a disclosed mean tropical year of 365.2425 days; traditions using another year convention will differ slightly.",
                                      "The schedule inherits uncertainty from birth time, timezone, coordinates, ayanamsa, and Moon longitude."], **base_kwargs)


def compute_transits(birth: dict[str, Any], *, as_of: date | datetime | str | None) -> dict[str, Any]:
    _require_swe()
    as_of_utc = _parse_as_of(as_of)
    sources = ["SRC-SWISSEPH-PLANETS", "SRC-TIMING-TRANSITS"]
    if as_of_utc is None:
        return _input_insufficient("transits", "transits-v1", "tropical-geocentric-major-aspects-1deg-v1", sources, "transits-v1 requires an explicit as_of time.")
    try:
        birth_utc, _, natal = _natal_frame(birth)
    except ValueError as exc:
        return _input_insufficient("transits", "transits-v1", "tropical-geocentric-major-aspects-1deg-v1", sources, str(exc))
    if as_of_utc < birth_utc:
        return _input_insufficient("transits", "transits-v1", "tropical-geocentric-major-aspects-1deg-v1", sources, "as_of precedes the birth instant.")
    current = _positions(_jd_from_datetime(as_of_utc))
    contacts: list[dict[str, Any]] = []
    for transit_name, transit in current.items():
        for natal_name, natal_item in natal["planets"].items():
            separation = abs(float(transit["longitude"]) - float(natal_item["longitude"]))
            separation = min(separation, 360.0 - separation)
            for angle, aspect_name in MAJOR_ASPECTS.items():
                orb = abs(separation - angle)
                if orb <= 1.0:
                    contacts.append({"transit": transit_name, "natal": natal_name, "aspect": aspect_name,
                                     "exact_angle": angle, "separation": round(separation, 6), "orb": round(orb, 6)})
                    break
    contacts.sort(key=lambda item: (item["orb"], item["transit"], item["natal"]))
    return system_result("transits", system_version="transits-v1", tradition="Astrological transits",
                         convention="tropical-geocentric-major-aspects-1deg-v1", artifact_class="timing",
                         epistemic_class="deterministic_calculation", dependency_roots=["birth_instant"],
                         input_dependencies=["birth.date", "birth.local_time", "birth.utc_offset", "as_of"],
                         calculation={"zodiac": "tropical", "as_of_utc": as_of_utc.isoformat().replace("+00:00", "Z"),
                                      "natal_positions": natal["planets"], "transit_positions": current,
                                      "major_aspect_orb_degrees": 1.0, "contacts": contacts},
                         source_ids=sources, sensitivity="personal",
                         license_info={"calculation_code": "project-authored", "third_party_dependencies": ["pyswisseph AGPL-3.0-or-later"]},
                         limitations=["Aspect contacts use a fixed one-degree computational orb and are not predictions.",
                                      "This v1 artifact is geocentric and tropical; topocentric and mundane models are not blended in."])


def compute_secondary_progressions(birth: dict[str, Any], *, as_of: date | datetime | str | None) -> dict[str, Any]:
    _require_swe()
    as_of_utc = _parse_as_of(as_of)
    convention = "day-for-year-mean-tropical-year-v1"
    sources = ["SRC-SWISSEPH-PLANETS", "SRC-TIMING-SECONDARY-PROGRESSIONS"]
    if as_of_utc is None:
        return _input_insufficient("secondary_progressions", "secondary-progressions-v1", convention, sources,
                                   "secondary-progressions-v1 requires an explicit as_of time.")
    try:
        _, natal_jd, natal = _natal_frame(birth)
    except ValueError as exc:
        return _input_insufficient("secondary_progressions", "secondary-progressions-v1", convention, sources, str(exc))
    as_of_jd = _jd_from_datetime(as_of_utc)
    elapsed_days = as_of_jd - natal_jd
    if elapsed_days < 0:
        return _input_insufficient("secondary_progressions", "secondary-progressions-v1", convention, sources, "as_of precedes the birth instant.")
    symbolic_days = elapsed_days / CONVENTIONAL_YEAR_DAYS
    progressed_jd = natal_jd + symbolic_days
    progressed_dt = _datetime_from_jd(progressed_jd)
    return system_result("secondary_progressions", system_version="secondary-progressions-v1", tradition="Secondary progressions",
                         convention=convention, artifact_class="timing", epistemic_class="deterministic_calculation",
                         dependency_roots=["birth_instant"], input_dependencies=["birth.date", "birth.local_time", "birth.utc_offset", "as_of"],
                         calculation={"zodiac": "tropical", "as_of_utc": as_of_utc.isoformat().replace("+00:00", "Z"),
                                      "elapsed_days": round(elapsed_days, 9), "symbolic_days_after_birth": round(symbolic_days, 9),
                                      "progressed_ephemeris_utc": progressed_dt.isoformat().replace("+00:00", "Z"),
                                      "natal_positions": natal["planets"], "progressed_positions": _positions(progressed_jd),
                                      "year_length_days": CONVENTIONAL_YEAR_DAYS},
                         source_ids=sources, sensitivity="personal",
                         license_info={"calculation_code": "project-authored", "third_party_dependencies": ["pyswisseph AGPL-3.0-or-later"]},
                         limitations=["This uses the disclosed day-for-a-year convention with 365.2425 days per symbolic year.",
                                      "v1 progresses planetary longitudes only; progressed houses and angles are intentionally excluded."])


def compute_solar_arc(birth: dict[str, Any], *, as_of: date | datetime | str | None) -> dict[str, Any]:
    _require_swe()
    as_of_utc = _parse_as_of(as_of)
    convention = "secondary-progressed-sun-arc-tropical-v1"
    deps = ["birth.date", "birth.local_time", "birth.utc_offset", "birth.coordinates", "as_of"]
    sources = ["SRC-SWISSEPH-PLANETS", "SRC-TIMING-SOLAR-ARC"]
    if as_of_utc is None:
        return _input_insufficient("solar_arc", "solar-arc-v1", convention, sources, "solar-arc-v1 requires an explicit as_of time.", input_dependencies=deps)
    try:
        _, natal_jd, natal = _natal_frame(birth, require_coordinates=True)
    except ValueError as exc:
        return _input_insufficient("solar_arc", "solar-arc-v1", convention, sources, str(exc), input_dependencies=deps)
    as_of_jd = _jd_from_datetime(as_of_utc)
    if as_of_jd < natal_jd:
        return _input_insufficient("solar_arc", "solar-arc-v1", convention, sources, "as_of precedes the birth instant.", input_dependencies=deps)
    symbolic_days = (as_of_jd - natal_jd) / CONVENTIONAL_YEAR_DAYS
    progressed_jd = natal_jd + symbolic_days
    progressed_sun = _positions(progressed_jd)["Sun"]["longitude"]
    natal_sun = natal["planets"]["Sun"]["longitude"]
    arc = (float(progressed_sun) - float(natal_sun)) % 360.0
    directed: dict[str, dict[str, Any]] = {}
    targets = {**natal["planets"], "Ascendant": natal["ascendant"], "Midheaven": natal["midheaven"]}
    for name, item in targets.items():
        directed[name] = _sign(float(item["longitude"]) + arc)
    return system_result("solar_arc", system_version="solar-arc-v1", tradition="Solar arc directions", convention=convention,
                         artifact_class="timing", epistemic_class="deterministic_calculation", dependency_roots=["birth_instant"],
                         input_dependencies=deps,
                         calculation={"zodiac": "tropical", "as_of_utc": as_of_utc.isoformat().replace("+00:00", "Z"),
                                      "symbolic_days_after_birth": round(symbolic_days, 9), "natal_sun_longitude": round(float(natal_sun), 6),
                                      "progressed_sun_longitude": round(float(progressed_sun), 6), "solar_arc_degrees": round(arc, 6),
                                      "directed_positions": directed, "year_length_days": CONVENTIONAL_YEAR_DAYS},
                         source_ids=sources, sensitivity="personal",
                         license_info={"calculation_code": "project-authored", "third_party_dependencies": ["pyswisseph AGPL-3.0-or-later"]},
                         limitations=["The same progressed-Sun arc is added to natal longitudes; this is a symbolic direction, not physical motion.",
                                      "v1 emits directed coordinates only and does not attach predictive meanings."])


def compute_solar_return(birth: dict[str, Any], *, as_of: date | datetime | str | None) -> dict[str, Any]:
    _require_swe()
    as_of_utc = _parse_as_of(as_of)
    convention = "tropical-sun-longitude-return-v1"
    deps = ["birth.date", "birth.local_time", "birth.utc_offset", "birth.coordinates", "as_of"]
    sources = ["SRC-SWISSEPH-SOLCROSS", "SRC-SWISSEPH-PLANETS", "SRC-TIMING-SOLAR-RETURN"]
    if as_of_utc is None:
        return _input_insufficient("solar_return", "solar-return-v1", convention, sources, "solar-return-v1 requires an explicit as_of time.", input_dependencies=deps)
    try:
        _, natal_jd, natal = _natal_frame(birth, require_coordinates=True)
    except ValueError as exc:
        return _input_insufficient("solar_return", "solar-return-v1", convention, sources, str(exc), input_dependencies=deps)
    as_of_jd = _jd_from_datetime(as_of_utc)
    if as_of_jd < natal_jd:
        return _input_insufficient("solar_return", "solar-return-v1", convention, sources, "as_of precedes the birth instant.", input_dependencies=deps)
    natal_sun = float(natal["planets"]["Sun"]["longitude"])
    flags = swe.FLG_MOSEPH
    cursor = float(swe.solcross_ut(natal_sun, as_of_jd - 400.0, flags))
    previous = None
    for _ in range(3):
        if cursor <= as_of_jd + 1e-9:
            previous = cursor
            cursor = float(swe.solcross_ut(natal_sun, cursor + 1e-5, flags))
        else:
            break
    next_return = cursor
    if previous is None:
        previous = float(swe.solcross_ut(natal_sun, as_of_jd - 800.0, flags))
        while True:
            candidate = float(swe.solcross_ut(natal_sun, previous + 1e-5, flags))
            if candidate > as_of_jd:
                next_return = candidate
                break
            previous = candidate
    return_positions = _positions(previous)
    cusps, ascmc = swe.houses(previous, float(birth["lat"]), float(birth["lon"]), b"P")
    return system_result("solar_return", system_version="solar-return-v1", tradition="Solar return", convention=convention,
                         artifact_class="timing", epistemic_class="deterministic_calculation", dependency_roots=["birth_instant"],
                         input_dependencies=deps,
                         calculation={"zodiac": "tropical", "as_of_utc": as_of_utc.isoformat().replace("+00:00", "Z"),
                                      "natal_sun_longitude": round(natal_sun, 6),
                                      "previous_return_utc": _datetime_from_jd(previous).isoformat().replace("+00:00", "Z"),
                                      "next_return_utc": _datetime_from_jd(next_return).isoformat().replace("+00:00", "Z"),
                                      "previous_return_chart": {"planets": return_positions, "ascendant": _sign(ascmc[0]),
                                                                "midheaven": _sign(ascmc[1]), "house_system": "Placidus",
                                                                "house_cusps": [round(float(value) % 360.0, 6) for value in cusps],
                                                                "location_basis": "birth_coordinates"}},
                         source_ids=sources, sensitivity="personal",
                         license_info={"calculation_code": "project-authored", "third_party_dependencies": ["pyswisseph AGPL-3.0-or-later"]},
                         limitations=["The return is the exact tropical ecliptic-longitude crossing of the natal Sun.",
                                      "The return chart is erected for stored birth coordinates; relocation requires an explicit separate location.",
                                      "No event prediction is attached to the return."])


def compute_annual_profection(birth: dict[str, Any], *, as_of: date | datetime | str | None) -> dict[str, Any]:
    _require_swe()
    as_of_utc = _parse_as_of(as_of)
    convention = "whole-sign-civil-birthday-classical-rulers-v1"
    deps = ["birth.date", "birth.local_time", "birth.utc_offset", "birth.coordinates", "as_of"]
    sources = ["SRC-PROFECTIONS-WHOLE-SIGN"]
    if as_of_utc is None:
        return _input_insufficient("annual_profection", "annual-profection-v1", convention, sources,
                                   "annual-profection-v1 requires an explicit as_of time.", input_dependencies=deps)
    try:
        _, _, natal = _natal_frame(birth, require_coordinates=True)
    except ValueError as exc:
        return _input_insufficient("annual_profection", "annual-profection-v1", convention, sources, str(exc), input_dependencies=deps)
    local_offset = timezone(timedelta(hours=float(birth["timezone_offset"])))
    local_now = as_of_utc.astimezone(local_offset)
    age = local_now.year - int(birth["year"])
    if (local_now.month, local_now.day) < (int(birth["month"]), int(birth["day"])):
        age -= 1
    if age < 0:
        return _input_insufficient("annual_profection", "annual-profection-v1", convention, sources, "as_of precedes the birth date.", input_dependencies=deps)
    asc_index = int(natal["ascendant"]["sign_index"])
    profected_house = age % 12 + 1
    activated_index = (asc_index + age) % 12
    return system_result("annual_profection", system_version="annual-profection-v1", tradition="Annual profections",
                         convention=convention, artifact_class="timing", epistemic_class="deterministic_calculation",
                         dependency_roots=["birth_instant"], input_dependencies=deps,
                         calculation={"zodiac": "tropical", "as_of_utc": as_of_utc.isoformat().replace("+00:00", "Z"),
                                      "completed_civil_years": age, "natal_rising_sign": natal["ascendant"]["sign"],
                                      "profected_house": profected_house, "activated_sign": SIGNS[activated_index],
                                      "activated_sign_index": activated_index, "lord_of_year": CLASSICAL_RULERS[activated_index],
                                      "ruler_scheme": "classical-seven-planet"},
                         source_ids=sources, sensitivity="personal",
                         license_info={"calculation_code": "project-authored", "third_party_dependencies": ["pyswisseph AGPL-3.0-or-later"]},
                         limitations=["v1 advances one whole sign per completed civil birthday from the natal rising sign.",
                                      "Classical sign rulers are used; modern outer-planet rulerships are not blended in.",
                                      "For Feb 29 births, the civil-age boundary remains Mar 1 in non-leap years under this implementation."])


def _sun_events_for_local_date(local_date: date, context: dict[str, Any]) -> tuple[float, float]:
    offset = timezone(timedelta(hours=float(context["timezone_offset"])))
    midnight_local = datetime(local_date.year, local_date.month, local_date.day, tzinfo=offset)
    start_jd = _jd_from_datetime(midnight_local.astimezone(timezone.utc))
    geopos = (float(context["lon"]), float(context["lat"]), float(context.get("altitude_m", 0.0)))
    flags = swe.FLG_MOSEPH
    rise_res, rise = swe.rise_trans(start_jd, swe.SUN, swe.CALC_RISE, geopos, 0.0, 0.0, flags)
    set_res, setting = swe.rise_trans(start_jd, swe.SUN, swe.CALC_SET, geopos, 0.0, 0.0, flags)
    if rise_res < 0 or set_res < 0:
        raise ValueError("Sunrise or sunset is unavailable for this date/location.")
    return float(rise[0]), float(setting[0])


def compute_planetary_hours(context: dict[str, Any], *, as_of: date | datetime | str | None) -> dict[str, Any]:
    _require_swe()
    as_of_utc = _parse_as_of(as_of)
    convention = "chaldean-sunrise-sunset-apparent-horizon-v1"
    required = {"lat", "lon", "timezone_offset"}
    missing = sorted(required - set(context))
    base = dict(system_version="planetary-hours-v1", tradition="Planetary hours / chronocrators", convention=convention,
                artifact_class="timing", epistemic_class="deterministic_calculation", dependency_roots=["environment_context"],
                input_dependencies=["timing_context.coordinates", "timing_context.utc_offset", "as_of"],
                source_ids=["SRC-SWISSEPH-RISE-SET", "SRC-PLANETARY-HOURS-CHALDEAN"], sensitivity="personal",
                license_info={"calculation_code": "project-authored", "third_party_dependencies": ["pyswisseph AGPL-3.0-or-later"]})
    if as_of_utc is None or missing:
        return system_result("planetary_hours", calculation={}, status="input_insufficient",
                             limitations=["planetary-hours-v1 requires explicit as_of plus timing-context latitude, longitude, and UTC offset."], **base)
    offset = timezone(timedelta(hours=float(context["timezone_offset"])))
    local_now = as_of_utc.astimezone(offset)
    try:
        today_rise, today_set = _sun_events_for_local_date(local_now.date(), context)
        if _jd_from_datetime(as_of_utc) < today_rise:
            base_date = local_now.date() - timedelta(days=1)
            rise_jd, set_jd = _sun_events_for_local_date(base_date, context)
            next_rise, _ = _sun_events_for_local_date(local_now.date(), context)
        else:
            base_date = local_now.date()
            rise_jd, set_jd = today_rise, today_set
            next_rise, _ = _sun_events_for_local_date(base_date + timedelta(days=1), context)
    except ValueError as exc:
        return system_result("planetary_hours", calculation={}, status="unavailable", limitations=[str(exc)], **base)
    now_jd = _jd_from_datetime(as_of_utc)
    if rise_jd <= now_jd < set_jd:
        phase = "day"
        segment = (set_jd - rise_jd) / 12.0
        index = min(11, max(0, int((now_jd - rise_jd) / segment)))
        hour_number = index + 1
        start = rise_jd + index * segment
        end = start + segment
        sequence_offset = index
    else:
        phase = "night"
        segment = (next_rise - set_jd) / 12.0
        index = min(11, max(0, int((now_jd - set_jd) / segment)))
        hour_number = index + 13
        start = set_jd + index * segment
        end = start + segment
        sequence_offset = 12 + index
    day_ruler = WEEKDAY_RULERS[base_date.weekday()]
    first_index = CHALDEAN_ORDER.index(day_ruler)
    ruler = CHALDEAN_ORDER[(first_index + sequence_offset) % len(CHALDEAN_ORDER)]
    return system_result("planetary_hours",
                         calculation={"as_of_utc": as_of_utc.isoformat().replace("+00:00", "Z"), "local_date_basis": base_date.isoformat(),
                                      "day_ruler": day_ruler, "chaldean_order": list(CHALDEAN_ORDER),
                                      "sunrise_utc": _datetime_from_jd(rise_jd).isoformat().replace("+00:00", "Z"),
                                      "sunset_utc": _datetime_from_jd(set_jd).isoformat().replace("+00:00", "Z"),
                                      "next_sunrise_utc": _datetime_from_jd(next_rise).isoformat().replace("+00:00", "Z"),
                                      "phase": phase, "planetary_hour_number": hour_number, "ruler": ruler,
                                      "hour_start_utc": _datetime_from_jd(start).isoformat().replace("+00:00", "Z"),
                                      "hour_end_utc": _datetime_from_jd(end).isoformat().replace("+00:00", "Z"),
                                      "segment_length_minutes": round(segment * 24.0 * 60.0, 6)},
                         limitations=["Hours divide sunrise-to-sunset and sunset-to-next-sunrise into twelve equal temporal hours.",
                                      "Swiss Ephemeris rise/set defaults are used; local terrain horizon and custom atmosphere are not modeled.",
                                      "This is an environmental timing artifact and is not independent evidence about a person."], **base)


def compute_zodiacal_releasing(birth: dict[str, Any], *, as_of: date | datetime | str | None = None, lot: str = "spirit") -> dict[str, Any]:
    _require_swe()
    lot_key = lot.strip().lower()
    if lot_key not in {"fortune", "spirit"}:
        raise ValueError("zodiacal-releasing-l1-v1 lot must be 'fortune' or 'spirit'.")
    convention = "valens-l1-fortune-spirit-365.2425day-v1"
    deps = ["birth.date", "birth.local_time", "birth.utc_offset", "birth.coordinates", "as_of(optional)"]
    sources = ["SRC-ZODIACAL-RELEASING-VALENS"]
    try:
        birth_utc, natal_jd, natal = _natal_frame(birth, require_coordinates=True)
    except ValueError as exc:
        return _input_insufficient("zodiacal_releasing", "zodiacal-releasing-l1-v1", convention, sources, str(exc), input_dependencies=deps)
    sun = natal["planets"]["Sun"]
    moon = natal["planets"]["Moon"]
    asc = natal["ascendant"]
    sun_raw = swe.calc_ut(natal_jd, swe.SUN, swe.FLG_MOSEPH)[0]
    _, sun_true_altitude, _ = swe.azalt(natal_jd, swe.ECL2HOR,
        (float(birth["lon"]), float(birth["lat"]), float(birth.get("altitude_m", 0.0))), 0.0, 0.0,
        (float(sun_raw[0]), float(sun_raw[1]), float(sun_raw[2])))
    sect = "day" if float(sun_true_altitude) >= 0.0 else "night"
    asc_lon, sun_lon, moon_lon = float(asc["longitude"]), float(sun["longitude"]), float(moon["longitude"])
    if sect == "day":
        fortune_lon = (asc_lon + moon_lon - sun_lon) % 360.0
        spirit_lon = (asc_lon + sun_lon - moon_lon) % 360.0
    else:
        fortune_lon = (asc_lon + sun_lon - moon_lon) % 360.0
        spirit_lon = (asc_lon + moon_lon - sun_lon) % 360.0
    lots = {"fortune": _sign(fortune_lon), "spirit": _sign(spirit_lon)}
    start_index = int(lots[lot_key]["sign_index"])
    periods: list[dict[str, Any]] = []
    cursor = birth_utc
    for offset in range(12):
        sign_index = (start_index + offset) % 12
        years = ZR_SIGN_YEARS[sign_index]
        end = cursor + timedelta(days=years * CONVENTIONAL_YEAR_DAYS)
        periods.append({"sign": SIGNS[sign_index], "sign_index": sign_index, "ruler": CLASSICAL_RULERS[sign_index],
                        "duration_years": years, "start_utc": cursor.isoformat().replace("+00:00", "Z"),
                        "end_utc": end.isoformat().replace("+00:00", "Z")})
        cursor = end
    as_of_utc = _parse_as_of(as_of)
    active = None
    if as_of_utc is not None and birth_utc <= as_of_utc < cursor:
        for period in periods:
            start = datetime.fromisoformat(period["start_utc"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(period["end_utc"].replace("Z", "+00:00"))
            if start <= as_of_utc < end:
                active = dict(period)
                break
    return system_result("zodiacal_releasing", system_version="zodiacal-releasing-l1-v1", tradition="Hellenistic zodiacal releasing",
                         convention=convention, artifact_class="timing", epistemic_class="deterministic_calculation",
                         dependency_roots=["birth_instant"], input_dependencies=deps,
                         calculation={"zodiac": "tropical", "sect": sect, "sun_true_altitude_degrees": round(float(sun_true_altitude), 6),
                                      "lots": lots, "selected_lot": lot_key,
                                      "sign_period_years": {SIGNS[i]: ZR_SIGN_YEARS[i] for i in range(12)},
                                      "year_length_days": CONVENTIONAL_YEAR_DAYS, "level_1_periods": periods,
                                      "level_1_cycle_years": sum(ZR_SIGN_YEARS),
                                      "as_of_utc": as_of_utc.isoformat().replace("+00:00", "Z") if as_of_utc else None,
                                      "active_level_1": active},
                         source_ids=sources, sensitivity="personal",
                         license_info={"calculation_code": "project-authored", "third_party_dependencies": ["pyswisseph AGPL-3.0-or-later"]},
                         limitations=["v1 implements Level 1 only from Fortune or Spirit; deeper levels and loosing-of-the-bond are not yet emitted.",
                                      "Sect is determined from the Sun's true astronomical altitude at birth.",
                                      "Calendar boundaries use the disclosed 365.2425-day normalization; alternative historical dating conventions can shift dates.",
                                      "This artifact provides period coordinates only and does not predict events."])


__all__ = [
    "compute_vimshottari", "compute_transits", "compute_secondary_progressions", "compute_solar_arc",
    "compute_solar_return", "compute_annual_profection", "compute_planetary_hours", "compute_zodiacal_releasing",
    "VIMSHOTTARI_SEQUENCE", "VIMSHOTTARI_YEARS",
]
