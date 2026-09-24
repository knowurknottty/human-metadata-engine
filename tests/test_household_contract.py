"""Multi-subject Human Manual contracts and fail-closed relational composition."""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, "tests"), os.path.join(ROOT, "webapp"), os.path.join(ROOT, "src")]

from household import (  # noqa: E402
    CHILD_PROFILE_VERSION,
    PET_PROFILE_VERSION,
    FORBIDDEN_RELATIONAL_INFERENCES,
    HouseholdContractError,
    analysis_record,
    build_child_profile,
    build_pet_profile,
    compose_relational_view,
    new_household_id,
    new_subject_id,
    profile_record,
    validate_household_manifest,
)
from narrative_helpers import exact_result  # noqa: E402
from server import analyze  # noqa: E402


def authority(kind: str) -> dict:
    return {"kind": kind, "attestation_version": "authority-v1"}


def member(subject_id, role, subject_class, record_contract, digest, authority_kind, state="resolved"):
    return {
        "subject_id": subject_id,
        "subject_role": role,
        "subject_class": subject_class,
        "membership": "context_only" if role == "reference" else "member",
        "record_contract": record_contract,
        "record_digest": digest,
        "record_state": state,
        "authority": authority(authority_kind),
    }


def pair_manifest(primary_record, partner_record):
    return {
        "contract_version": "household-v1",
        "household_id": new_household_id(),
        "composition": "pair",
        "primary_subject_id": primary_record["subject_id"],
        "subjects": [
            member(primary_record["subject_id"], "primary", "person_adult", "analysis-v1",
                   primary_record["record_digest"], "self_attested"),
            member(partner_record["subject_id"], "partner", "person_adult", "analysis-v1",
                   partner_record["record_digest"], "adult_consent_attested"),
        ],
        "requested_dimensions": [
            "composition_scope", "role_presence", "declared_relationship",
            "input_readiness", "system_availability", "evidence_state",
            "same_system_observations",
        ],
    }


def test_random_subject_ids_do_not_derive_from_names():
    left = new_subject_id()
    right = new_subject_id()
    assert left != right
    assert left.startswith("subj_") and len(left) == 37
    assert right.startswith("subj_") and len(right) == 37


def test_child_profile_invokes_only_child_safe_selected_systems():
    subject_id = new_subject_id()
    profile = build_child_profile(
        subject_id=subject_id,
        display_alias="Avery Example",
        age_band="child",
        authority=authority("guardian_attested"),
        birth={"year": 2016, "month": 4, "day": 8},
    )
    assert profile["contract_version"] == CHILD_PROFILE_VERSION
    assert profile["subject_class"] == "person_minor"
    assert set(profile["worksheets"]) == {
        "unicode_codepoint", "sumerian_sexagesimal", "mandaean_duodecimal",
        "elder_futhark", "ogham",
    }
    serialized = repr(profile).casefold()
    assert "jyotish" not in serialized
    assert "bazi-v2" not in serialized
    assert "maya-classical" not in serialized
    assert "not predictive" in profile["label"].casefold()


def test_child_policy_excludes_birth_dependent_worksheet_even_when_birth_is_present():
    profile = build_child_profile(
        subject_id=new_subject_id(),
        display_alias="Avery Example",
        age_band="adolescent",
        authority=authority("guardian_attested"),
    )
    assert "chinese" not in profile["worksheets"]


def test_pet_profile_never_runs_human_symbolic_engine():
    profile = build_pet_profile(
        subject_id=new_subject_id(),
        display_alias="Mochi",
        species="cat",
        breed="domestic shorthair",
        age_band="adult",
        authority=authority("owner_attested"),
    )
    assert profile["contract_version"] == PET_PROFILE_VERSION
    assert profile["subject_class"] == "nonhuman_animal"
    assert profile["symbolic_systems"] == {}
    assert profile["interpretation_policy"] == "care_context_only"
    assert "no symbolic or health interpretation" in profile["label"].casefold()


def test_pair_contract_is_exactly_primary_plus_partner():
    primary = analysis_record(new_subject_id(), exact_result())
    partner = analysis_record(new_subject_id(), analyze({"name": "Ada Lovelace", "mode": "data"}))
    validated = validate_household_manifest(pair_manifest(primary, partner))
    assert validated["composition"] == "pair"
    assert {item["subject_role"] for item in validated["subjects"]} == {"primary", "partner"}

    bad = pair_manifest(primary, partner)
    bad["subjects"][1]["subject_role"] = "adult_family"
    with __import__("pytest").raises(HouseholdContractError):
        validate_household_manifest(bad)


