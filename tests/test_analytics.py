"""
Tests for v0.4.0 analytics: composite resonance, fingerprints,
correlations, similarity, batch report, snapshots, and the
long-form report generator.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import pytest
from engine import compute_unified_signature
from analytics import (
    composite_resonance, identity_fingerprint, feature_vector,
    cosine_similarity, feature_agreement, identity_similarity_matrix,
    cross_encoder_correlations, batch_report, FEATURE_ORDER,
)
from snapshot import personality_snapshot
from report import generate_report


def sig_for(text, birth=None):
    ident = {"id": f"test:{text.lower().replace(' ', '_')}", "text": text}
    if birth:
        ident["birth"] = birth
    return compute_unified_signature(ident)


@pytest.fixture(scope="module")
def s1():
    return sig_for("John Michael Smith",
                   birth={"year": 1985, "month": 6, "day": 15, "hour": 10, "minute": 30,
                          "timezone_offset": -7, "location": "Portland, Oregon, USA",
                          "lat": 45.5152, "lon": -122.6765})


@pytest.fixture(scope="module")
def s2():
    return sig_for("CAPT")


@pytest.fixture(scope="module")
def s3():
    return sig_for("Albert Einstein")


@pytest.fixture(scope="module")
def s4():
    return sig_for("Jenn")


@pytest.fixture(scope="module")
def sigs(s1, s2, s3, s4):
    return [s1, s2, s3, s4]


# ---- Composite resonance ----

def test_resonance_score_range(s1):
    r1 = composite_resonance(s1)
    assert 0 <= r1["score"] <= 100

def test_resonance_components(s1):
    r1 = composite_resonance(s1)
    assert len(r1["components"]) == 4
    assert all(0 <= v <= 1 for v in r1["components"].values())

def test_resonance_weights_sum(s1):
    r1 = composite_resonance(s1)
    assert abs(sum(r1["weights"].values()) - 1.0) < 1e-9

def test_resonance_deterministic(s1):
    r1 = composite_resonance(s1)
    assert composite_resonance(s1)["score"] == r1["score"]

def test_engine_embeds_resonance(s1):
    r1 = composite_resonance(s1)
    assert s1.get("resonance", {}).get("score") == r1["score"]


# ---- Fingerprint ----

def test_fingerprint_hash(s1):
    f1 = identity_fingerprint(s1)
    assert len(f1["hash"]) == 16
    assert all(c in "0123456789abcdef" for c in f1["hash"])

def test_fingerprint_different_for_different_names(s1, s2):
    f1 = identity_fingerprint(s1)
    f2 = identity_fingerprint(s2)
    assert f1["hash"] != f2["hash"]

def test_fingerprint_deterministic(s1):
    f1 = identity_fingerprint(s1)
    assert identity_fingerprint(s1)["hash"] == f1["hash"]

def test_fingerprint_symmetry(s1):
    f1 = identity_fingerprint(s1)
    assert 3 <= f1["symmetry"] <= 9

def test_fingerprint_spokes(s1):
    f1 = identity_fingerprint(s1)
    assert len(f1["spokes"]) == 7
    assert all(0 <= sp["value"] <= 1 for sp in f1["spokes"])

def test_fingerprint_ring_pattern(s1):
    f1 = identity_fingerprint(s1)
    assert f1["ring_pattern"] == s1["encoders"]["binary_prime"]["binary_string"]


# ---- Feature vectors / similarity ----

def test_feature_vector_length(s1):
    v1 = feature_vector(s1)
    assert len(v1) == len(FEATURE_ORDER)

def test_feature_vector_normalized(s1):
    v1 = feature_vector(s1)
    assert all(0 <= x <= 1 for x in v1)

def test_self_similarity(s1):
    v1 = feature_vector(s1)
    assert abs(cosine_similarity(v1, v1) - 1.0) < 1e-9

def test_self_agreement(s1):
    v1 = feature_vector(s1)
    assert abs(feature_agreement(v1, v1) - 1.0) < 1e-9

def test_discrete_feature_agreement():
    discrete_left = [0.0] * 8 + [0.5] * 6
    discrete_right = [1.0 / 9.0] * 8 + [0.5] * 6
    assert abs(feature_agreement(discrete_left, discrete_right) - (6 / 14)) < 1e-9

def test_similarity_matrix(sigs):
    sim = identity_similarity_matrix(sigs)
    assert sim["metric"] == "feature_agreement_v1"
    assert len(sim["matrix"]) == 4
    assert all(len(row) == 4 for row in sim["matrix"].values())
    assert all(abs(sim["matrix"][i][i] - 1.0) < 1e-6 for i in sim["ids"])
    assert all(sim["matrix"][a][b] == sim["matrix"][b][a]
               for a in sim["ids"] for b in sim["ids"])
    assert all(len(n) == 3 for n in sim["nearest_neighbors"].values())
    assert all(0 <= n["agreement"] <= 1
               for neighbors in sim["nearest_neighbors"].values() for n in neighbors)


# ---- Cross-encoder correlations ----

def test_correlations(sigs):
    corr = cross_encoder_correlations(sigs)
    assert len(corr["pearson"]) == 7
    assert all(abs(corr["pearson"][e][e] - 1.0) < 1e-6 for e in corr["magnitude_encoders"])
    assert all(-1 <= corr["pearson"][a][b] <= 1
               for a in corr["magnitude_encoders"] for b in corr["magnitude_encoders"])
    assert all(corr["digit_agreement"][e][e] == 1.0 for e in corr["digit_encoders"])
    assert all(0 <= corr["digit_agreement"][a][b] <= 1
               for a in corr["digit_encoders"] for b in corr["digit_encoders"])


# ---- Batch report ----

def test_batch_report(sigs):
    rep_json, rep_md = batch_report(sigs)
    assert len(rep_json["ranking"]) == 4
    assert all(rep_json["ranking"][i]["resonance"] >= rep_json["ranking"][i + 1]["resonance"]
               for i in range(3))
    assert "| Rank |" in rep_md
    assert "Digit Agreement" in rep_md


# ---- Snapshot ----

def test_snapshot_empty():
    snap_empty = personality_snapshot("Test Name")
    assert snap_empty["available_layers"] == []
    assert len(snap_empty["narrative"]) > 50

def test_snapshot_psychology():
    psych = {"big_five": {"openness": 0.9, "conscientiousness": 0.5,
                          "extraversion": 0.3, "agreeableness": 0.6, "neuroticism": 0.4},
             "mbti": "INTJ", "enneagram": {"type": 5, "wing": 4}, "attachment": "secure"}
    snap_p = personality_snapshot("Test Name", psychology=psych)
    assert "psychology" in snap_p["available_layers"]
    assert "INTJ" in snap_p["narrative"]

def test_snapshot_astrology(s3):
    astro = s3["encoders"].get("astrology")
    if astro and not astro.get("error"):
        snap_a = personality_snapshot("Albert Einstein", astrology=astro)
        assert "astrology" in snap_a["available_layers"]
        assert astro["sun_sign"] in snap_a["narrative"]
    else:
        pytest.skip("astrology not available (no swisseph)")

def test_engine_embeds_snapshot(s1):
    assert "snapshot" in s1


# ---- Long-form report ----

def test_report_sections(s1):
    psych = {"big_five": {"openness": 0.9, "conscientiousness": 0.5,
                          "extraversion": 0.3, "agreeableness": 0.6, "neuroticism": 0.4},
             "mbti": "INTJ", "enneagram": {"type": 5, "wing": 4}, "attachment": "secure"}
    s2 = sig_for("CAPT")
    r = generate_report(s1, psychology=psych,
                        comparisons=[{"id": s2["id"], "text": s2["text"], "similarity": 0.91}])
    has_astro = s1["encoders"].get("astrology") and not s1["encoders"]["astrology"].get("error")
    if has_astro:
        assert r["sections"] == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    else:
        assert 5 not in r["sections"]

def test_report_word_count(s1):
    psych = {"big_five": {"openness": 0.9, "conscientiousness": 0.5,
                          "extraversion": 0.3, "agreeableness": 0.6, "neuroticism": 0.4},
             "mbti": "INTJ", "enneagram": {"type": 5, "wing": 4}, "attachment": "secure"}
    s2 = sig_for("CAPT")
    r = generate_report(s1, psychology=psych,
                        comparisons=[{"id": s2["id"], "text": s2["text"], "similarity": 0.91}])
    assert r["word_count"] >= 3000

def test_report_deterministic(s1):
    psych = {"big_five": {"openness": 0.9, "conscientiousness": 0.5,
                          "extraversion": 0.3, "agreeableness": 0.6, "neuroticism": 0.4},
             "mbti": "INTJ", "enneagram": {"type": 5, "wing": 4}, "attachment": "secure"}
    s2 = sig_for("CAPT")
    r1 = generate_report(s1, psychology=psych,
                         comparisons=[{"id": s2["id"], "text": s2["text"], "similarity": 0.91}])
    r2 = generate_report(s1, psychology=psych,
                         comparisons=[{"id": s2["id"], "text": s2["text"], "similarity": 0.91}])
    assert r1["markdown"] == r2["markdown"]

def test_name_only_report(s2):
    r_min = generate_report(s2)
    assert 5 not in r_min["sections"] and 6 not in r_min["sections"]
    assert r_min["word_count"] >= 2000

def test_report_mentions_name(s1):
    psych = {"big_five": {"openness": 0.9, "conscientiousness": 0.5,
                          "extraversion": 0.3, "agreeableness": 0.6, "neuroticism": 0.4},
             "mbti": "INTJ", "enneagram": {"type": 5, "wing": 4}, "attachment": "secure"}
    s2 = sig_for("CAPT")
    r = generate_report(s1, psychology=psych,
                        comparisons=[{"id": s2["id"], "text": s2["text"], "similarity": 0.91}])
    assert s1["text"] in r["markdown"]

def test_report_fingerprint(s1):
    psych = {"big_five": {"openness": 0.9, "conscientiousness": 0.5,
                          "extraversion": 0.3, "agreeableness": 0.6, "neuroticism": 0.4},
             "mbti": "INTJ", "enneagram": {"type": 5, "wing": 4}, "attachment": "secure"}
    s2 = sig_for("CAPT")
    r = generate_report(s1, psychology=psych,
                        comparisons=[{"id": s2["id"], "text": s2["text"], "similarity": 0.91}])
    assert s1["fingerprint"]["hash"] in r["markdown"]


# ---- Engine integration ----

def test_dimension_count(s1):
    assert s1["dimensions"] > 56

def test_human_design(s1):
    hd = s1["encoders"].get("human_design", {})
    assert isinstance(hd.get("channels"), list)

def test_astrology(s1):
    a1 = s1["encoders"].get("astrology", {})
    assert bool(a1) and not a1.get("error")
