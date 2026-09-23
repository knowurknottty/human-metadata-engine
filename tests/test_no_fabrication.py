"""Invariant, no-fabrication, and wall-clock-silence enforcement suite.

Mechanises the frozen doctrine (EN-01, EN-08, EN-09, EN-13) as always-on static
checks so promises become CI failures instead of review-time assertions.

Scan discipline: the prohibition scans target **produced keys** and **function
names**. Disclosure text and ``limitations`` wording are explicitly exempt, so
"we do not apply true-solar correction" never trips a support scan.
"""
from __future__ import annotations

import ast
import inspect
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [_ROOT, os.path.join(_ROOT, "src"), os.path.join(_ROOT, "webapp")]

from encoders.bazi import compute_bazi  # noqa: E402
from encoders.jyotish import compute_jyotish  # noqa: E402
from encoders.maya_classical import compute_classical_maya  # noqa: E402
from narrative_helpers import exact_result  # noqa: E402
from synthesis.epistemic_safety import (  # noqa: E402
    MAX_INTERPRETIVE_STRENGTH,
    validate_epistemic_strength,
)
from unsupported_capabilities import (  # noqa: E402
    PROHIBITED_SCALAR_KEY_TOKENS,
    PROHIBITED_SUPPORT_MARKERS,
    REMOVED_EPISTEMIC_KEYS,
    SYSTEMS_WITHOUT_BACKEND,
    UNSUPPORTED_CAPABILITY_FRAGMENTS,
)

ROOT = _ROOT
SRC = os.path.join(ROOT, "src")
DOC = os.path.join(ROOT, "docs", "SIGNATURE_V3.md")

BIRTH = {
    "year": 2000, "month": 1, "day": 7, "hour": 12, "minute": 0,
    "timezone_offset": 8, "lat": 39.9042, "lon": 116.4074,
    "time_accuracy": "exact",
}
UNKNOWN_BIRTH = {**BIRTH, "time_accuracy": "unknown"}
# A Gregorian date whose JDN precedes the GMT 584283 correlation epoch, used to
# exercise the withheld "negative Long Count" branch.
MAYA_PRE_CORRELATION = {"year": -3200, "month": 1, "day": 1}

# EN-08 allowlist: modules that may read the wall clock because they are
# operational tooling rather than result-producing. Keep this list explicit.
WALL_CLOCK_ALLOWLIST = (
    "src/run_all.py",            # elapsed-time reporting in a CLI driver
    "src/coherence_gate.py",     # audit timestamps; passes an explicit tz
    "src/knowledge_bubble.py",   # generated_at audit stamp; explicit tz
    "src/birth_validation.py",   # explicit-tz current-year sanity bound
)

# EN-08 scope: modules whose output becomes a returned result.
RESULT_PRODUCING_MODULES = (
    "src/engine.py",
    "src/time_context.py",
    "src/signature_v3.py",
    "src/timing_v1.py",
    "src/timing_v2.py",
    "src/zodiacal_releasing_v2.py",
    "src/synthesis/plan.py",
    "src/synthesis/realize.py",
    "src/synthesis/extractors.py",
    "src/synthesis/prose_lexicon.py",
    "src/encoders/jyotish.py",
    "src/encoders/bazi.py",
    "src/encoders/maya_classical.py",
)

# EN-01: the three promoted tradition adapters.
TRADITION_ADAPTERS = (
    "src/encoders/jyotish.py",
    "src/encoders/bazi.py",
    "src/encoders/maya_classical.py",
)
# Modules the adapters may legitimately share: contract primitives and the
# validated Gregorian/JDN civil-time primitive. Anything matching a semantic
# conversion role is forbidden to be shared.
ALLOWED_SHARED_ADAPTER_MODULES = {
    "system_contracts", "time_context", "swisseph",
    "datetime", "typing", "collections", "math", "zoneinfo",
    "importlib", "re", "functools", "itertools", "copy", "hashlib",
    "__future__",
}
SEMANTIC_CONVERSION_PATTERN = (
    "convert", "conversion", "calendar", "epoch", "precession",
    "ayanamsa", "correlation", "jieqi", "tzolkin", "day_boundary",
)


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _collect_keys(value, keys=None):
    keys = set() if keys is None else keys
    if isinstance(value, dict):
        for key, item in value.items():
            keys.add(str(key))
            _collect_keys(item, keys)
    elif isinstance(value, list):
        for item in value:
            _collect_keys(item, keys)
    return keys