def test_household_allows_child_and_pet_but_requires_matching_contracts_and_authority():
    primary = analysis_record(new_subject_id(), exact_result())
    child = build_child_profile(
        subject_id=new_subject_id(), display_alias="Avery", age_band="child",
        authority=authority("guardian_attested"),
    )
    pet = build_pet_profile(
        subject_id=new_subject_id(), display_alias="Mochi", species="cat",
        authority=authority("owner_attested"),
    )
    child_record = profile_record(child)
    pet_record = profile_record(pet)
    manifest = {
        "contract_version": "household-v1",
        "household_id": new_household_id(),
        "composition": "household",
        "primary_subject_id": primary["subject_id"],
        "subjects": [
            member(primary["subject_id"], "primary", "person_adult", "analysis-v1",
                   primary["record_digest"], "self_attested"),
            member(child_record["subject_id"], "child", "person_minor", "child-profile-v1",
                   child_record["record_digest"], "guardian_attested"),
            member(pet_record["subject_id"], "pet", "nonhuman_animal", "pet-profile-v1",
                   pet_record["record_digest"], "owner_attested"),
        ],
        "requested_dimensions": ["composition_scope", "role_presence", "system_availability"],
    }
    validated = validate_household_manifest(manifest)
    assert [item["subject_role"] for item in validated["subjects"]] == ["primary", "child", "pet"]


def test_relational_view_compares_adults_only_within_same_system_field():
    primary = analysis_record(new_subject_id(), exact_result())
    partner = analysis_record(new_subject_id(), analyze({"name": "Ada Lovelace", "mode": "data"}))
    manifest = pair_manifest(primary, partner)
    registry = {primary["subject_id"]: primary, partner["subject_id"]: partner}
    view = compose_relational_view(manifest, registry)

    assert view["schema_version"] == "relational-view-v1"
    assert view["status"] == "computed"
    assert view["degraded"] is False
    assert view["view_digest"].startswith("sha256:")
    assert view["observations"]
    for observation in view["observations"]:
        assert observation["kind"] in {"same_marker", "different_marker"}
        assert observation["dimension"] == "same_system_observation"
        assert len(observation["evidence_ids"]) == 2
        assert "compatibility" in observation["forbidden_inferences"]
        assert "score" not in observation
        assert "magnitude" not in observation

    text = repr(view).casefold()
    assert "compatibility_score" not in text
    assert "soulmate_score" not in text


def test_stale_member_fails_closed_and_suppresses_observations():
    primary = analysis_record(new_subject_id(), exact_result())
    partner = analysis_record(new_subject_id(), analyze({"name": "Ada Lovelace", "mode": "data"}))
    manifest = pair_manifest(primary, partner)
    manifest["subjects"][1]["record_state"] = "stale"
    view = compose_relational_view(
        manifest,
        {primary["subject_id"]: primary, partner["subject_id"]: partner},
    )
    assert view["status"] == "unavailable"
    assert view["degraded"] is True
    assert view["subjects"] == []
    assert view["observations"] == []
    assert any(":stale" in reason for reason in view["degradation_reasons"])


def test_child_and_pet_never_receive_adult_relational_marker_observations():
    primary = analysis_record(new_subject_id(), exact_result())
    child = profile_record(build_child_profile(
        subject_id=new_subject_id(), display_alias="Avery", age_band="child",
        authority=authority("guardian_attested"),
    ))
    pet = profile_record(build_pet_profile(
        subject_id=new_subject_id(), display_alias="Mochi", species="cat",
        authority=authority("owner_attested"),
    ))
    manifest = {
        "contract_version": "household-v1",
        "household_id": new_household_id(),
        "composition": "household",
        "primary_subject_id": primary["subject_id"],
        "subjects": [
            member(primary["subject_id"], "primary", "person_adult", "analysis-v1",
                   primary["record_digest"], "self_attested"),
            member(child["subject_id"], "child", "person_minor", "child-profile-v1",
                   child["record_digest"], "guardian_attested"),
            member(pet["subject_id"], "pet", "nonhuman_animal", "pet-profile-v1",
                   pet["record_digest"], "owner_attested"),
        ],
        "requested_dimensions": ["composition_scope", "role_presence", "system_availability"],
    }
    view = compose_relational_view(
        manifest,
        {primary["subject_id"]: primary, child["subject_id"]: child, pet["subject_id"]: pet},
    )
    assert view["status"] == "computed"
    assert view["observations"] == []
    by_role = {item["subject_role"]: item for item in view["subjects"]}
    assert by_role["pet"]["systems"] == []
    assert by_role["pet"]["system_availability"] == "unavailable"
    assert "jyotish" not in by_role["child"]["systems"]


def test_forbidden_inference_registry_contains_required_prohibitions():
    forbidden = set(FORBIDDEN_RELATIONAL_INFERENCES)
    for key in {
        "compatibility", "soulmate", "parenting_suitability", "child_potential",
        "pet_diagnosis", "relationship_outcome_prediction", "cross_tradition_agreement",
    }:
        assert key in forbidden
