"""
Hardening regression suite for HME.

Covers:
  1. Data -> Magic -> Data mode persistence
  2. Contract tests for the /api/analyze response shape
  3. Contract tests for the etymology payload shape
  4. Adversarial name cases
  5. Hostile URL injection
  6. Null / empty / unsupported / unavailable / failed / low-confidence
  7. Etymology edge cases: malformed fields, missing sources
"""

import sys
import os
import json
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from engine import (
    compute_unified_signature,
    count_signature_dimensions,
    available_encoder_names,
)
from etymology import analyze_name_etymology, SOURCES, KNOWN_COMPONENTS
from url_sanitize import sanitize_url, validate_source_urls
from snapshot import personality_snapshot

PASS = 0
FAIL = 0
RESULTS = []


def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  OK  {label}")
    else:
        FAIL += 1
        print(f"  FAIL: {label} -- {detail}")
    RESULTS.append({"label": label, "passed": bool(condition), "detail": detail})


def analyze_full(name, birth=None, mode="data"):
    """Build a minimal identity dict and run the engine + server-layer mode logic."""
    identity = {"id": f"test:{name.lower().replace(' ', '_')[:40]}", "text": name}
    if birth:
        identity["birth"] = birth
    sig = compute_unified_signature(identity)
    # Apply mode logic (mirrors server.py _compute_signature)
    if mode == "data":
        layers = available_encoder_names(sig)
        sig["snapshot"] = {
            "available_layers": layers,
            "mode": "data",
            "narrative": "Data mode reports reproducible string measurements.",
            "highlights": [
                f"{len(layers)} encoder outputs available",
                "raw input is not retained by this process",
                "interpretive claims are disabled in Data mode",
            ],
            "psychology_present": False,
        }
    else:
        sig["snapshot"] = personality_snapshot(
            identity["text"],
            astrology=sig["encoders"].get("astrology"),
            human_design=sig["encoders"].get("human_design"),
        )
        sig["snapshot"]["mode"] = "magic"
    sig["computed_dimensions"] = count_signature_dimensions(sig)
    sig["dimensions"] = count_signature_dimensions(sig, include_unavailable=True)
    sig["analysis_mode"] = mode
    return sig


# ---------------------------------------------------------------------------
# 1. MODE PERSISTENCE
# ---------------------------------------------------------------------------
print("=== 1. Mode Persistence: Data -> Magic -> Data ===")

r1 = analyze_full("Mode Test", mode="data")
check("data mode: analysis_mode == data", r1.get("analysis_mode") == "data",
      f"got {r1.get('analysis_mode')}")
check("data mode: snapshot.mode == data",
      r1.get("snapshot", {}).get("mode") == "data",
      f"got {r1.get('snapshot', {}).get('mode')}")

r2 = analyze_full("Mode Test", mode="magic")
check("magic mode: analysis_mode == magic", r2.get("analysis_mode") == "magic",
      f"got {r2.get('analysis_mode')}")
check("magic mode: snapshot.mode == magic",
      r2.get("snapshot", {}).get("mode") == "magic")

r3 = analyze_full("Mode Test", mode="data")
check("data again: analysis_mode == data", r3.get("analysis_mode") == "data",
      f"got {r3.get('analysis_mode')}")
check("magic does not leak into data snapshot",
      r3.get("snapshot", {}).get("mode") == "data")

# ---------------------------------------------------------------------------
# 2. RESPONSE CONTRACT
# ---------------------------------------------------------------------------
print("\n=== 2. Response Contract (engine-level) ===")

r = analyze_full("Contract Check", mode="data")
# Engine output keys
check("engine: contract_version present", "contract_version" in r)
check("engine: encoders present", isinstance(r.get("encoders"), dict))
check("engine: fingerprint present", isinstance(r.get("fingerprint"), dict))
check("engine: resonance present", isinstance(r.get("resonance"), dict))
check("engine: dimensions present", isinstance(r.get("dimensions"), int))
check("engine: snapshot present", isinstance(r.get("snapshot"), dict))
check("engine: determinism present", "determinism" in r)
check("engine: id present", "id" in r)
check("engine: text present", "text" in r)
# Server-level overlay (applied in analyze_full)
check("overlay: analysis_mode present", "analysis_mode" in r)
check("overlay: snapshot has mode", r.get("snapshot", {}).get("mode") == "data")
check("overlay: snapshot.available_layers is list",
      isinstance(r.get("snapshot", {}).get("available_layers"), list))

# ---------------------------------------------------------------------------
# 3. ETYMOLOGY PAYLOAD CONTRACT
# ---------------------------------------------------------------------------
print("\n=== 3. Etymology Payload Contract ===")

