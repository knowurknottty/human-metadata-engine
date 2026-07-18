from src.encoders.quantum_soul_codex import quantum_soul_codex


def test_kirk_evan_brown_reference_vector():
    result = quantum_soul_codex(
        "Kirk Evan Brown",
        {"year": 1982, "month": 2, "day": 4},
    )

    assert result["status"] == "computed"
    assert result["interpretation_level"] == "symbolic_modern_synthesis"
    assert result["provenance"]["empirical_validity"] == "not_established"
    assert result["provenance"]["quantum_term"] == "metaphorical_only"

    data = result["data"]
    assert data["codex_key"] == "QSC-81374"
    assert data["timeline_key"] == "TKP-6634:2200"
    assert data["primary_sequence"] == [8, 1, 3, 7, 4]
    assert data["life_path"]["raw"] == 26
    assert data["expression"]["raw"] == 64
    assert data["soul_urge"]["raw"] == 21
    assert data["personality"]["raw"] == 43
    assert data["timeline"]["pinnacles"] == [6, 6, 3, 4]
    assert data["timeline"]["challenges"] == [2, 2, 0, 0]
    assert [(s["total"], s["reduced"]) for s in data["name_segments"]] == [
        (22, 22),
        (15, 6),
        (27, 9),
    ]


def test_birth_date_is_required_and_failure_is_explicit():
    result = quantum_soul_codex("Kirk Evan Brown", None)
    assert result["status"] == "insufficient_input"
    assert result["data"]["required"] == [
        "birth.year",
        "birth.month",
        "birth.day",
    ]


def test_output_is_deterministic():
    birth = {"year": 1982, "month": 2, "day": 4}
    assert quantum_soul_codex("Kirk Evan Brown", birth) == quantum_soul_codex(
        "Kirk Evan Brown", birth
    )
