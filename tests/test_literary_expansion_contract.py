from pathlib import Path
from synthesis.prose_lexicon import (
    LITERARY_EXPANSION_MIN_FACTOR,
    LITERARY_EXPANSION_PREFERRED_FACTOR,
    literary_inventory,
    literary_expansion_targets,
)


def test_literary_expansion_contract_is_machine_readable():
    assert LITERARY_EXPANSION_MIN_FACTOR == 2
    assert LITERARY_EXPANSION_PREFERRED_FACTOR == 5
    inv = literary_inventory()
    assert inv["usable_units"] >= 90
    assert inv["unique_units"] == inv["usable_units"]
    targets = literary_expansion_targets(inv["usable_units"])
    assert targets["minimum"] == inv["usable_units"] * 2
    assert targets["preferred"] == inv["usable_units"] * 5


def test_canonical_literary_expansion_contract_is_documented():
    text = (Path(__file__).resolve().parents[1] / "docs/LITERARY_EXPANSION_CONTRACT.md").read_text()
    assert "2× minimum" in text
    assert "5× preferred" in text
    assert "padding" in text.lower()
    assert "provenance" in text.lower()
    assert "accepted post-review inventory" in text.lower()