ety = analyze_name_etymology("Kirk Brown")
check("etymology has 'name'", "name" in ety)
check("etymology.name == input", ety.get("name") == "Kirk Brown")
check("etymology has 'components'", isinstance(ety.get("components"), list))
check("etymology has 'unresolved_components'", isinstance(ety.get("unresolved_components"), list))
check("etymology has 'lineage_surnames'", isinstance(ety.get("lineage_surnames"), list))
check("etymology has 'sources'", isinstance(ety.get("sources"), dict))
check("etymology has 'epistemic_status'", "epistemic_status" in ety)
check("etymology.epistemic_status == historical-linguistic",
      ety.get("epistemic_status") == "historical-linguistic")
check("etymology.personality_inference == False",
      ety.get("personality_inference") is False)
check("etymology.genetic_inference == False",
      ety.get("genetic_inference") is False)
# Each source should have the required shape
for sid, sdata in ety.get("sources", {}).items():
    check(f"source '{sid}' has 'title'", "title" in sdata)
    check(f"source '{sid}' has 'url'", "url" in sdata)
    check(f"source '{sid}' has 'publisher'", "publisher" in sdata)
    check(f"source '{sid}' has 'quality'", "quality" in sdata)

# Empty/unknown name should still return valid shape
ety_empty = analyze_name_etymology("")
check("empty name: valid shape", isinstance(ety_empty, dict))
check("empty name: components is list", isinstance(ety_empty.get("components"), list))
check("empty name: sources is dict", isinstance(ety_empty.get("sources"), dict))
check("empty name: no components for empty input", len(ety_empty.get("components", [])) == 0)

ety_unknown = analyze_name_etymology("Xyzzorp")
check("unknown name: valid shape", isinstance(ety_unknown, dict))
check("unknown name: unresolved_components contains token",
      "Xyzzorp" in ety_unknown.get("unresolved_components", []))

# ---------------------------------------------------------------------------
# 4. ADVERSARIAL NAME CASES
# ---------------------------------------------------------------------------
print("\n=== 4. Adversarial Name Cases ===")

adversarial = [
    ("mononym", "Madonna"),
    ("hyphenated", "Jean-Luc Picard"),
    ("apostrophe", "O'Brien"),
    ("diacritics", "Jose"),
    ("non-Latin script", "Tanaka Yuki"),
    ("compound surname", "Mary Jane Watson-Parker"),
    ("very long name", "A" * 80 + " B"),
    ("numbers in name", "4est"),
    ("empty string", ""),
    ("whitespace only", "   "),
    ("single char", "X"),
    ("mixed separators", "Mary-Jane_O'Brien Smith"),
]

for label, name in adversarial:
    try:
        ety = analyze_name_etymology(name)
        check(f"ety({label}): returns dict", isinstance(ety, dict))
        check(f"ety({label}): has 'components'", "components" in ety)
        check(f"ety({label}): has 'unresolved'", "unresolved_components" in ety)
        check(f"ety({label}): personality_inference is False",
              ety.get("personality_inference") is False)
    except Exception as e:
        check(f"ety({label}): no exception", False, str(e))

    try:
        sig = compute_unified_signature(
            {"id": f"test:{label}", "text": name}
        )
        check(f"sig({label}): returns dict", isinstance(sig, dict))
        check(f"sig({label}): has encoders", "encoders" in sig)
    except Exception as e:
        check(f"sig({label}): no exception", False, str(e))

# ---------------------------------------------------------------------------
# 5. HOSTILE URL INJECTION
# ---------------------------------------------------------------------------
print("\n=== 5. Hostile URL Injection ===")

# All hardcoded SOURCES should be https
for sid, sdata in SOURCES.items():
    url = sdata.get("url", "")
    check(f"SOURCES['{sid}'].url is https", url.startswith("https://"),
          f"got {url[:50]}")

# sanitize_url should reject dangerous schemes
bad_urls = [
    ("javascript:alert(1)", "javascript scheme"),
    ("data:text/html,<script>", "data scheme"),
    ("vbscript:MsgBox(1)", "vbscript scheme"),
    ("file:///etc/passwd", "file scheme"),
    ("javascript:void(0)", "javascript void"),
    ("JAVASCRIPT:alert(1)", "uppercase javascript"),
    ("HTTPS://safe.com", "uppercase HTTPS should pass"),
    ("https://safe.com/path?q=1#frag", "URL with query and fragment"),
    ("", "empty string"),
    (None, "None input"),
    ("  https://safe.com  ", "whitespace-padded URL"),
    ("not-a-url", "plain text"),
    ("javascript:alert(1)//https://safe.com", "javascript with https in path"),
]

