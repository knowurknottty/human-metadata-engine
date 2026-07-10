"""
Regression + privacy suite for src/fingerprint.py

Proves:
  1. Same-input reproducibility (two calls, same process)
  2. Change sensitivity (single char diff changes full output)
  3. Excluded-field absence in SVG output
  4. Excluded-field absence in inline-SVG HTML export
  5. HMAC private projection structure
  6. Canonical bytes are deterministic and JSON-parseable
  7. Manifest binding integrity (all 6 layers, epistemic labels)
  8. Digest changes when projection changes
  9. SVG contains all 6 layer <g> groups with correct ids
  10. SVG data-* attributes present (digest, schema, render, mode)
"""

import re
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from fingerprint import (
    generate_fingerprint_svg,
    build_public_projection,
    build_private_projection,
    build_manifest,
    render_sigil_svg,
    export_manual_html,
    _canonical_bytes,
    _digest_hex,
)

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  \u2713 {name}")
    else:
        FAIL += 1
        print(f"  \u2717 {name}" + (f"  [{detail}]" if detail else ""))


# ---------------------------------------------------------------------------
# Fixture -- contains every excluded field category
# ---------------------------------------------------------------------------
_SIG = {
    "id": "test:alice",
    "text": "Alice Wonderland",
    "mbti": {"type": "INFJ", "score": 0.87},
    "numerology": {"life_path": 7},
    # --- excluded ---
    "birth": {"year": 1990, "month": 3, "day": 14},
    "lat": 45.51,
    "lon": -122.67,
    "location": "Portland, OR",
    "health": {"notes": "private-data"},
    "neuro": {"eeg": [1, 2, 3]},
    "contacts": ["bob@example.com"],
    "relationships": {"partner": "Bob"},
    "tokens": {"api": "sk-secret-key"},
    "private_notes": "eyes only",
    "assessments": {"raw": "redacted-score"},
}

EXCLUDED_FIELDS = [
    "birth", "lat", "lon", "location",
    "health", "neuro", "contacts", "relationships",
    "tokens", "private_notes", "assessments",
    # substring sentinels that must not leak
    "sk-secret", "private-data", "redacted-score", "eyes only",
    "bob@example.com",
]

print("\nSigil Regression + Privacy Suite")
print("=" * 60)

# 1. Reproducibility
svg_a = generate_fingerprint_svg(_SIG)
svg_b = generate_fingerprint_svg(_SIG)
check("same-input reproducibility", svg_a == svg_b)

# 2. Change sensitivity
_SIG2 = {**_SIG, "text": _SIG["text"] + "x"}
svg_c = generate_fingerprint_svg(_SIG2)
check("single-char change alters SVG", svg_a != svg_c)

# 3. Excluded fields absent from SVG
for field in EXCLUDED_FIELDS:
    check(f"excluded absent from SVG: {field}", field not in svg_a)

# 4. Excluded fields absent from HTML manual (inline SVG)
with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as tf:
    tmp_path = tf.name
export_manual_html([_SIG], outpath=tmp_path)
html_content = open(tmp_path, encoding="utf-8").read()
os.unlink(tmp_path)
for field in EXCLUDED_FIELDS:
    check(f"excluded absent from HTML: {field}", not re.search(rf'\b{re.escape(field)}\b', html_content))

# 5. HMAC private projection
priv = build_private_projection(_SIG, secret=b"test-secret-key")
check("private projection has _hmac_sha256", "_hmac_sha256" in priv)
check("private projection mode tag", priv.get("_projection") == "private")
check("HMAC is valid 64-char hex", len(priv["_hmac_sha256"]) == 64)
check("HMAC changes with different secret",
      build_private_projection(_SIG, b"other")["_hmac_sha256"] !=
      priv["_hmac_sha256"])

# 6. Canonical bytes deterministic + parseable
cb1 = _canonical_bytes(_SIG)
cb2 = _canonical_bytes(_SIG)
check("canonical bytes deterministic", cb1 == cb2)
try:
    parsed = json.loads(cb1.decode("utf-8"))
    check("canonical bytes are valid UTF-8 JSON", isinstance(parsed, dict))
except Exception as e:
    check("canonical bytes are valid UTF-8 JSON", False, str(e))

# 7. Manifest binding integrity
proj = build_public_projection(_SIG)
mf   = build_manifest(proj, mode="public")
check("manifest digest is 64-char hex", len(mf["digest"]) == 64)
check("manifest schema_version == 1.0.0", mf["schema_version"] == "1.0.0")
check("manifest render_spec == sigil-v1", mf["render_spec"] == "sigil-v1")
check("manifest projection_mode == public", mf["projection_mode"] == "public")
check("manifest has exactly 6 layers", len(mf["layers"]) == 6)
check("epistemic keys match layer list",
      set(mf["epistemic"].keys()) == set(mf["layers"]))
EPISTEMIC_VALID = {"Established", "Experimental", "Speculative"}
for layer, label in mf["epistemic"].items():
    check(f"epistemic label valid: {layer}", label in EPISTEMIC_VALID)

# 8. Digest changes with projection change
proj2 = build_public_projection(_SIG2)
mf2   = build_manifest(proj2)
check("digest changes with input change", mf["digest"] != mf2["digest"])

# 9. SVG layer group ids
for layer in mf["layers"]:
    check(f'SVG has <g id="layer-{layer}">', f'id="layer-{layer}"' in svg_a)

# 10. SVG data-* attributes
for attr in ["data-digest", "data-schema", "data-render", "data-mode"]:
    check(f"SVG has {attr}", attr in svg_a)

# 11. Public projection excludes all sensitive keys
for k in ["birth", "lat", "lon", "location", "health",
          "neuro", "contacts", "relationships", "tokens",
          "private_notes", "assessments"]:
    check(f"public projection strips: {k}", k not in proj)

# 12. Public projection preserves allowed keys
check("public projection retains id",  "id"  in proj)
check("public projection retains text", "text" in proj)
check("public projection retains mbti", "mbti" in proj)

print(f"\n{'='*60}")
print(f"PASS: {PASS}  FAIL: {FAIL}")
if FAIL:
    sys.exit(1)
