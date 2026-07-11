#!/usr/bin/env python3
"""Canonical test runner for this repository's mixed unittest/script suite."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    tests = sorted((root / "tests").glob("test_*.py"))
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(root / "src"), str(root / "webapp"), env.get("PYTHONPATH", "")])
    failures = []
    for test_file in tests:
        command = [sys.executable, str(test_file)]
        completed = subprocess.run(
            command,
            cwd=root,
            env=env,
            stdout=subprocess.DEVNULL if args.quiet else None,
            stderr=subprocess.STDOUT if args.quiet else None,
        )
        if completed.returncode:
            failures.append(test_file.name)
            if args.quiet:
                print(f"FAIL {test_file.name}", file=sys.stderr)
    print(f"Test files: {len(tests)}; failures: {len(failures)}")
    if failures:
        print("Failed: " + ", ".join(failures), file=sys.stderr)
        return 1
    print("ALL_TESTS_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
