"""Opt-in signature-v3 composition layer.

signature-v2 remains the public compatibility contract. v3 adds typed system
artifacts without flattening them into the legacy encoder map.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from engine import compute_unified_signature
from encoders.bazi import compute_bazi
from encoders.jyotish import compute_jyotish
from encoders.maya_classical import compute_classical_maya
from system_contracts import SIGNATURE_V3, summarize_systems
from timing_v1 import (
    compute_annual_profection,
    compute_planetary_hours,
    compute_secondary_progressions,
    compute_solar_arc,
    compute_solar_return,
    compute_transits,
    compute_vimshottari,
    compute_zodiacal_releasing,
)


def compute_signature_v3(
    identity: dict[str, Any],
    *,
    as_of: Any | None = None,
    include_timing: bool = False,
    timing_context: dict[str, Any] | None = None,
    jyotish_ayanamsa: str = "lahiri",
    jyotish_lunar_node: str = "mean",
    **legacy_kwargs: Any,
) -> dict[str, Any]:
    base = compute_unified_signature(identity, **legacy_kwargs)
    result = deepcopy(base)
    legacy_contract = result.get("contract_version", "signature-v2")
    result["contract_version"] = SIGNATURE_V3
    result["legacy_contract_version"] = legacy_contract

    birth = identity.get("birth")
    systems: dict[str, dict[str, Any]] = {}
    if birth:
        systems["bazi"] = compute_bazi(birth)
        systems["jyotish"] = compute_jyotish(birth, ayanamsa=jyotish_ayanamsa, lunar_node=jyotish_lunar_node)
        systems["maya_classical"] = compute_classical_maya(birth)
    result["systems"] = systems
    result["system_manifest"] = summarize_systems(systems)

    timing: dict[str, dict[str, Any]] = {}
    if include_timing and birth:
        timing["vimshottari"] = compute_vimshottari(birth, as_of=as_of, ayanamsa=jyotish_ayanamsa)
        if as_of is not None:
            timing["transits"] = compute_transits(birth, as_of=as_of)
            timing["secondary_progressions"] = compute_secondary_progressions(birth, as_of=as_of)
            timing["solar_arc"] = compute_solar_arc(birth, as_of=as_of)
            timing["solar_return"] = compute_solar_return(birth, as_of=as_of)
            timing["annual_profection"] = compute_annual_profection(birth, as_of=as_of)
            timing["zodiacal_releasing"] = compute_zodiacal_releasing(birth, as_of=as_of, lot="spirit")
    if include_timing and timing_context is not None and as_of is not None:
        timing["planetary_hours"] = compute_planetary_hours(timing_context, as_of=as_of)

    result["timing"] = timing
    result["timing_manifest"] = summarize_systems(timing)
    result["artifacts"] = {"static_signature": systems, "timing": timing}
    result["convergence_policy"] = {
        "unit": "dependency_family",
        "rule": "Systems sharing a dependency family are multiple lenses, not independent confirmations.",
        "raw_dependency_roots": sorted({root for item in systems.values() for root in item.get("dependency_roots", [])}),
        "independence_families": sorted(result["system_manifest"].get("independence_families", {})),
        "timing_excluded_from_static_convergence": True,
    }
    result["timing_policy"] = {
        "requires_explicit_as_of_for_dynamic_artifacts": True,
        "planetary_hours_require_separate_timing_context": True,
        "timezone_model": "explicit_fixed_utc_offset_no_iana_dst_resolution",
        "zodiacal_releasing_status": "level_1_only",
    }
    return result


__all__ = ["compute_signature_v3"]
