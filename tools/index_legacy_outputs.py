#!/usr/bin/env python3
"""Build a non-destructive cryptographic quarantine index for legacy output artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
INDEX = ROOT / "release" / "legacy-output-index.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    records = []
    if OUTPUT.exists():
        for path in sorted(item for item in OUTPUT.rglob("*") if item.is_file()):
            records.append({
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": digest(path),
                "public_status": "quarantined_historical",
                "active_evidence": False,
                "reason": "Pre-v2 generated output; preserved byte-for-byte and excluded from active synthesis evidence.",
            })
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "legacy-output-index-v1",
        "policy": "preserve_bytes_do_not_promote_to_active_evidence",
        "active_evidence_version": "synthesis-evidence-v2",
        "artifacts": records,
    }
    INDEX.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"LEGACY_OUTPUT_INDEXED {len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
