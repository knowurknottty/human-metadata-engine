from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any

from .astronomy import civil_to_julian_day, planetary_positions, solve_design_jd
from .constants import CHANNELS, MANDALA_VERSION
from .mandala import map_longitude
from .topology import build_topology, resolve_authority, resolve_definition, resolve_type

ENGINE_VERSION = "true-human-design-core-v1"
RULE_SET_VERSION = "compatibility-rules-v1"

STRATEGIES = {
    "Manifestor": "Inform before initiating",
    "Generator": "Respond",
    "Manifesting Generator": "Respond, then inform",
    "Projector": "Wait for recognition and invitation",
    "Reflector": "Wait a lunar cycle",
}


@dataclass(frozen=True)
class BirthRecord:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone_name: str
    latitude: float | None = None
    longitude: float | None = None
    second: int = 0
    fold: int = 0
    subject_id: str | None = None


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _activation_dict(position) -> dict[str, Any]:
    mapped = map_longitude(position.longitude)
    return {
        "body": position.body,
        "julian_day": position.julian_day,
        "longitude": position.longitude,
        "latitude": position.latitude,
        "speed_longitude": position.speed_longitude,
        "retrograde": position.retrograde,
        "gate": mapped.gate,
        "line": mapped.line,
        "fraction_within_gate": mapped.fraction_within_gate,
        "distance_to_previous_gate_boundary": mapped.distance_to_previous_boundary,
        "distance_to_next_gate_boundary": mapped.distance_to_next_boundary,
        "mapping_version": mapped.mapping_version,
        "ephemeris_profile": position.ephemeris_profile,
        "calculation_flags": position.calculation_flags,
    }


def _resolution(value: str, reasons: tuple[str, ...] | list[str], rejected: tuple[str, ...] | list[str] = ()) -> dict[str, Any]:
    return {"value": value, "reasons": list(reasons), "rejected": list(rejected)}


def _serialize_topology(topology) -> dict[str, Any]:
    channel_rows = []
    for first_gate, second_gate in topology.channels:
        centers = CHANNELS[(first_gate, second_gate)]
        channel_rows.append({"gates": [first_gate, second_gate], "centers": list(centers)})
    all_centers = {"Head", "Ajna", "Throat", "G", "Heart", "Sacral", "Spleen", "Solar Plexus", "Root"}
    return {
        "active_gates": sorted(topology.active_gates),
        "channels": channel_rows,
        "defined_centers": sorted(topology.defined_centers),
        "undefined_centers": sorted(all_centers - set(topology.defined_centers)),
        "edges": [list(edge) for edge in topology.edges],
        "components": [sorted(component) for component in topology.components],
        "motor_to_throat": topology.motor_to_throat,
        "motor_to_throat_paths": [list(path) for path in topology.motor_to_throat_paths],
    }


def calculate_chart(
    record: BirthRecord,
    *,
    expected_result: dict[str, Any] | None = None,
    include_private_input: bool = False,
    node_mode: str = "true",
) -> dict[str, Any]:
    raw_input = asdict(record)
    input_fingerprint = _sha256(raw_input)

    time_ledger = civil_to_julian_day(
        record.year,
        record.month,
        record.day,
        record.hour,
        record.minute,
        record.timezone_name,
        second=record.second,
        fold=record.fold,
    )
    design_solve = solve_design_jd(time_ledger.julian_day)
    personality_positions = planetary_positions(time_ledger.julian_day, node_mode=node_mode)
    design_positions = planetary_positions(design_solve.design_jd, node_mode=node_mode)

    personality = {name: _activation_dict(position) for name, position in personality_positions.items()}
    design = {name: _activation_dict(position) for name, position in design_positions.items()}
    active_gates = {row["gate"] for row in personality.values()} | {row["gate"] for row in design.values()}

    topology = build_topology(active_gates)
    type_resolution = resolve_type(topology)
    authority_resolution = resolve_authority(topology)
    definition_resolution = resolve_definition(topology)

    personality_sun_line = personality["Sun"]["line"]
    design_sun_line = design["Sun"]["line"]
    profile = f"{personality_sun_line}/{design_sun_line}"
    cross = {
        "personality_sun": personality["Sun"]["gate"],
        "personality_earth": personality["Earth"]["gate"],
        "design_sun": design["Sun"]["gate"],
        "design_earth": design["Earth"]["gate"],
    }
    cross_value = "/".join(str(cross[key]) for key in (
        "personality_sun", "personality_earth", "design_sun", "design_earth"
    ))

    calculated = {
        "engine_version": ENGINE_VERSION,
        "rule_set_version": RULE_SET_VERSION,
        "mandala_version": MANDALA_VERSION,
        "node_mode": node_mode,
        "personality_jd": time_ledger.julian_day,
        "design_jd": design_solve.design_jd,
        "activations": {"personality": personality, "design": design},
        "topology": _serialize_topology(topology),
        "resolutions": {
            "type": _resolution(type_resolution.value, type_resolution.reasons, type_resolution.rejected),
            "strategy": _resolution(STRATEGIES[type_resolution.value], (f"strategy associated with calculated Type {type_resolution.value}",)),
            "authority": _resolution(authority_resolution.value, authority_resolution.reasons, authority_resolution.rejected),
            "definition": _resolution(definition_resolution.value, definition_resolution.reasons, definition_resolution.rejected),
            "profile": _resolution(profile, (f"Personality Sun line {personality_sun_line}", f"Design Sun line {design_sun_line}")),
            "cross_signature": _resolution(cross_value, tuple(f"{key} gate {value}" for key, value in cross.items())),
        },
    }
    calculation_hash = _sha256(calculated)

    expected = dict(expected_result or {})
    comparison = {
        "expected_type": expected.get("type"),
        "calculated_type": type_resolution.value,
        "type_matches": expected.get("type") == type_resolution.value if expected.get("type") else None,
        "expected_profile": expected.get("profile"),
        "calculated_profile": profile,
        "profile_matches": expected.get("profile") == profile if expected.get("profile") else None,
        "expected_authority": expected.get("authority"),
        "calculated_authority": authority_resolution.value,
        "authority_matches": expected.get("authority") == authority_resolution.value if expected.get("authority") else None,
    }

    result = {
        "status": "provisional_calculation",
        "symbolic_status": "Human Design is treated as a symbolic interpretive system, not empirical psychology.",
        "activations": calculated["activations"],
        "topology": calculated["topology"],
        "resolutions": calculated["resolutions"],
        "comparison": comparison,
        "ledger": {
            "engine_version": ENGINE_VERSION,
            "rule_set_version": RULE_SET_VERSION,
            "mandala_version": MANDALA_VERSION,
            "node_mode": node_mode,
            "input_fingerprint": input_fingerprint,
            "calculation_hash": calculation_hash,
            "time": {
                "timezone_name": time_ledger.timezone_name,
                "utc_offset_hours": time_ledger.utc_offset_hours,
                "personality_jd": time_ledger.julian_day,
            },
            "design_solver": asdict(design_solve),
        },
    }
    if include_private_input:
        result["private_input"] = raw_input
        result["ledger"]["time"].update({"local_iso": time_ledger.local_iso, "utc_iso": time_ledger.utc_iso})
    return result


__all__ = ["BirthRecord", "calculate_chart"]
