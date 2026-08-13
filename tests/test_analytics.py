"""
Tests for v0.4.0 analytics: composite resonance, fingerprints,
correlations, similarity, batch report, snapshots, and the
long-form report generator.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from engine import compute_unified_signature
from analytics import (
    composite_resonance, identity_fingerprint, feature_vector,
    cosine_similarity, feature_agreement, identity_similarity_matrix,
    cross_encoder_correlations, batch_report, FEATURE_ORDER,
)
from snapshot import personality_snapshot
from report import generate_report

PASS = 0
FAIL = 0


def check(name, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✓ {name}")
    else:
        FAIL += 1
        print(f"  ✗ {name}")


def sig_for(text, birth=None):
    ident = {"id": f"test:{text.lower().replace(' ', '_')}", "text": text}
    if birth:
        ident["birth"] = birth
    return compute_unified_signature(ident)


print("Analytics Tests")
print("=" * 60)

s1 = sig_for("John Michael Smith",
             birth={"year": 1985, "month": 6, "day": 15, "hour": 10, "minute": 30,
                    "timezone_offset": -7, "location": "Portland, Oregon, USA",
                    "lat": 45.5152, "lon": -122.6765})
s2 = sig_for("CAPT")
s3 = sig_for("Albert Einstein")
s4 = sig_for("Jenn")
sigs = [s1, s2, s3, s4]

# ---- Composite resonance ----
r1 = composite_resonance(s1)
check("resonance score in [0, 100]", 0 <= r1["score"] <= 100)
check("resonance has 4 components", len(r1["components"]) == 4)
check("all components in [0, 1]",
      all(0 <= v <= 1 for v in r1["components"].values()))
check("weights sum to 1.0", abs(sum(r1["weights"].values()) - 1.0) < 1e-9)
check("resonance deterministic", composite_resonance(s1)["score"] == r1["score"])
check("engine embeds resonance", s1.get("resonance", {}).get("score") == r1["score"])

# ---- Fingerprint ----
f1 = identity_fingerprint(s1)
f2 = identity_fingerprint(s2)
check("fingerprint hash is 16 hex chars",
      len(f1["hash"]) == 16 and all(c in "0123456789abcdef" for c in f1["hash"]))
check("different names, different hashes", f1["hash"] != f2["hash"])
check("fingerprint deterministic", identity_fingerprint(s1)["hash"] == f1["hash"])
check("symmetry in [3, 9]", 3 <= f1["symmetry"] <= 9)
check("7 spokes (core encoders)", len(f1["spokes"]) == 7)
check("spoke values normalized", all(0 <= sp["value"] <= 1 for sp in f1["spokes"]))
check("ring pattern is the binary string",
      f1["ring_pattern"] == s1["encoders"]["binary_prime"]["binary_string"])

# ---- Feature vectors / similarity ----
v1 = feature_vector(s1)
check("feature vector matches FEATURE_ORDER length", len(v1) == len(FEATURE_ORDER))
check("features normalized to [0, 1]", all(0 <= x <= 1 for x in v1))
check("self-similarity is 1.0", abs(cosine_similarity(v1, v1) - 1.0) < 1e-9)
check("feature agreement with self is 1.0", abs(feature_agreement(v1, v1) - 1.0) < 1e-9)
discrete_left = [0.0] * 8 + [0.5] * 6
discrete_right = [1.0 / 9.0] * 8 + [0.5] * 6
check("different digit categories do not look numerically close",
      abs(feature_agreement(discrete_left, discrete_right) - (6 / 14)) < 1e-9)
sim = identity_similarity_matrix(sigs)
check("comparison matrix declares feature agreement", sim["metric"] == "feature_agreement_v1")
check("similarity matrix is square",
      len(sim["matrix"]) == 4 and all(len(row) == 4 for row in sim["matrix"].values()))
check("diagonal is 1.0",
      all(abs(sim["matrix"][i][i] - 1.0) < 1e-6 for i in sim["ids"]))
check("matrix symmetric",
      all(sim["matrix"][a][b] == sim["matrix"][b][a]
          for a in sim["ids"] for b in sim["ids"]))
check("3 nearest neighbors per identity",
      all(len(n) == 3 for n in sim["nearest_neighbors"].values()))
check("nearest-neighbor values are agreement scores",
      all(0 <= n["agreement"] <= 1
          for neighbors in sim["nearest_neighbors"].values() for n in neighbors))

# ---- Cross-encoder correlations ----
corr = cross_encoder_correlations(sigs)
check("pearson matrix covers 7 encoders", len(corr["pearson"]) == 7)
check("pearson diagonal is 1.0",
      all(abs(corr["pearson"][e][e] - 1.0) < 1e-6 for e in corr["magnitude_encoders"]))
check("pearson values in [-1, 1]",
      all(-1 <= corr["pearson"][a][b] <= 1
          for a in corr["magnitude_encoders"] for b in corr["magnitude_encoders"]))
check("digit agreement diagonal is 1.0",
      all(corr["digit_agreement"][e][e] == 1.0 for e in corr["digit_encoders"]))
check("digit agreement in [0, 1]",
      all(0 <= corr["digit_agreement"][a][b] <= 1
          for a in corr["digit_encoders"] for b in corr["digit_encoders"]))

# ---- Batch report ----
rep_json, rep_md = batch_report(sigs)
check("batch ranking covers all identities", len(rep_json["ranking"]) == 4)
check("ranking sorted descending",
      all(rep_json["ranking"][i]["resonance"] >= rep_json["ranking"][i + 1]["resonance"]
          for i in range(3)))
check("markdown report has ranking table", "| Rank |" in rep_md)
check("markdown report has agreement matrix", "Digit Agreement" in rep_md)

# ---- Snapshot ----
snap_empty = personality_snapshot("Test Name")
check("empty snapshot has no layers", snap_empty["available_layers"] == [])
check("empty snapshot still has narrative", len(snap_empty["narrative"]) > 50)
psych = {"big_five": {"openness": 0.9, "conscientiousness": 0.5,
                      "extraversion": 0.3, "agreeableness": 0.6, "neuroticism": 0.4},
         "mbti": "INTJ", "enneagram": {"type": 5, "wing": 4}, "attachment": "secure"}
snap_p = personality_snapshot("Test Name", psychology=psych)
check("psychology layer detected", "psychology" in snap_p["available_layers"])
check("MBTI appears in narrative", "INTJ" in snap_p["narrative"])
astro = s3["encoders"].get("astrology")
if astro and not astro.get("error"):
    snap_a = personality_snapshot("Albert Einstein", astrology=astro)
    check("astrology layer detected", "astrology" in snap_a["available_layers"])
    check("sun sign in narrative", astro["sun_sign"] in snap_a["narrative"])
else:
    check("astrology layer detected (skipped, no swisseph)", True)
    check("sun sign in narrative (skipped, no swisseph)", True)
check("engine embeds snapshot", "snapshot" in s1)

# ---- Long-form report ----
r = generate_report(s1, psychology=psych,
                    comparisons=[{"id": s2["id"], "text": s2["text"], "similarity": 0.91}])
check("report includes all 10 sections when data present",
      r["sections"] == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
      if (s1["encoders"].get("astrology") and not s1["encoders"]["astrology"].get("error"))
      else 5 not in r["sections"])
check("full report exceeds 3000 words", r["word_count"] >= 3000)
check("report is deterministic",
      generate_report(s1, psychology=psych,
                      comparisons=[{"id": s2["id"], "text": s2["text"], "similarity": 0.91}]
                      )["markdown"] == r["markdown"])
r_min = generate_report(s2)
check("name-only report skips sections 5 and 6",
      5 not in r_min["sections"] and 6 not in r_min["sections"])
check("name-only report still substantial", r_min["word_count"] >= 2000)
check("report mentions the name", s1["text"] in r["markdown"])
check("report embeds fingerprint hash", s1["fingerprint"]["hash"] in r["markdown"])

# ---- Engine integration ----
check("engine dimension count grew with analytics", s1["dimensions"] > 56)
hd = s1["encoders"].get("human_design", {})
check("human design has channels list", isinstance(hd.get("channels"), list))
a1 = s1["encoders"].get("astrology", {})
check("astrology computed without error", bool(a1) and not a1.get("error"))
print()
print("=" * 60)
print(f"Analytics Tests: {PASS} passed, {FAIL} failed out of {PASS + FAIL}")
print("=" * 60)
sys.exit(1 if FAIL else 0)
