from signature_v3 import compute_signature_v3


BIRTH = {
    "year": 2000, "month": 1, "day": 7,
    "hour": 12, "minute": 0, "timezone_offset": 8,
    "location": "Beijing, China", "lat": 39.9042, "lon": 116.4074,
    "time_accuracy": "exact",
}


def test_timing_policy_declares_fixed_offset_timezone_model():
    result = compute_signature_v3(
        {"id": "human:test", "text": "Test Person", "birth": BIRTH},
        snapshot_fn=None,
    )
    policy = result["timing_policy"]
    assert policy["requires_explicit_as_of_for_dynamic_artifacts"] is True
    assert policy["planetary_hours_require_separate_timing_context"] is True
    assert policy["timezone_model"] == "explicit_fixed_utc_offset_no_iana_dst_resolution"
