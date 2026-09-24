from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sys
from copy import deepcopy

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, "webapp"), os.path.join(ROOT, "src"), os.path.join(ROOT, "tests")]

from household import (
    ADULT_LABEL,
    CHILD_LABEL,
    PET_LABEL,
    HouseholdContractError,
    analysis_record,
    build_child_profile,
    build_pet_profile,
    compose_relational_view,
    new_household_id,
    new_subject_id,
    profile_record,
    record_digest,
    validate_household_manifest,
)
from entitlements import verify_entitlement_token
from narrative_helpers import exact_result


def authority(kind):
    return {"kind": kind, "attestation_version": "authority-v1"}


def entry(subject_id, role, subject_class, contract, digest, auth, state="resolved", membership="member"):
    return {
        "subject_id": subject_id,
        "subject_role": role,
        "subject_class": subject_class,
        "membership": membership,
        "record_contract": contract,
        "record_digest": digest,
        "record_state": state,
        "authority": authority(auth),
    }


def manifest(primary_id, other, *, composition="pair"):
    return {
        "contract_version": "household-v1",
        "household_id": new_household_id(),
        "composition": composition,
        "primary_subject_id": primary_id,
        "subjects": other,
        "requested_dimensions": [
            "composition_scope", "role_presence", "declared_relationship",
            "input_readiness", "system_availability", "evidence_state",
            "same_system_observations",
        ],
    }


def test_subject_ids_are_random_non_name_derived():
    ids = {new_subject_id() for _ in range(20)}
    assert len(ids) == 20
    assert all(value.startswith("subj_") and len(value) == 37 for value in ids)


def test_child_profile_invokes_only_child_safe_worksheets():
    subject_id = new_subject_id()
    profile = build_child_profile(
        subject_id=subject_id,
        display_alias="Example Child",
        age_band="child",
        authority=authority("guardian_attested"),
        birth={"year": 2018, "month": 6, "day": 10},
    )
    assert profile["label"] == CHILD_LABEL
    assert set(profile["worksheets"]) == {
        "unicode_codepoint", "sumerian_sexagesimal", "mandaean_duodecimal",
        "elder_futhark", "ogham",
    }
    assert not {"jyotish", "bazi", "maya_classical", "tarot", "astrology", "human_design"} & set(profile["worksheets"])


def test_pet_profile_never_runs_human_symbolic_engine():
    profile = build_pet_profile(
        subject_id=new_subject_id(),
        display_alias="Scout",
        species="dog",
        breed="mixed",
        authority=authority("owner_attested"),
    )
    assert profile["label"] == PET_LABEL
    assert profile["symbolic_systems"] == {}
    assert profile["interpretation_policy"] == "care_context_only"


def test_household_manifest_excludes_names_birth_data_and_result_bodies():
    result = exact_result()
    primary_id, partner_id = new_subject_id(), new_subject_id()
    primary = analysis_record(primary_id, result)
    partner = analysis_record(partner_id, result)
    serialized_projection = json.dumps(primary["payload"])
    assert "normalized_input" not in primary["payload"]
    assert "report" not in primary["payload"]
    assert result["normalized_input"]["name"] not in serialized_projection
    payload = manifest(primary_id, [
        entry(primary_id, "primary", "person_adult", "analysis-v1", primary["record_digest"], "self_attested"),
        entry(partner_id, "partner", "person_adult", "analysis-v1", partner["record_digest"], "adult_consent_attested"),
    ])
    assert validate_household_manifest(payload)["composition"] == "pair"
    bad = deepcopy(payload)
    bad["subjects"][1]["name"] = "Private Name"
    with pytest.raises(HouseholdContractError, match="Unexpected household subject fields"):
        validate_household_manifest(bad)


def test_pair_requires_exact_primary_partner():
    result = exact_result()
    p, c = new_subject_id(), new_subject_id()
    pr = analysis_record(p, result)
    child = build_child_profile(subject_id=c, display_alias="Kid", age_band="child", authority=authority("guardian_attested"))
    payload = manifest(p, [
        entry(p, "primary", "person_adult", "analysis-v1", pr["record_digest"], "self_attested"),
        entry(c, "child", "person_minor", "child-profile-v1", child["record_digest"], "guardian_attested"),
    ])
    with pytest.raises(HouseholdContractError, match=r"primary \+ partner"):
        validate_household_manifest(payload)


