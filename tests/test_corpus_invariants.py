"""R2/R4 corpus and evidence-counting invariants (EN-11, EN-12, EN-16)."""
from __future__ import annotations

import hashlib
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [_ROOT, os.path.join(_ROOT, "src"), os.path.join(_ROOT, "webapp"),
                os.path.dirname(os.path.abspath(__file__))]

from synthesis.prose_lexicon import (  # noqa: E402
    LITERARY_INVENTORY,
    authored_asset_inventory,
    INVENTORY_VERSION,
)
from synthesis.system_vocabulary import (  # noqa: E402
    SYSTEM_VOCABULARY_ASSETS,
    select_system_vocabulary,
    R2_SYSTEM_TEXTS,
    R2_NON_IDENTITY_SYSTEMS,
)

ROOT = _ROOT
DOC = os.path.join(ROOT, "docs", "SIGNATURE_V3.md")


def test_corpus_asset_count_derived_not_hardcoded():
    """EN-12: 12×10 + 24×5 composition, derived from the actual data."""
    first_block = [a for a in SYSTEM_VOCABULARY_ASSETS if "-r2-" not in a["id"]]
    r2_block = [a for a in SYSTEM_VOCABULARY_ASSETS if "-r2-" in a["id"]]

    # First block: 12 systems × 10 assets each
    by_system_first = {}
    for asset in first_block:
        sys_name = asset["system_eligibility"][0]
        by_system_first.setdefault(sys_name, []).append(asset)
    assert len(by_system_first) == 12
    for assets in by_system_first.values():
        assert len(assets) == 10

    # R2 block: 24 systems × 5 assets each
    by_system_r2 = {}
    for asset in r2_block:
        sys_name = asset["system_eligibility"][0]
        by_system_r2.setdefault(sys_name, []).append(asset)
    assert len(by_system_r2) == 24
    for assets in by_system_r2.values():
        assert len(assets) == 5

    # Derived total matches the arithmetic
    derived = len(by_system_first) * 10 + len(by_system_r2) * 5
    assert len(SYSTEM_VOCABULARY_ASSETS) == derived
    assert derived == 240


def test_id_convention_with_documented_exemption():
    """EN-12: hyphen-separated convention; documented exemptions for human_design and sumerian_me."""
    ids = [a["id"] for a in SYSTEM_VOCABULARY_ASSETS]
    # Pattern: sys-<system_id>-NNN  or  sys-<system_id>-r2-NNN
    # The system_id may contain underscores (e.g. human_design, sumerian_me).
    pattern = r"^sys-[a-z0-9_]+(?:-[a-z0-9_]+)*(?:-r2)?-\d{3}$"
    for aid in ids:
        assert re.match(pattern, aid), f"id {aid} does not match convention"
    # Exemptions are documented in the implementation docs.
    doc = open(DOC, encoding="utf-8").read()
    assert "human_design" in doc
    assert "sumerian_me" in doc


def test_generated_record_injection_leaves_authored_count_unchanged(monkeypatch):
    """EN-12 / EN-15: adding a generated composition record never inflates authored."""
    import synthesis.prose_lexicon as pl

    before = authored_asset_inventory()
    monkeypatch.setattr(pl, "LITERARY_INVENTORY", pl.LITERARY_INVENTORY + ({
        "id": "li2-gen-999", "inventory_version": INVENTORY_VERSION,
        "category": "scene_opening", "review_status": "accepted",
        "text": "Generated template filler for testing.",
    },))
    after = authored_asset_inventory()
    assert after["generated_composition_records"] == before["generated_composition_records"] + 1
    assert after["authored_asset_count"] == before["authored_asset_count"]
    assert after["substantive_authored_asset_count"] == before["substantive_authored_asset_count"]


