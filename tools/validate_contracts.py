#!/usr/bin/env python3
"""Dependency-free structural checks for versioned public JSON contracts."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    for filename in ("analysis-v1.request.json", "analysis-v1.response.json"):
        path = ROOT / "schemas" / filename
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        if payload.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            raise SystemExit(f"{filename}: missing JSON Schema draft marker")
        if payload.get("type") != "object":
            raise SystemExit(f"{filename}: root must be an object")
    print("PUBLIC_CONTRACTS_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
