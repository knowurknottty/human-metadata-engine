#!/usr/bin/env python3
"""Dependency-free structural checks for versioned JSON contracts."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_schema(filename: str) -> dict:
    path = ROOT / "schemas" / filename
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise SystemExit(f"{filename}: missing JSON Schema draft marker")
    if payload.get("type") != "object":
        raise SystemExit(f"{filename}: root must be an object")
    return payload


def main() -> int:
    for filename in ("analysis-v1.request.json", "analysis-v1.response.json"):
        _load_schema(filename)
    print("PUBLIC_CONTRACTS_VALID")

    system_schema = _load_schema("system-result-v2.schema.json")
    required = {
        "contract_version", "system_id", "system_version", "tradition", "convention",
        "artifact_class", "epistemic_class", "input_dependencies", "dependency_roots",
        "sensitivity", "status", "calculation", "interpretation", "provenance",
        "license", "limitations",
    }
    if not required <= set(system_schema.get("required", [])):
        raise SystemExit("system-result-v2.schema.json: incomplete required envelope")
    if system_schema.get("properties", {}).get("contract_version", {}).get("const") != "system-result-v2":
        raise SystemExit("system-result-v2.schema.json: contract_version const mismatch")
    print("SYSTEM_RESULT_V2_SCHEMA_VALID")

    evidence_schema = _load_schema("synthesis-evidence-v2.schema.json")
    if evidence_schema.get("properties", {}).get("schema_version", {}).get("const") != "synthesis-evidence-v2":
        raise SystemExit("synthesis-evidence-v2.schema.json: schema_version const mismatch")
    required_evidence = {"schema_version", "analysis_id", "evidence_items", "packet_digest"}
    if not required_evidence <= set(evidence_schema.get("required", [])):
        raise SystemExit("synthesis-evidence-v2.schema.json: incomplete required packet identity")
    print("SYNTHESIS_EVIDENCE_V2_SCHEMA_VALID")

    household_schema = _load_schema("household-v1.schema.json")
    if household_schema.get("properties", {}).get("contract_version", {}).get("const") != "household-v1":
        raise SystemExit("household-v1.schema.json: contract_version const mismatch")
    print("HOUSEHOLD_V1_SCHEMA_VALID")

    relational_schema = _load_schema("relational-view-v1.schema.json")
    if relational_schema.get("properties", {}).get("schema_version", {}).get("const") != "relational-view-v1":
        raise SystemExit("relational-view-v1.schema.json: schema_version const mismatch")
    print("RELATIONAL_VIEW_V1_SCHEMA_VALID")

    child_schema = _load_schema("child-profile-v1.schema.json")
    if child_schema.get("properties", {}).get("contract_version", {}).get("const") != "child-profile-v1":
        raise SystemExit("child-profile-v1.schema.json: contract_version const mismatch")
    print("CHILD_PROFILE_V1_SCHEMA_VALID")

    pet_schema = _load_schema("pet-profile-v1.schema.json")
    if pet_schema.get("properties", {}).get("contract_version", {}).get("const") != "pet-profile-v1":
        raise SystemExit("pet-profile-v1.schema.json: contract_version const mismatch")
    print("PET_PROFILE_V1_SCHEMA_VALID")

    release_schema = _load_schema("release-manifest-v1.schema.json")
    if release_schema.get("properties", {}).get("schema_version", {}).get("const") != "human-manual-release-manifest-v1":
        raise SystemExit("release-manifest-v1.schema.json: schema_version const mismatch")
    print("RELEASE_MANIFEST_V1_SCHEMA_VALID")

    household_schema = _load_schema("household-v1.schema.json")
    if household_schema.get("properties", {}).get("contract_version", {}).get("const") != "household-v1":
        raise SystemExit("household-v1.schema.json: contract_version const mismatch")
    relational_schema = _load_schema("relational-view-v1.schema.json")
    if relational_schema.get("properties", {}).get("schema_version", {}).get("const") != "relational-view-v1":
        raise SystemExit("relational-view-v1.schema.json: schema_version const mismatch")
    child_schema = _load_schema("child-profile-v1.schema.json")
    if child_schema.get("properties", {}).get("contract_version", {}).get("const") != "child-profile-v1":
        raise SystemExit("child-profile-v1.schema.json: contract_version const mismatch")
    pet_schema = _load_schema("pet-profile-v1.schema.json")
    if pet_schema.get("properties", {}).get("contract_version", {}).get("const") != "pet-profile-v1":
        raise SystemExit("pet-profile-v1.schema.json: contract_version const mismatch")
    projection_schema = _load_schema("household-subject-projection-v1.schema.json")
    if projection_schema.get("properties", {}).get("projection_version", {}).get("const") != "household-subject-projection-v1":
        raise SystemExit("household-subject-projection-v1.schema.json: projection_version const mismatch")
    entitlement_schema = _load_schema("entitlement-v1.schema.json")
    if entitlement_schema.get("properties", {}).get("schema_version", {}).get("const") != "entitlement-v1":
        raise SystemExit("entitlement-v1.schema.json: schema_version const mismatch")
    print("HOUSEHOLD_CONTRACTS_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
