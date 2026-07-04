"""
Final Encoder Tests — Complete Suite
=====================================

Tests for Gematria, Isopsephy, Astrology, Human Design, Psychology,
Graph Algorithms, and Knowledge Bubbles.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# ===================== GEMATRIA TESTS =====================

def test_gematria_capt():
    from encoders.gematria import gematria_signature
    sig = gematria_signature("CAPT")
    assert sig.absolute_total > 0
    assert sig.reduced_total > 0
    assert len(sig.letter_values) == 4
    print("✓ test_gematria_capt passed")


def test_gematria_case_insensitive():
    from encoders.gematria import gematria_signature
    sig1 = gematria_signature("CAPT")
    sig2 = gematria_signature("Capt")
    assert sig1.absolute_total == sig2.absolute_total
    print("✓ test_gematria_case_insensitive passed")


def test_gematria_ratio():
    from encoders.gematria import gematria_signature
    sig = gematria_signature("CAPT")
    assert sig.gematria_ordinal_ratio > 0
    print("✓ test_gematria_ratio passed")


# ===================== ISOPSEPHY TESTS =====================

def test_isopsephy_capt():
    from encoders.isopsephy import isopsephy_signature
    sig = isopsephy_signature("CAPT")
    assert sig.total > 0
    assert sig.reduced > 0
    assert len(sig.letter_values) == 4
    assert len(sig.greek_correspondence) == 4
    print("✓ test_isopsephy_capt passed")


def test_isopsephy_digital_root():
    from encoders.isopsephy import isopsephy_signature
    sig = isopsephy_signature("CAPT")
    assert len(sig.digital_root_chain) >= 1
    assert sig.digital_root_chain[-1] == sig.reduced
    print("✓ test_isopsephy_digital_root passed")


def test_isopsephy_greek_correspondence():
    from encoders.isopsephy import isopsephy_signature
    sig = isopsephy_signature("A")
    assert sig.greek_correspondence[0]["greek"] == "α"
    assert sig.greek_correspondence[0]["greek_name"] == "alpha"
    print("✓ test_isopsephy_greek_correspondence passed")


# ===================== ASTROLOGY TESTS =====================

def test_astrology_sun_sign():
    from encoders.astrology import compute_chart
    chart = compute_chart(1982, 2, 4, 1, 42, -7, "Evanston, Wyoming, USA")
    assert chart.sun_sign == "Aquarius"
    print("✓ test_astrology_sun_sign passed")


def test_astrology_moon_sign():
    from encoders.astrology import compute_chart
    chart = compute_chart(1982, 2, 4, 1, 42, -7, "Evanston, Wyoming, USA")
    assert chart.moon_sign == "Gemini"
    print("✓ test_astrology_moon_sign passed")


def test_astrology_ascendant():
    from encoders.astrology import compute_chart
    chart = compute_chart(1982, 2, 4, 1, 42, -7, "Evanston, Wyoming, USA")
    assert chart.ascendant == "Scorpio"
    print("✓ test_astrology_ascendant passed")


def test_astrology_planets():
    from encoders.astrology import compute_chart
    chart = compute_chart(1982, 2, 4, 1, 42, -7, "Evanston, Wyoming, USA")
    assert len(chart.planets) == 10
    print("✓ test_astrology_planets passed")


def test_astrology_aspects():
    from encoders.astrology import compute_chart
    chart = compute_chart(1982, 2, 4, 1, 42, -7, "Evanston, Wyoming, USA")
    assert len(chart.aspects) > 0
    print("✓ test_astrology_aspects passed")


def test_astrology_confidence():
    from encoders.astrology import compute_chart
    chart = compute_chart(1982, 2, 4, 1, 42, -7, "Evanston, Wyoming, USA")
    assert chart.confidence == 0.95  # Exact time
    print("✓ test_astrology_confidence passed")


def test_astrology_noon_default():
    from encoders.astrology import compute_chart
    chart = compute_chart(1982, 2, 4, 12, 0, -7, "Evanston, Wyoming, USA")
    assert chart.confidence == 0.4  # Noon default
    print("✓ test_astrology_noon_default passed")


def test_astrology_chart_ruler():
    from encoders.astrology import compute_chart
    chart = compute_chart(1982, 2, 4, 1, 42, -7, "Evanston, Wyoming, USA")
    assert chart.chart_ruler == "Pluto"  # Scorpio ascendant → Pluto
    print("✓ test_astrology_chart_ruler passed")


def test_astrology_lunar_phase():
    from encoders.astrology import compute_chart
    chart = compute_chart(1982, 2, 4, 1, 42, -7, "Evanston, Wyoming, USA")
    assert chart.lunar_phase != "Unknown"
    assert chart.is_waxing is not None
    print("✓ test_astrology_lunar_phase passed")


# ===================== HUMAN DESIGN TESTS =====================

def test_human_design_type():
    from encoders.human_design import compute_human_design
    hd = compute_human_design(1982, 2, 4, 1, 42, -7, "Evanston, Wyoming, USA")
    assert hd.hd_type in ["Manifestor", "Generator", "Manifesting Generator", "Projector", "Reflector"]
    print("✓ test_human_design_type passed")


def test_human_design_strategy():
    from encoders.human_design import compute_human_design
    hd = compute_human_design(1982, 2, 4, 1, 42, -7, "Evanston, Wyoming, USA")
    assert hd.strategy != ""
    print("✓ test_human_design_strategy passed")


def test_human_design_gates():
    from encoders.human_design import compute_human_design
    hd = compute_human_design(1982, 2, 4, 1, 42, -7, "Evanston, Wyoming, USA")
    assert len(hd.personality_gates) > 0
    assert len(hd.design_gates) > 0
    for g in hd.personality_gates:
        assert 1 <= g.gate <= 64
    print("✓ test_human_design_gates passed")


def test_human_design_profile():
    from encoders.human_design import compute_human_design
    hd = compute_human_design(1982, 2, 4, 1, 42, -7, "Evanston, Wyoming, USA")
    assert 1 <= hd.profile_number[0] <= 6
    assert 1 <= hd.profile_number[1] <= 6
    print("✓ test_human_design_profile passed")


def test_human_design_centers():
    from encoders.human_design import compute_human_design
    hd = compute_human_design(1982, 2, 4, 1, 42, -7, "Evanston, Wyoming, USA")
    assert len(hd.centers) == 9
    print("✓ test_human_design_centers passed")


# ===================== PSYCHOLOGY TESTS =====================

def test_psychology_big_five():
    from encoders.psychology import create_profile
    p = create_profile("test", big_five={"openness": 0.9, "conscientiousness": 0.8,
                       "extraversion": 0.6, "agreeableness": 0.7, "neuroticism": 0.3})
    assert p.big_five is not None
    assert p.big_five.openness == 0.9
    assert p.big_five.dominant_trait() == "Openness"
    print("✓ test_psychology_big_five passed")


def test_psychology_mbti():
    from encoders.psychology import create_profile, MBTI
    p = create_profile("test", mbti_type="INTJ")
    assert p.mbti is not None
    assert p.mbti.type_code == "INTJ"
    assert p.mbti.cognitive_functions == ["Ni", "Te", "Fi", "Se"]
    assert MBTI.validate_type("INTJ") is True
    assert MBTI.validate_type("INVALID") is False
    print("✓ test_psychology_mbti passed")


def test_psychology_enneagram():
    from encoders.psychology import create_profile
    p = create_profile("test", enneagram_type=5, enneagram_wing=4)
    assert p.enneagram is not None
    assert p.enneagram.core_type == 5
    assert p.enneagram.wing == 4
    assert "Investigator" in p.enneagram.summary()
    print("✓ test_psychology_enneagram passed")


def test_psychology_attachment():
    from encoders.psychology import create_profile
    p = create_profile("test", attachment="Secure")
    assert p.attachment_style is not None
    assert p.attachment_style.primary_style == "Secure"
    print("✓ test_psychology_attachment passed")


def test_psychology_summary():
    from encoders.psychology import create_profile
    p = create_profile("test", mbti_type="ENFP", enneagram_type=7)
    summary = p.summary()
    assert "ENFP" in summary
    assert "Enthusiast" in summary
    print("✓ test_psychology_summary passed")


# ===================== GRAPH ALGORITHM TESTS =====================

def test_pagerank():
    from graph.algorithms import pagerank
    import json
    with open("output/identity_graph.json") as f:
        graph = json.load(f)
    results = pagerank(graph)
    assert len(results) > 0
    assert results[0].rank > 0
    # Kirk Evan Brown should be highest (most connections)
    # PageRank measures incoming link importance — projects with most inbound rank highest
    assert results[0].node_id in ["human:kirk_evan_brown", "project:frankencapt", "project:capt"]
    print("✓ test_pagerank passed")


def test_connected_components():
    from graph.algorithms import connected_components
    import json
    with open("output/identity_graph.json") as f:
        graph = json.load(f)
    cc = connected_components(graph)
    assert len(cc) > 0
    # All nodes should appear exactly once
    all_nodes = [n for comp in cc for n in comp]
    assert len(all_nodes) == len(set(all_nodes))
    print("✓ test_connected_components passed")


def test_graph_diameter():
    from graph.algorithms import graph_diameter
    import json
    with open("output/identity_graph.json") as f:
        graph = json.load(f)
    diameter, radius, ecc = graph_diameter(graph)
    assert diameter > 0
    assert radius > 0
    assert radius <= diameter
    print("✓ test_graph_diameter passed")


def test_hits():
    from graph.algorithms import hits
    import json
    with open("output/identity_graph.json") as f:
        graph = json.load(f)
    hubs, auths = hits(graph)
    assert len(hubs) > 0
    assert len(auths) > 0
    # Kirk should be top hub
    top_hub = max(hubs, key=hubs.get)
    assert top_hub == "human:kirk_evan_brown"
    print("✓ test_hits passed")


# ===================== KNOWLEDGE BUBBLE TESTS =====================

def test_knowledge_bubble_creation():
    from knowledge_bubble import create_identity_bubble
    bubble = create_identity_bubble(
        "CAPT",
        pythagorean_data={"total": 13, "expression": 4, "master_preserved": None,
                         "soul_urge": 1, "personality": 3, "soul_urge_total": 1,
                         "personality_total": 12},
        chaldean_data={"compound_number": 16, "name_number": 7,
                       "soul_urge": 1, "personality": 8},
        ordinal_data={"standard": 40, "standard_reduced": 4, "reverse": 68,
                     "reverse_reduced": 5},
        linguistic_data={"letter_count": 4, "shannon_entropy": 2.0,
                        "max_possible_entropy": 4.7, "syllable_estimate": 1,
                        "vowel_ratio": 0.25, "unique_letters": 4},
        binary_prime_data={"binary_string": "1011", "binary_weight": 3,
                          "prime_total": 131, "prime_reduced": 5,
                          "vowel_power": 2, "consonant_power": 129,
                          "polarity_score": -127},
    )
    assert bubble.topic == "Identity: CAPT"
    assert len(bubble.claims) > 0
    assert len(bubble.computations) > 0
    assert bubble.confidence > 0
    print("✓ test_knowledge_bubble_creation passed")


def test_knowledge_bubble_markdown():
    from knowledge_bubble import create_identity_bubble, export_bubble_markdown
    bubble = create_identity_bubble(
        "Test",
        pythagorean_data={"total": 10, "expression": 1, "master_preserved": None,
                         "soul_urge": 5, "personality": 5, "soul_urge_total": 5,
                         "personality_total": 5},
        chaldean_data={"compound_number": 10, "name_number": 1, "soul_urge": 5, "personality": 5},
        ordinal_data={"standard": 10, "standard_reduced": 1, "reverse": 100, "reverse_reduced": 1},
        linguistic_data={"letter_count": 4, "shannon_entropy": 2.0,
                        "max_possible_entropy": 4.7, "syllable_estimate": 1,
                        "vowel_ratio": 0.5, "unique_letters": 3},
        binary_prime_data={"binary_string": "0101", "binary_weight": 2,
                          "prime_total": 50, "prime_reduced": 5,
                          "vowel_power": 20, "consonant_power": 30,
                          "polarity_score": -10},
    )
    md = export_bubble_markdown(bubble)
    assert "# Identity: Test" in md
    assert "Claims" in md
    assert "Computations" in md
    print("✓ test_knowledge_bubble_markdown passed")


# ===================== RUN ALL =====================

def run_all():
    tests = [
        # Gematria
        test_gematria_capt,
        test_gematria_case_insensitive,
        test_gematria_ratio,
        # Isopsephy
        test_isopsephy_capt,
        test_isopsephy_digital_root,
        test_isopsephy_greek_correspondence,
        # Astrology
        test_astrology_sun_sign,
        test_astrology_moon_sign,
        test_astrology_ascendant,
        test_astrology_planets,
        test_astrology_aspects,
        test_astrology_confidence,
        test_astrology_noon_default,
        test_astrology_chart_ruler,
        test_astrology_lunar_phase,
        # Human Design
        test_human_design_type,
        test_human_design_strategy,
        test_human_design_gates,
        test_human_design_profile,
        test_human_design_centers,
        # Psychology
        test_psychology_big_five,
        test_psychology_mbti,
        test_psychology_enneagram,
        test_psychology_attachment,
        test_psychology_summary,
        # Graph Algorithms
        test_pagerank,
        test_connected_components,
        test_graph_diameter,
        test_hits,
        # Knowledge Bubbles
        test_knowledge_bubble_creation,
        test_knowledge_bubble_markdown,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {type(e).__name__}: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Final Tests: {passed} passed, {failed} failed out of {len(tests)}")
    print(f"{'='*60}")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