def _module_import_names(path: str) -> set[str]:
    tree = ast.parse(_read(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def _adapter_function_names(path: str) -> set[str]:
    tree = ast.parse(_read(path))
    names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            names.add(node.name)
    return names


class TestNoFabricationProducedKeys:
    def _all_results(self):
        return (
            compute_jyotish(BIRTH),
            compute_jyotish(UNKNOWN_BIRTH),
            compute_bazi(BIRTH),
            compute_bazi(UNKNOWN_BIRTH),
            compute_classical_maya({"year": 2012, "month": 12, "day": 21}),
            compute_classical_maya({"year": 1000, "month": 1, "day": 1}),
        )

    def test_removed_epistemic_keys_never_reappear_as_produced_keys(self):
        for result in self._all_results():
            keys = _collect_keys(result)
            for removed in REMOVED_EPISTEMIC_KEYS:
                assert removed not in keys, f"{removed} reappeared as a produced key"
            for token in PROHIBITED_SCALAR_KEY_TOKENS:
                assert not any(token in key for key in keys), f"numeric truth scalar key {token}"

    def test_no_epistemic_metadata_scalar_survives_in_the_narrative_surface(self):
        narrative = exact_result()["synthesis"]["narratives"]["plain"]
        keys = _collect_keys(narrative)
        assert "confidence_bound" not in keys
        assert "evidence_density" not in keys
        assert "total_evidence_density" not in keys
        assert "total_evidence_item_count" in keys
        assert any(key == "evidence_item_count" for key in keys)

    def test_no_gene_keys_family_is_registered(self):
        sys.path.insert(0, SRC)
        from synthesis.extractors import EXTRACTORS  # noqa: E402
        for module_path in TRADITION_ADAPTERS + ("src/synthesis/extractors.py", "src/synthesis/system_vocabulary.py"):
            source = _read(os.path.join(ROOT, module_path))
            for absent in SYSTEMS_WITHOUT_BACKEND:
                assert absent not in source, f"{absent} referenced in {module_path}"
        produced = set()
        for extractor in EXTRACTORS:
            assert "gene_keys" not in extractor.__name__
            produced.add(extractor.__name__)
        assert produced

    def test_no_support_markers_in_produced_keys_or_adapters(self):
        for result in self._all_results():
            keys = _collect_keys(result)
            for marker in PROHIBITED_SUPPORT_MARKERS:
                assert not any(marker in key for key in keys), f"support marker {marker} in keys"
        for module_path in TRADITION_ADAPTERS + ("src/engine.py",):
            names = _adapter_function_names(os.path.join(ROOT, module_path))
            for marker in PROHIBITED_SUPPORT_MARKERS:
                assert not any(marker.replace("-", "_") in name for name in names)
                assert not any(marker in name for name in names)

    def test_disclosure_text_is_exempt_from_the_support_scan(self):
        """Negative fixture: disclosure wording must not be branded a support claim."""
        result = compute_bazi(BIRTH)
        limitations_text = " ".join(result["limitations"])
        assert "true/apparent solar-time correction is not applied" in limitations_text
        assert "not applied" in limitations_text
        # The scan above only inspects keys/names, so this text is provably exempt.
        assert "23:00" not in "".join(_collect_keys(result))


class TestNoSharedSemanticConversionLayer:
    def test_only_contract_and_civil_time_primitives_are_shared(self):
        shared: dict[str, set[str]] = {}
        for module_path in TRADITION_ADAPTERS:
            shared[module_path] = _module_import_names(os.path.join(ROOT, module_path))
        counts: dict[str, int] = {}
        for names in shared.values():
            for name in names:
                counts[name] = counts.get(name, 0) + 1
        multi = {name for name, count in counts.items() if count > 1}
        unexpected = multi - ALLOWED_SHARED_ADAPTER_MODULES
        assert unexpected == set(), f"unreviewed shared imports across adapters: {sorted(unexpected)}"
        for name in multi:
            assert not any(token in name for token in SEMANTIC_CONVERSION_PATTERN)

    def test_positive_and_negative_fixtures_for_the_shared_layer_rule(self):
        offending = {"semantic_calendar_convert", "tradition_conversion", "jieqi_helper"}
        allowed = {"system_contracts", "time_context"}
        for name in offending:
            assert any(token in name for token in SEMANTIC_CONVERSION_PATTERN)
        for name in allowed:
            assert not any(token in name for token in SEMANTIC_CONVERSION_PATTERN)


class TestSharedSourceNeverIndependentEvidence:
    def test_duplicate_source_rows_never_become_independent_evidence(self):
        items = exact_result()["synthesis"]["evidence"]["evidence_items"]
        by_pair: dict[tuple[str, str], set[str]] = {}
        for item in items:
            key = (item["system"], str(item.get("source_value")))
            by_pair.setdefault(key, set()).add(item.get("independence_group"))
        for key, groups in by_pair.items():
            assert len(groups) == 1, f"shared source {key} split across groups {groups}"

    def test_reading_only_rows_never_increment_a_motif_vote(self):
        result = exact_result()
        items = result["synthesis"]["evidence"]["evidence_items"]
        reading_only_ids = {
            item["evidence_id"] for item in items
            if item["symbol_family"].startswith(("roadmap_", "binary_prime_"))
        }
        assert reading_only_ids
        for motif in result["synthesis"]["plan"]["dominant_motifs"]:
            assert reading_only_ids.isdisjoint(motif["evidence_ids"])

    def test_shared_source_registry_witnesses_are_documented(self):
        assets = _read(os.path.join(SRC, "synthesis", "system_vocabulary.py"))
        assert "sys-gematria-007" in assets
        assert "sys-kabbalah-006" in assets


class TestWallClockSilence:
    NO_ARG_CALLS = ("time.time", "datetime.now", "date.today", "time.localtime")

    def _calls(self, path: str) -> set[str]:
        return self._calls_from_source(_read(path))

    def _calls_from_source(self, source: str) -> set[str]:
        tree = ast.parse(source)
        found = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Attribute):
                name = f"{getattr(func.value, 'id', '')}.{func.attr}"
            elif isinstance(func, ast.Name):
                name = func.id
            else:
                continue
            if node.args or node.keywords:
                continue  # explicit-argument constructors are allowed
            found.add(name)
        return found

    def test_result_producing_modules_never_read_the_wall_clock_silently(self):
        offenders = {}
        for module_path in RESULT_PRODUCING_MODULES:
            path = os.path.join(ROOT, module_path)
            assert os.path.exists(path), f"scope path missing: {module_path}"
            bad = self._calls(path) & set(self.NO_ARG_CALLS)
            if bad:
                offenders[module_path] = sorted(bad)
        assert offenders == {}, f"silent wall-clock reads: {offenders}"

    def test_scan_fixtures_positive_and_negative(self):
        positive = "def f():\n    return time.time()\n"
        negative = "def f(now):\n    return datetime.now(now)\n"
        assert self._calls_from_source(positive) & set(self.NO_ARG_CALLS)
        assert not self._calls_from_source(negative) & set(self.NO_ARG_CALLS)

    def test_allowlist_is_documented_and_explicit(self):
        assert isinstance(WALL_CLOCK_ALLOWLIST, tuple)
        assert all(entry.startswith("src/") for entry in WALL_CLOCK_ALLOWLIST)
        # Allowlisted modules must be outside the result-producing scope.
        assert not set(WALL_CLOCK_ALLOWLIST) & set(RESULT_PRODUCING_MODULES)


class TestUnsupportedCapabilityRegistry:
    def _limitations_for(self, system: str) -> list[str]:
        if system == "jyotish":
            return compute_jyotish(BIRTH)["limitations"] + compute_jyotish(UNKNOWN_BIRTH)["limitations"]
        if system == "bazi":
            return compute_bazi(BIRTH)["limitations"] + compute_bazi(UNKNOWN_BIRTH)["limitations"]
        if system == "maya_classical":
            return (
                compute_classical_maya({"year": 2012, "month": 12, "day": 21})["limitations"]
                + compute_classical_maya(MAYA_PRE_CORRELATION)["limitations"]
            )
        raise AssertionError(f"unknown system {system}")

    def test_registry_equals_encoder_limitations_wording(self):
        for system, capabilities in UNSUPPORTED_CAPABILITY_FRAGMENTS.items():
            published = " ".join(self._limitations_for(system))
            for capability, fragment in capabilities.items():
                assert fragment in published, f"{system}.{capability} disclosure drifted: {fragment!r}"

    def test_registry_shape_fixture(self):
        assert set(UNSUPPORTED_CAPABILITY_FRAGMENTS) == {"jyotish", "bazi", "maya_classical"}
        for system, capabilities in UNSUPPORTED_CAPABILITY_FRAGMENTS.items():
            assert capabilities, f"{system} registry is empty"
            for capability, fragment in capabilities.items():
                assert isinstance(capability, str) and capability
                assert isinstance(fragment, str) and len(fragment.split()) >= 3
                # Must not describe an absent capability as a configurable mode.
                assert "configurable" not in fragment
                assert "enable" not in fragment

    def test_no_output_field_asserts_true_solar_or_rollover_support(self):
        for result in (compute_bazi(BIRTH), compute_bazi(UNKNOWN_BIRTH)):
            keys = _collect_keys(result)
            assert not any("true_solar" in key or "true_solar_time" in key for key in keys)
            assert not any("rollover" in key for key in keys)

    def test_withholding_branches_are_explicit(self):
        assert compute_jyotish(UNKNOWN_BIRTH)["status"] == "input_insufficient"
        bazi_unknown = compute_bazi(UNKNOWN_BIRTH)["calculation"]
        assert bazi_unknown["pillars"]["hour"] is None
        maya_negative = compute_classical_maya(MAYA_PRE_CORRELATION)
        assert maya_negative["status"] == "unavailable"

    def test_registry_is_documented(self):
        doc = _read(DOC)
        assert "src/unsupported_capabilities.py" in doc
        assert "Gene Keys" in doc
        assert "confidence_bound" in doc


class TestPinnedEpistemicStrengthContract:
    def test_known_good_strength_returns_true(self):
        valid, issues = validate_epistemic_strength([{"text": "bounded", "strength": 2.0}], "plain")
        assert valid is True
        assert issues == []

    def test_overclaiming_strength_returns_false_with_issues(self):
        valid, issues = validate_epistemic_strength([{"text": "too strong", "strength": 9.0}], "plain")
        assert valid is False
        assert issues
        valid_mythic, issues_mythic = validate_epistemic_strength(
            [{"text": "too strong", "strength": MAX_INTERPRETIVE_STRENGTH + 1}], "mythic"
        )
        assert valid_mythic is False and issues_mythic

    def test_valid_is_true_iff_issues_is_empty(self):
        matrix = [
            ([], "plain"), ([{"strength": 1}], "plain"), ([{"strength": 5}], "plain"),
            ([{"strength": 5}], "mythic"), ([{"strength": 6}], "mythic"),
            ([{"strength": 9}], "research"), ([{"strength": 2}], "unlisted_mode"),
        ]
        for claims, mode in matrix:
            valid, issues = validate_epistemic_strength(claims, mode)
            assert valid is (len(issues) == 0)

    def test_docstring_equals_the_asserted_contract(self):
        doc = inspect.getdoc(validate_epistemic_strength) or ""
        for phrase in (
            "Returns ``(valid, issues)``",
            "if and only if",
            "is not a truth-confidence scalar",
            "``plain`` and ``research``",
        ):
            assert phrase in doc, f"missing contract phrase: {phrase!r}"

    def test_realize_binding_reads_the_documented_element(self):
        narrative = exact_result()["synthesis"]["narratives"]["plain"]
        plan = exact_result()["synthesis"]["plan"]
        claims = [
            claim
            for section in plan["narrative_sections"]
            if section["section_id"] != "evidence_ledger"
            for claim in section["claims"]
        ]
        expected, issues = validate_epistemic_strength(claims, "plain")
        assert narrative["epistemic_validation"]["strength_valid"] is expected
        assert narrative["epistemic_validation"]["strength_issues"] == ([] if expected else issues)
        assert "strength_valid" in narrative["epistemic_validation"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
