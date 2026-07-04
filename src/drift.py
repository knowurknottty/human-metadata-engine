"""
Temporal Identity Drift Tracker
================================

Track how identity signatures change across life stages.
Since encoders are deterministic, drift comes from INPUT changes
(name changes, marriage, nickname, cultural shifts).

Usage:
    from src.drift import track_drift
    drift = track_drift("Captain", ["Captain", "KnowUrKnot", "The Captain"])
"""

import json
import math
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DriftPoint:
    stage: str
    name_used: str
    resonance: float
    vector: dict
    delta_from_previous: float = 0.0


@dataclass
class DriftReport:
    identity: str
    stages: list
    total_drift: float
    drift_direction: str
    stability_score: float  # 0=volatile, 100=stable
    analysis: str


def track_drift(identity_name: str, name_variants: list, signatures_func=None) -> DriftReport:
    """Track identity drift across name variants.

    Args:
        identity_name: The canonical identity name
        name_variants: List of name strings to compare
        signatures_func: Function that returns unified signature for a name.
                        If None, uses compute_unified_signature.
    """
    if signatures_func is None:
        from engine import compute_unified_signature
        def signatures_func(name):
            return compute_unified_signature({"name": name, "id": name})

    stages = []
    for i, variant in enumerate(name_variants):
        try:
            sig = signatures_func(variant)
            resonance = _get_resonance(sig)
            vector = _flatten(sig)
            delta = 0.0
            if stages:
                delta = _cosine_distance(stages[-1].vector, vector)
            stages.append(DriftPoint(
                stage=f"Stage {i + 1}",
                name_used=variant,
                resonance=resonance,
                vector=vector,
                delta_from_previous=delta,
            ))
        except Exception as e:
            stages.append(DriftPoint(
                stage=f"Stage {i + 1}",
                name_used=variant,
                resonance=0,
                vector={},
                delta_from_previous=0,
            ))

    # Compute total drift
    if len(stages) >= 2:
        total_drift = _cosine_distance(stages[0].vector, stages[-1].vector)
    else:
        total_drift = 0.0

    # Direction
    if len(stages) >= 2:
        if stages[-1].resonance > stages[0].resonance + 5:
            direction = "ascending — later variants show stronger resonance"
        elif stages[-1].resonance < stages[0].resonance - 5:
            direction = "descending — earlier variants show stronger resonance"
        else:
            direction = "stable — resonance is consistent across variants"
    else:
        direction = "single stage — no drift to measure"

    # Stability score
    deltas = [s.delta_from_previous for s in stages[1:]]
    avg_delta = sum(deltas) / len(deltas) if deltas else 0
    stability = max(0, min(100, 100 - avg_delta * 500))

    # Analysis
    analysis = _generate_drift_analysis(stages, total_drift, stability)

    return DriftReport(
        identity=identity_name,
        stages=stages,
        total_drift=total_drift,
        drift_direction=direction,
        stability_score=round(stability, 1),
        analysis=analysis,
    )


def _get_resonance(sig: dict) -> float:
    analytics = sig.get("analytics", {})
    return analytics.get("composite_resonance", analytics.get("resonance_score", 0)) or 0


def _flatten(sig: dict) -> dict:
    vec = {}
    for enc_name, enc_data in sig.get("encoders", {}).items():
        if isinstance(enc_data, dict):
            for k, v in enc_data.items():
                if isinstance(v, (int, float)):
                    vec[f"{enc_name}_{k}"] = float(v)
    return vec


def _cosine_distance(a: dict, b: dict) -> float:
    keys = set(a.keys()) & set(b.keys())
    if not keys:
        return 1.0
    dot = sum(a[k] * b[k] for k in keys)
    mag_a = math.sqrt(sum(a[k] ** 2 for k in keys))
    mag_b = math.sqrt(sum(b[k] ** 2 for k in keys))
    if mag_a == 0 or mag_b == 0:
        return 1.0
    sim = dot / (mag_a * mag_b)
    return 1.0 - sim


def _generate_drift_analysis(stages, total_drift, stability):
    parts = []
    if len(stages) < 2:
        parts.append("Only one name variant provided. Drift analysis requires at least two variants.")
        return " ".join(parts)

    if stability > 80:
        parts.append("This identity is remarkably stable across name variants. The core encoding pattern persists regardless of how the name is expressed.")
    elif stability > 50:
        parts.append("This identity shows moderate stability. Some encoder dimensions shift between name variants, but the core pattern is recognizable.")
    else:
        parts.append("This identity is highly sensitive to name variants. Different expressions of the same identity produce significantly different signatures.")

    resonances = [s.resonance for s in stages]
    if max(resonances) - min(resonances) > 15:
        best = max(stages, key=lambda s: s.resonance)
        worst = min(stages, key=lambda s: s.resonance)
        parts.append(f"The strongest resonance is '{best.name_used}' ({best.resonance:.0f}) and the weakest is '{worst.name_used}' ({worst.resonance:.0f}).")

    return " ".join(parts)