def test_evidence_counting_invariants():
    """EN-11: shared-source and reading-only never inflate motif votes."""
    from narrative_helpers import exact_result
    from synthesis.analysis import rank_motifs

    result = exact_result()
    items = result["synthesis"]["evidence"]["evidence_items"]
    plan = result["synthesis"]["plan"]

    # reading_only items have no interpretive_tags and are roadmap_* or binary_prime_*
    reading_only = [
        item for item in items
        if item.get("symbol_family", "").startswith(("roadmap_", "binary_prime_"))
    ]
    assert reading_only
    assert all(item["epistemic_class"] in {"deterministic_calculation", "historical_textual_reference"}
               for item in reading_only)

    # Duplicate evidence row with same independence_group adds recurrence_bonus but not a new group
    duped_item = reading_only[0]
    synthetic = {
        "evidence_items": items + [duped_item],
        "data_quality": result["synthesis"]["evidence"]["data_quality"],
    }
    ranked = rank_motifs(synthetic)
    original = rank_motifs(result["synthesis"]["evidence"])
    # Find the motif containing the duped evidence_id
    duped_id = duped_item["evidence_id"]
    for m in ranked:
        if duped_id in m["evidence_ids"]:
            # independent_group_count must be unchanged (only strongest per group counts)
            orig = next((o for o in original if o["motif_id"] == m["motif_id"]), None)
            assert orig is not None
            assert m["independent_group_count"] == orig["independent_group_count"]
            break

    # Reading-only rows never appear in dominant motif evidence_ids
    reading_only_ids = {item["evidence_id"] for item in reading_only}
    for motif in plan["dominant_motifs"]:
        assert reading_only_ids.isdisjoint(motif["evidence_ids"])


def test_shared_source_witnesses_documented():
    """EN-11: the sys-gematria-007 / sys-kabbalah-006 pattern is documented."""
    ids = [a["id"] for a in SYSTEM_VOCABULARY_ASSETS]
    witnesses = {"sys-gematria-007", "sys-kabbalah-006", "sys-pythagorean-007",
                 "sys-chaldean-005", "sys-ordinal-003", "sys-isopsephy-007",
                 "sys-linguistic-007", "sys-chinese-006", "sys-human_design-008"}
    assert witnesses.issubset(set(ids))
    doc = open(DOC, encoding="utf-8").read()
    for wid in witnesses:
        assert wid in doc, f"witness {wid} not documented"


def test_vocabulary_eligibility_tags_present():
    """EN-16: every asset declares mode_eligibility, claim_type_eligibility,
    epistemic_safety_tags, and a boolean identity_synthesis_eligible."""
    for asset in SYSTEM_VOCABULARY_ASSETS:
        assert asset["mode_eligibility"], f"{asset['id']}: empty mode_eligibility"
        assert asset["claim_type_eligibility"], f"{asset['id']}: empty claim_type_eligibility"
        assert asset["epistemic_safety_tags"], f"{asset['id']}: empty epistemic_safety_tags"
        assert isinstance(asset["identity_synthesis_eligible"], bool)
        assert asset["system_eligibility"]


def test_select_system_vocabulary_respects_identity_synthesis_gate():
    """EN-16: the identity_synthesis_eligible boolean is enforced by the selector."""
    # Systems in R2_NON_IDENTITY_SYSTEMS must be excluded when for_identity_synthesis=True
    for system in R2_NON_IDENTITY_SYSTEMS:
        assert select_system_vocabulary(system, "test-seed", for_identity_synthesis=True) is None
        assert select_system_vocabulary(system, "test-seed", for_identity_synthesis=False) is not None

    # At least one identity-eligible system yields a result in both modes
    identity_systems = [s for s in R2_SYSTEM_TEXTS if s not in R2_NON_IDENTITY_SYSTEMS]
    for system in identity_systems[:3]:
        assert select_system_vocabulary(system, "test-seed", for_identity_synthesis=True) is not None
        assert select_system_vocabulary(system, "test-seed", for_identity_synthesis=False) is not None


def test_mode_eligibility_remains_a_declaration():
    """EN-16 + CD-23 record: mode_eligibility is a declaration; no readings.py mode guard in R4."""
    doc = open(DOC, encoding="utf-8").read()
    assert "remains documentation" in doc
    assert "mode_eligibility" in doc
    assert "the guard stays a deferred" in doc


import re  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))