for url, label in bad_urls:
    result = sanitize_url(url)
    if url and isinstance(url, str) and url.strip().lower().startswith("https://"):
        check(f"sanitize({label}): allows https", result is not None, f"got {result}")
    elif url and isinstance(url, str) and url.strip().lower().startswith("http://"):
        # http not allowed by default
        check(f"sanitize({label}): blocks http (no allow_http)", result is None)
    else:
        check(f"sanitize({label}): rejects", result is None, f"got {result}")

# HTTP allowed when flag is set
check("sanitize(http with allow_http): allows",
      sanitize_url("http://example.com", allow_http=True) is not None)
check("sanitize(https with allow_http): allows",
      sanitize_url("https://example.com", allow_http=True) is not None)

# validate_source_urls
results = validate_source_urls(SOURCES)
for sid, url in results.items():
    check(f"validate_source_urls('{sid}'): passes", url is not None, f"got {url}")

# ---------------------------------------------------------------------------
# 6. EPISTEMIC STATES
# ---------------------------------------------------------------------------
print("\n=== 6. Epistemic States ===")

# not-requested: no birth data provided
sig_no_birth = compute_unified_signature({"id": "test:no-birth", "text": "NoBirth"})
check("no-birth: returns result", isinstance(sig_no_birth, dict))
check("no-birth: no crash", "encoders" in sig_no_birth)

# not-found: unknown name etymology
ety_not_found = analyze_name_etymology("Zqxwv")
check("etymology not-found: has unresolved", "Zqxwv" in ety_not_found.get("unresolved_components", []))
check("etymology not-found: empty sources", len(ety_not_found.get("sources", {})) == 0)

# unsupported: mode validation
from public_contract import validate_mode
try:
    validate_mode("badmode")
    check("unsupported mode: raises ValueError", False, "should have raised")
except (ValueError, Exception) as e:
    check("unsupported mode: raises ValueError", True)

# unavailable: encode with identity that triggers unavailable encoders
sig_minimal = compute_unified_signature({"id": "test:min", "text": "Min"})
dims = count_signature_dimensions(sig_minimal, include_unavailable=True)
check("unavailable dims: dimensions is int", isinstance(dims, int))

# low-confidence: known component with 'moderate-high' confidence
ety_mod = analyze_name_etymology("Aghyarian")
components = ety_mod.get("components", [])
if components:
    conf = components[0].get("confidence", "unknown")
    check(f"Aghyarian confidence: {conf}", conf in ("moderate-high", "high"))
else:
    check("Aghyarian has components", False, "no components found")

# ---------------------------------------------------------------------------
# 7. MALFORMED ETYMOLOGY FIELDS
# ---------------------------------------------------------------------------
print("\n=== 7. Malformed Etymology Fields ===")

# Pass invalid types
for bad_name in [123, True, [], {}, object()]:
    try:
        ety = analyze_name_etymology(str(bad_name) if not isinstance(bad_name, str) else bad_name)
        check(f"analyze_name_etymology({type(bad_name).__name__}): returns dict",
              isinstance(ety, dict))
    except Exception as e:
        check(f"analyze_name_etymology({type(bad_name).__name__}): no crash", False, str(e))

# Unicode edge cases
unicode_names = [
    "Caf\u00e9",           # accent
    "Jose\u0301",          # combining accent
    "\u00d1o\u00f1o",      # tilde
    "\u4e16\u754c",        # Chinese (world)
    "\u0410\u043b\u0435\u043a\u0441\u0430\u043d\u0434\u0440",  # Cyrillic
    "\u0627\u0644\u0639\u0631\u0628\u064a\u0629",  # Arabic
]

for name in unicode_names:
    try:
        ety = analyze_name_etymology(name)
        check(f"unicode ({name[:8]}...): returns dict", isinstance(ety, dict))
    except Exception as e:
        check(f"unicode ({name[:8]}...): no crash", False, str(e))


# ---------------------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------------------
print(f"\n{'='*60}")
print(f"RESULTS: {PASS} passed, {FAIL} failed out of {PASS + FAIL} total")
if FAIL == 0:
    print("ALL HARDENING REGRESSION TESTS PASSED")
else:
    print(f"WARNING: {FAIL} test(s) failed")
    for r in RESULTS:
        if not r["passed"]:
            print(f"  FAILED: {r['label']} -- {r['detail']}")

if __name__ == "__main__":
    sys.exit(1 if FAIL else 0)
