"""Public Human Design adapter backed by the validated core engine.

This module is deliberately conservative at the product boundary.  A chart is
calculated only when the caller supplied a precise birth time and coordinates;
approximate or unknown times remain explicitly unavailable.  The adapter keeps
the legacy UI shape while retaining the versioned core ledger for auditability.
"""

from __future__ import annotations

from typing import Any

from .engine import BirthRecord, calculate_chart


KNOWN_TIME_ACCURACIES = {"exact", "provided"}


def _fixed_timezone_name(offset: float) -> str:
    total_minutes = round(float(offset) * 60)
    if abs(total_minutes - float(offset) * 60) > 1e-6:
        raise ValueError("timezone_offset must resolve to whole minutes")
    if not -14 * 60 <= total_minutes <= 14 * 60:
        raise ValueError("timezone_offset must be between -14 and +14")
    sign = "+" if total_minutes >= 0 else "-"
    magnitude = abs(total_minutes)
    return f"UTC{sign}{magnitude // 60:02d}:{magnitude % 60:02d}"


def unavailable_human_design(birth: dict[str, Any] | None) -> dict[str, Any]:
    accuracy = (birth or {}).get("time_accuracy", "unknown")
    return {
        "available": False,
        "status": "unavailable_uncertain_birth_time",
        "unavailable": "A known birth time with precise time_accuracy is required for Human Design output.",
        "reason": (
            "Human Design activations and the design-time calculation are withheld "
            f"for time_accuracy={accuracy!r}; no noon or approximate-time result is used."
        ),
        "time_accuracy": accuracy,
        "epistemic_class": "symbolic-unavailable",
        "calculation_engine": "true-human-design-core-v1",
    }


def _display_center_name(name: str) -> str:
    return {
        "G": "G/Identity",
        "Heart": "Heart/Will",
        "Spleen": "Splenic",
    }.get(name, name)


def calculate_public_human_design(
    birth: dict[str, Any],
    *,
    subject_id: str | None = None,
) -> dict[str, Any]:
    """Calculate a redacted, provenance-labelled public chart.

    Numeric UTC offsets are accepted as explicit fixed-offset time zones.  This
    is deterministic, but it is not a claim that the offset captures historical
    DST rules; that distinction is surfaced in ``timezone_provenance``.
    """
    if not isinstance(birth, dict):
        raise ValueError("birth must be an object")
    accuracy = birth.get("time_accuracy", "unknown")
    if accuracy not in KNOWN_TIME_ACCURACIES:
        return unavailable_human_design(birth)
    required = ("year", "month", "day", "hour", "minute", "timezone_offset", "lat", "lon")
    missing = [field for field in required if birth.get(field) in (None, "")]
    if missing:
        raise ValueError(f"Human Design birth data missing: {', '.join(missing)}")

    timezone_name = birth.get("timezone_name") or _fixed_timezone_name(float(birth["timezone_offset"]))
    record = BirthRecord(
        year=int(birth["year"]),
        month=int(birth["month"]),
        day=int(birth["day"]),
        hour=int(birth["hour"]),
        minute=int(birth["minute"]),
        timezone_name=str(timezone_name),
        latitude=float(birth["lat"]),
        longitude=float(birth["lon"]),
        subject_id=subject_id,
    )
    chart = calculate_chart(record, include_private_input=False)
    # Keep the audit ledger useful without returning the caller's raw IANA zone
    # (or any other input identity) through a nested public payload.
    public_chart = dict(chart)
    public_ledger = dict(chart["ledger"])
    public_time = dict(public_ledger["time"])
    public_time.pop("timezone_name", None)
    public_ledger["time"] = public_time
    public_chart["ledger"] = public_ledger
    resolutions = chart["resolutions"]
    topology = chart["topology"]

    personality = chart["activations"]["personality"]
    design = chart["activations"]["design"]
    personality_gates = [
        {"gate": row["gate"], "line": row["line"], "planet": body, "longitude": row["longitude"]}
        for body, row in personality.items()
    ]
    design_gates = [
        {"gate": row["gate"], "line": row["line"], "planet": body, "longitude": row["longitude"]}
        for body, row in design.items()
    ]
    channels = [
        {
            "gates": list(channel["gates"]),
            "centers": [_display_center_name(center) for center in channel["centers"]],
            "name": f"Gates {channel['gates'][0]}–{channel['gates'][1]}",
            "label_kind": "gate-pair",
        }
        for channel in topology["channels"]
    ]
    centers = [
        {
            "name": _display_center_name(name),
            "defined": name in topology["defined_centers"],
            "core_name": name,
        }
        for name in ("Head", "Ajna", "Throat", "G", "Heart", "Solar Plexus", "Sacral", "Spleen", "Root")
    ]

    return {
        "available": True,
        "status": chart["status"],
        "epistemic_class": "symbolic-calculation",
        "calculation_engine": chart["ledger"]["engine_version"],
        "calculation_standard": "true-human-design-core-v1",
        "timezone_provenance": "explicit_iana" if birth.get("timezone_name") else "provided_utc_offset",
        "timezone_rules_note": (
            "IANA timezone rules supplied by caller."
            if birth.get("timezone_name")
            else "Fixed UTC offset supplied by caller; historical DST rules were not inferred."
        ),
        "time_accuracy": accuracy,
        "type": resolutions["type"]["value"],
        "strategy": resolutions["strategy"]["value"],
        "authority": resolutions["authority"]["value"],
        "definition": resolutions["definition"]["value"],
        "profile": [int(part) for part in resolutions["profile"]["value"].split("/")],
        "incarnation_cross": resolutions["cross_signature"]["value"],
        "personality_gates": personality_gates,
        "design_gates": design_gates,
        "gates": sorted(topology["active_gates"]),
        "channels": channels,
        "centers": centers,
        "confidence": None,
        "confidence_note": "No empirical confidence score is assigned; inspect the calculation ledger and input accuracy.",
        "true_engine": public_chart,
    }


__all__ = ["calculate_public_human_design", "unavailable_human_design"]
