"""R2 corpus/data-source integration invariants."""
from narrative_helpers import exact_result

from synthesis.prose_lexicon import literary_inventory
from synthesis.system_vocabulary import (
    SYSTEM_VOCABULARY_ASSETS,
    SYSTEM_VOCABULARY_VERSION,
    select_system_vocabulary,
)

ROADMAP_SYSTEMS = {
    "alchemical_transformation", "apollonius", "arabic_abjad",
    "babylonian_planetary", "cuneiform_magic", "egyptian",
    "egyptian_maat", "elder_futhark", "esoteric_bridge",
    "hermes_thoth_nabu", "hermetic_principles", "indus_valley",
    "mandaean_duodecimal", "mayan_tzolkin", "ogham",
    "sacred_geometry", "solomonic", "sumerian_me_ontology",
    "sumerian_sexagesimal", "tartaria_architecture",
    "temporal_numerology", "unicode_codepoint", "vedic_jyotish",
}
NEW_EVIDENCE_SYSTEMS = ROADMAP_SYSTEMS | {"binary_prime"}

def test_new_data_sources_reach_evidence_without_becoming_motif_votes():
    result = exact_result()
    items = result["synthesis"]["evidence"]["evidence_items"]
    present = {item["system"] for item in items}
    assert NEW_EVIDENCE_SYSTEMS <= present

    new_items = [item for item in items if item["system"] in NEW_EVIDENCE_SYSTEMS]
    assert new_items
    assert all(item["interpretive_tags"] == [] for item in new_items)

    new_ids = {item["evidence_id"] for item in new_items}
    for motif in result["synthesis"]["plan"]["dominant_motifs"]:
        assert new_ids.isdisjoint(motif["evidence_ids"])


def test_system_vocabulary_is_literal_unique_and_substantive():
    texts = [item["text"] for item in SYSTEM_VOCABULARY_ASSETS]
    ids = [item["id"] for item in SYSTEM_VOCABULARY_ASSETS]
    assert len(texts) >= 240
    assert len(texts) == len(set(texts))
    assert len(ids) == len(set(ids))
    assert min(len(text.split()) for text in texts) >= 4

def test_authored_corpus_accounting_separates_assets_from_generated_space():
    inventory = literary_inventory()
    assert inventory["substantive_authored_asset_count"] >= 500
    assert inventory["authored_asset_count"] >= inventory["substantive_authored_asset_count"]
    assert inventory["system_vocabulary_asset_count"] >= 240
    assert inventory["generated_composition_records"] == inventory["accepted_units"]
    assert "reported separately" in inventory["accounting_note"]


def test_non_identity_historical_or_uncertain_systems_stay_out_of_identity_narration():
    excluded = {
        "cuneiform_magic", "hermes_thoth_nabu", "indus_valley",
        "sumerian_me_ontology", "tartaria_architecture",
    }
    for system in excluded:
        assert select_system_vocabulary(
            system, "r2-test-seed", for_identity_synthesis=True
        ) is None


def test_system_vocabulary_readings_are_self_contained_and_versioned():
    result = exact_result()
    reading_claims = [
        claim
        for section in result["synthesis"]["plan"]["narrative_sections"]
        for claim in section["claims"]
        if claim["claim_type"] == "reading"
        and claim["metadata"].get("library_version") == SYSTEM_VOCABULARY_VERSION
    ]
    assert len(reading_claims) >= 10
    assert all(claim["metadata"]["allow_lexicon_enrichment"] is False for claim in reading_claims)

