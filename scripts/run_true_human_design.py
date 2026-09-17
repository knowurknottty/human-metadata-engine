#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from true_human_design.engine import BirthRecord, calculate_chart


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the True Human Design core on a private birth record.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--include-private-input", action="store_true")
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    expected = payload.pop("expected_result", None)
    record = BirthRecord(**payload)
    chart = calculate_chart(record, expected_result=expected, include_private_input=args.include_private_input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(chart, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "status": chart["status"],
        "calculation_hash": chart["ledger"]["calculation_hash"],
        "type": chart["resolutions"]["type"]["value"],
        "profile": chart["resolutions"]["profile"]["value"],
        "authority": chart["resolutions"]["authority"]["value"],
        "output": str(args.output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