def test_relational_view_is_same_system_observation_not_compatibility_score():
    result = exact_result()
    p, q = new_subject_id(), new_subject_id()
    pr, qr = analysis_record(p, result), analysis_record(q, result)
    household = manifest(p, [
        entry(p, "primary", "person_adult", "analysis-v1", pr["record_digest"], "self_attested"),
        entry(q, "partner", "person_adult", "analysis-v1", qr["record_digest"], "adult_consent_attested"),
    ])
    view = compose_relational_view(household, {p: pr, q: qr})
    assert view["status"] == "computed"
    assert view["subjects"][0]["label"] == ADULT_LABEL
    assert view["observations"]
    assert {item["kind"] for item in view["observations"]} <= {"same_marker", "different_marker"}
    assert all(item["dimension"] == "same_system_observation" for item in view["observations"])
    assert all("compatibility measure" in item["policy_note"] or "incompatibility" in item["policy_note"] for item in view["observations"])
    serialized = json.dumps(view)
    for forbidden_key in ['"score":', '"rank":', '"compatibility":', '"harmony":', '"fit":']:
        assert forbidden_key not in serialized


def test_stale_member_fails_closed_and_suppresses_relational_edges():
    result = exact_result()
    p, q = new_subject_id(), new_subject_id()
    pr, qr = analysis_record(p, result), analysis_record(q, result)
    household = manifest(p, [
        entry(p, "primary", "person_adult", "analysis-v1", pr["record_digest"], "self_attested"),
        entry(q, "partner", "person_adult", "analysis-v1", qr["record_digest"], "adult_consent_attested", state="stale"),
    ])
    view = compose_relational_view(household, {p: pr, q: qr})
    assert view["status"] == "unavailable"
    assert view["observations"] == []
    assert view["degraded"] is True


def test_child_and_pet_members_do_not_create_interpretive_edges():
    result = exact_result()
    p, c, pet = new_subject_id(), new_subject_id(), new_subject_id()
    pr = analysis_record(p, result)
    child = build_child_profile(subject_id=c, display_alias="Kid", age_band="child", authority=authority("guardian_attested"))
    animal = build_pet_profile(subject_id=pet, display_alias="Scout", species="dog", authority=authority("owner_attested"))
    cr, ar = profile_record(child), profile_record(animal)
    household = manifest(p, [
        entry(p, "primary", "person_adult", "analysis-v1", pr["record_digest"], "self_attested"),
        entry(c, "child", "person_minor", "child-profile-v1", cr["record_digest"], "guardian_attested"),
        entry(pet, "pet", "nonhuman_animal", "pet-profile-v1", ar["record_digest"], "owner_attested"),
    ], composition="household")
    view = compose_relational_view(household, {p: pr, c: cr, pet: ar})
    assert view["status"] == "computed"
    assert view["observations"] == []
    labels = {item["subject_role"]: item["label"] for item in view["subjects"]}
    assert labels["child"] == CHILD_LABEL
    assert labels["pet"] == PET_LABEL


def _token(payload, secret):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    sig = hmac.new(secret.encode(), raw, hashlib.sha256).digest()
    enc = lambda b: base64.urlsafe_b64encode(b).decode().rstrip("=")
    return enc(raw) + "." + enc(sig)


def test_entitlement_verification_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("HME_HOUSEHOLD_PAID_ENABLED", raising=False)
    decision = verify_entitlement_token(None, household_id=new_household_id(), required_added_subjects=1, secret="x" * 32, now=1000)
    assert not decision.allowed
    assert decision.code == "paid_feature_disabled"


def test_entitlement_binds_household_expiry_and_added_subject_limit(monkeypatch):
    monkeypatch.setenv("HME_HOUSEHOLD_PAID_ENABLED", "1")
    secret = "s" * 48
    household_id = new_household_id()
    claims = {
        "schema_version": "entitlement-v1", "scope": "household", "household_id": household_id,
        "subject_limit": 2, "issued_at": 900, "expires_at": 2000, "jti": "0123456789abcdef",
    }
    token = _token(claims, secret)
    assert verify_entitlement_token(token, household_id=household_id, required_added_subjects=2, secret=secret, now=1000).allowed
    assert verify_entitlement_token(token, household_id=household_id, required_added_subjects=3, secret=secret, now=1000).code == "entitlement_subject_limit_exceeded"
    assert verify_entitlement_token(token, household_id=household_id, required_added_subjects=1, secret=secret, now=2000).code == "entitlement_expired"
    assert verify_entitlement_token(token, household_id=new_household_id(), required_added_subjects=1, secret=secret, now=1000).code == "entitlement_household_mismatch"
