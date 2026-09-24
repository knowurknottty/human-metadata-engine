"""Collection count baseline gate (EN-06).

Compares current pytest collection counts to the checked-in baseline.
Divergence fails with an actionable message unless a same-PR changelog entry exists.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASELINE = os.path.join(ROOT, "tests", "COLLECTION_BASELINE.json")


def _collect_counts() -> tuple[int, int]:
    """Return (test_count, file_count) for current pytest collection."""
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([os.path.join(ROOT, "src"), os.path.join(ROOT, "webapp"), env.get("PYTHONPATH", "")])
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    combined = result.stdout + "\n" + result.stderr
    for line in combined.strip().splitlines():
        if "tests collected" in line:
            parts = line.split()
            test_count = int(parts[0])
            break
    else:
        raise RuntimeError(f"could not parse collect output: {combined}")
    files = [f for f in os.listdir(os.path.join(ROOT, "tests")) if f.startswith("test_") and f.endswith(".py")]
    return test_count, len(files)


def test_collection_baseline():
    with open(BASELINE, encoding="utf-8") as handle:
        baseline = json.load(handle)
    current_tests, current_files = _collect_counts()
    expected_tests = baseline["pytest_collect_tests"]
    expected_files = baseline["pytest_collect_files"]

    if current_tests != expected_tests or current_files != expected_files:
        raise AssertionError(
            "Collection count drift detected. Current: {} tests / {} files; "
            "Baseline: {} tests / {} files.\n"
            "If this change is intentional, update tests/COLLECTION_BASELINE.json "
            "and record a changelog entry in the same PR (docs/SIGNATURE_V3.md#convention-governance-protocol)."
            .format(current_tests, current_files, expected_tests, expected_files)
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))