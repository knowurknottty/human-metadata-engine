"""Shared v3 result contracts for heterogeneous human-metadata systems."""
from __future__ import annotations

from collections import Counter
from typing import Any

SYSTEM_RESULT_VERSION = "system-result-v2"
SIGNATURE_V3 = "signature-v3"

ARTIFACT_CLASSES = {
    "static_signature", "timing", "divination_session", "assessment", "environment", "biometric",
}
EPISTEMIC_CLASSES = {
    "deterministic_calculation", "deterministic_relationship",
    "traditional_symbolic_interpretation", "user_supplied", "measured_observation",
    "interpretive_synthesis",
}
DEPENDENCY_ROOTS = {
    "birth_instant", "birth_date", "name_string", "assessment_instrument",
    "session_entropy", "environment_context", "biometric_observation",
}
SENSITIVITY_CLASSES = {"public", "personal", "sensitive"}
DEPENDENCY_FAMILIES = {
    "birth_instant": "birth", "birth_date": "birth", "name_string": "name",
    "assessment_instrument": "assessment", "session_entropy": "session",
    "environment_context": "environment", "biometric_observation": "biometric",
}


def system_result(
    system_id: str,
    *,
    system_version: str,
    tradition: str,
    convention: str,
    artifact_class: str,
    epistemic_class: str,
    dependency_roots: list[str],
    calculation: dict[str, Any],
    source_ids: list[str],
    input_dependencies: list[str] | None = None,
    interpretation: dict[str, Any] | None = None,
    limitations: list[str] | None = None,
    sensitivity: str = "personal",
    license_info: dict[str, Any] | None = None,
    status: str = "computed",
) -> dict[str, Any]:
    if artifact_class not in ARTIFACT_CLASSES:
        raise ValueError(f"unsupported artifact_class: {artifact_class}")
    if epistemic_class not in EPISTEMIC_CLASSES:
        raise ValueError(f"unsupported epistemic_class: {epistemic_class}")
    unknown_roots = set(dependency_roots) - DEPENDENCY_ROOTS
    if unknown_roots:
        raise ValueError(f"unsupported dependency roots: {sorted(unknown_roots)}")
    if sensitivity not in SENSITIVITY_CLASSES:
        raise ValueError(f"unsupported sensitivity: {sensitivity}")
    if status not in {"computed", "input_insufficient", "unavailable"}:
        raise ValueError(f"unsupported status: {status}")
    return {
        "contract_version": SYSTEM_RESULT_VERSION,
        "system_id": system_id,
        "system_version": system_version,
        "tradition": tradition,
        "convention": convention,
        "artifact_class": artifact_class,
        "epistemic_class": epistemic_class,
        "input_dependencies": sorted(set(input_dependencies or [])),
        "dependency_roots": sorted(set(dependency_roots)),
        "sensitivity": sensitivity,
        "status": status,
        "calculation": calculation,
        "interpretation": interpretation or {},
        "provenance": {"source_ids": list(dict.fromkeys(source_ids))},
        "license": license_info or {
            "calculation_code": "project-authored",
            "third_party_dependencies": [],
        },
        "limitations": list(limitations or []),
    }


def summarize_systems(systems: dict[str, Any]) -> dict[str, Any]:
    valid = [item for item in systems.values() if isinstance(item, dict)]
    root_counts = Counter(root for item in valid for root in item.get("dependency_roots", []))
    family_counts: Counter[str] = Counter()
    for item in valid:
        families = {
            DEPENDENCY_FAMILIES[root]
            for root in item.get("dependency_roots", [])
            if root in DEPENDENCY_FAMILIES
        }
        family_counts.update(families)
    return {
        "system_count": len(valid),
        "lens_count": len(valid),
        "available_system_count": sum(item.get("status") == "computed" for item in valid),
        "raw_dependency_root_count": len(root_counts),
        "independence_family_count": len(family_counts),
        "independence_families": dict(family_counts),
        "artifact_classes": dict(Counter(item.get("artifact_class", "unknown") for item in valid)),
        "epistemic_classes": dict(Counter(item.get("epistemic_class", "unknown") for item in valid)),
        "dependency_roots": dict(root_counts),
        "computed_field_count": sum(
            len(item.get("calculation", {}))
            for item in valid
            if item.get("status") == "computed" and isinstance(item.get("calculation"), dict)
        ),
    }


__all__ = ["system_result", "summarize_systems", "SIGNATURE_V3", "SYSTEM_RESULT_VERSION"]
