#!/usr/bin/env python3
"""Run and persist every provenance-backed public-figure reference record."""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analytics import feature_vector, identity_similarity_matrix  # noqa: E402
from engine import compute_unified_signature  # noqa: E402
from persistence import IdentityDB  # noqa: E402
from reference_population import load_famous_reference_catalog  # noqa: E402


def git_revision() -> str:
    build_revision = os.environ.get("HME_BUILD_REVISION", "").strip()
    if build_revision:
        return build_revision
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def validate_population(catalog: dict, signatures: list[dict], vectors: list[list[float]],
                        comparison: dict) -> dict:
    """Fail closed if catalog provenance or comparison math is malformed."""
    records = catalog["records"]
    qids = [record.get("qid") for record in records]
    ids = [record.get("id") for record in records]
    failures = []
    if catalog.get("exclusions"):
        failures.append("catalog has unresolved exclusions")
    if len(qids) != len(set(qids)):
        failures.append("catalog contains duplicate Wikidata QIDs")
    if len(ids) != len(set(ids)):
        failures.append("catalog contains duplicate record IDs")
    for record in records:
        provenance = record.get("provenance", {})
        if record.get("calculation_status") != "core_only":
            failures.append(f"{record.get('qid')}: not marked core_only")
        if not provenance.get("wikidata_url") or not provenance.get("enwiki_url"):
            failures.append(f"{record.get('qid')}: missing source URL")
    for index, vector in enumerate(vectors):
        if len(vector) != 14 or any(not math.isfinite(value) or not 0 <= value <= 1 for value in vector):
            failures.append(f"{signatures[index]['id']}: invalid feature vector")
    matrix = comparison.get("matrix", {})
    if comparison.get("metric") != "feature_agreement_v1":
        failures.append("comparison metric is not feature_agreement_v1")
    for left in comparison.get("ids", []):
        if matrix.get(left, {}).get(left) != 1.0:
            failures.append(f"{left}: comparison diagonal is not 1.0")
        for right, score in matrix.get(left, {}).items():
            if not 0 <= score <= 1 or score != matrix.get(right, {}).get(left):
                failures.append(f"{left}/{right}: comparison matrix is invalid")
                break
    if failures:
        raise ValueError("Public reference validation failed: " + "; ".join(failures[:10]))
    return {
        "passed": True,
        "catalog_records": len(records),
        "feature_vectors_checked": len(vectors),
        "matrix_cells_checked": len(records) ** 2,
    }


def main() -> int:
    catalog = load_famous_reference_catalog()
    records = catalog["records"]
    output = ROOT / "output"
    output.mkdir(exist_ok=True)
    db = IdentityDB(str(output / "famous_people.sqlite"))
    signatures = []
    vectors = []
    revision = git_revision()
    try:
        db.conn.execute("BEGIN")
        for record in records:
            signature = compute_unified_signature({"id": record["id"], "text": record["text"]})
            vector = feature_vector(signature)
            db.store_reference_signature(record, signature, vector, revision, commit=False)
            signatures.append(signature)
            vectors.append(vector)
        db.prune_reference_population([record["qid"] for record in records], commit=False)
        similarity = identity_similarity_matrix(signatures)
        validation_check = validate_population(catalog, signatures, vectors, similarity)
        validation = {
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "catalog_record_count": len(records),
            "stored": db.reference_stats(),
            "engine_revision": revision,
            "birth_encoder_policy": "core_only unless a separately sourced, verified birth time is added",
            "comparison": similarity,
            "validation": validation_check,
        }
        (output / "famous_people_validation.json").write_text(
            json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        db.conn.commit()
    except Exception:
        db.conn.rollback()
        raise
    finally:
        db.close()
    print(f"Stored {len(signatures)} public-figure signatures in output/famous_people.sqlite")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
