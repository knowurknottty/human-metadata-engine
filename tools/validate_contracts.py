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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
