from __future__ import annotations

from dataclasses import dataclass
import math

from .constants import GATE_SPAN, HD_START_DEGREE, LINE_SPAN, MANDALA_SEQUENCE, MANDALA_VERSION


@dataclass(frozen=True)
class GateActivation:
    longitude: float
    gate: int
    line: int
    fraction_within_gate: float
    distance_to_previous_boundary: float
    distance_to_next_boundary: float
    mapping_version: str = MANDALA_VERSION


def map_longitude(longitude: float) -> GateActivation:
    if not math.isfinite(longitude):
        raise ValueError("longitude must be finite")
    normalized = longitude % 360.0
    adjusted = (normalized - HD_START_DEGREE) % 360.0
    index = min(int(adjusted / GATE_SPAN), 63)
    offset = adjusted - index * GATE_SPAN
    line = min(int(offset / LINE_SPAN) + 1, 6)
    fraction = offset / GATE_SPAN
    return GateActivation(
        longitude=normalized,
        gate=MANDALA_SEQUENCE[index],
        line=line,
        fraction_within_gate=fraction,
        distance_to_previous_boundary=offset,
        distance_to_next_boundary=GATE_SPAN - offset,
    )


__all__ = ["GATE_SPAN", "MANDALA_SEQUENCE", "GateActivation", "map_longitude"]
