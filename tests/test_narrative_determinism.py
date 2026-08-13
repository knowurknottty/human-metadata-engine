"""Stable IDs, rankings, plans, prose, and metadata tests."""

import json

from narrative_helpers import exact_payload
from server import analyze


def test_identical_inputs_produce_identical_synthesis_bytes():
    first = analyze(exact_payload())["synthesis"]
    second = analyze(exact_payload())["synthesis"]
    encoded_first = json.dumps(first, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    encoded_second = json.dumps(second, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    assert encoded_first == encoded_second
    assert '"generated_at":null' in encoded_first


def test_all_verifier_reports_pass_for_deterministic_output():
    synthesis = analyze(exact_payload())["synthesis"]
    assert all(report["valid"] for report in synthesis["verification"].values())
    assert synthesis["ai_realization"] == {"enabled": False, "required": False, "remote_provider_used": False}
