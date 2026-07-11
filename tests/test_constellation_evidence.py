import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from constellation import ConstellationValidationError, connection_summary, validate_constellation
from etymology import analyze_name_etymology
from evidence_v3 import chance_corrected_pair_agreement, weighted_claim_support


def test_aghyarian_etymology_is_lineage_not_personality():
    result = analyze_name_etymology(
        "Kirk Evan Brown",
        lineage_surnames=["Aghyarian"],
    )
    lineage = result["lineage_surnames"][0]
    assert lineage["canonical_form"] == "Aghyarian"
    assert lineage["literal_glosses"] == ["family or descendants of Agha"]
    assert result["personality_inference"] is False
    assert result["genetic_inference"] is False


def test_aghiarian_resolves_as_spelling_variant():
    result = analyze_name_etymology("Aghiarian")
    component = result["components"][0]
    assert component["canonical_form"] == "Aghyarian"
    assert component["matched_variant"] == "Aghiarian"


def test_single_duplicate_is_only_weak_excess_over_chance():
    agreement = chance_corrected_pair_agreement([1, 1, 2, 3])
    assert agreement["matching_pairs"] == 1
    assert agreement["chance_corrected_agreement"] == 0.0625


def test_observed_contradiction_outweighs_symbolic_support():
    result = weighted_claim_support({
        "observed_behavior": -0.8,
        "astrology": 1.0,
        "numerology": 1.0,
        "experimental_correspondence": 1.0,
    })
    assert result["support"] < 0.0


def test_tiered_constellation_accepts_creations_and_name_only_people():
    graph = validate_constellation({
        "nodes": [
            {"id": "self", "type": "person", "name": "Kirk Evan Brown"},
            {"id": "capt", "type": "alias", "name": "Capt"},
            {"id": "capt-project", "type": "project", "name": "CAPT"},
            {"id": "child", "type": "person", "name": "Private Child", "is_minor": True},
        ],
        "edges": [
            {"source": "capt", "target": "self", "relation": "alias_of"},
            {"source": "self", "target": "capt-project", "relation": "created"},
            {"source": "self", "target": "child", "relation": "parent_of"},
        ],
    })
    assert graph["nodes"][3]["profile_level"] == "name_only"
    assert connection_summary(graph)["edge_count"] == 3


def test_minor_psychology_is_rejected():
    try:
        validate_constellation({
            "nodes": [{
                "id": "child",
                "type": "person",
                "name": "Private Child",
                "is_minor": True,
                "profile_level": "self_report",
                "consent_basis": "explicit_consent",
                "psychology": {"big_five": {"openness": 0.5}},
            }],
            "edges": [],
        })
    except ConstellationValidationError as exc:
        assert "minor" in str(exc)
    else:
        raise AssertionError("minor psychology must be rejected")


def main():
    tests = [
        test_aghyarian_etymology_is_lineage_not_personality,
        test_aghiarian_resolves_as_spelling_variant,
        test_single_duplicate_is_only_weak_excess_over_chance,
        test_observed_contradiction_outweighs_symbolic_support,
        test_tiered_constellation_accepts_creations_and_name_only_people,
        test_minor_psychology_is_rejected,
    ]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} constellation/evidence tests")


if __name__ == "__main__":
    main()
