"""Truth-bounded public reports.

``report.py`` is retained as the legacy long-form compatibility formatter.
This module is the only formatter used by the public server.  It builds a
shorter report from structured engine output instead of repairing legacy prose
with string replacements.
"""

from __future__ import annotations

from typing import Any

from engine import available_encoder_names


EVIDENCE_MODEL = "computed-self_report-symbolic-experimental-v2"


def _md(value: Any) -> str:
    """Escape user-controlled text for the report's supported Markdown subset."""
    text = str(value)
    for marker in ("\\", "`", "*", "_", "[", "]", "#"):
        text = text.replace(marker, "\\" + marker)
    return text


def _meta(
    section: int,
    title: str,
    category: str,
    *,
    validation: str,
    provenance: list[str],
    limitations: list[str],
) -> dict[str, Any]:
    return {
        "section": section,
        "title": title,
        "category": category,
        "evidence_level": {
            "mathematical": "direct_calculation",
            "astronomical": "ephemeris_calculation",
            "user_reported": "supplied_by_user",
            "traditional_symbolic": "traditional_framework",
            "heuristic": "configured_method",
            "speculative_synthesis": "interpretive_synthesis",
        }[category],
        "confidence": None,
        "deterministic": True,
        "scientific_validation": validation,
        "provenance": provenance,
        "limitations": limitations,
    }


def _common_metadata() -> list[dict[str, Any]]:
    return [
        _meta(1, "Identity and input summary", "user_reported", validation="not_applicable",
              provenance=["analysis-v1 normalized input"],
              limitations=["Exact birth location, coordinates, and time are omitted from the export."]),
        _meta(2, "Data quality and calculation coverage", "heuristic", validation="method_dependent",
              provenance=["signature-v2 availability flags"],
              limitations=["Coverage is not accuracy and missing evidence is not imputed."]),
        _meta(3, "Plain-English overview", "speculative_synthesis", validation="not_established",
              provenance=["resonance-v3 configured components"],
              limitations=["The convergence index is not a probability, diagnosis, or measure of worth."]),
        _meta(4, "Deterministic name calculations", "mathematical", validation="calculation_reproducible",
              provenance=["Pythagorean", "Chaldean", "ordinal", "linguistic encoders"],
              limitations=["Numerology mappings are traditional conventions; arithmetic correctness does not validate personality claims."]),
        _meta(5, "Astronomical birth-chart calculations", "astronomical", validation="ephemeris_computed",
              provenance=["Swiss Ephemeris tropical chart"],
              limitations=["Astrological interpretation is traditional and not scientifically established."]),
        _meta(6, "Human Design", "traditional_symbolic", validation="not_established",
              provenance=["true-human-design-core-v1 when available"],
              limitations=["A versioned symbolic calculation is not a validated personality assessment."]),
        _meta(7, "User-supplied psychology", "user_reported", validation="depends_on_source_method",
              provenance=["public request psychology fields"],
              limitations=["The engine does not independently verify, diagnose, or upgrade self-report status."]),
        _meta(8, "Cross-system synthesis", "speculative_synthesis", validation="not_established",
              provenance=["configured report synthesis"],
              limitations=["Repeated themes across symbolic systems are not independent evidence."]),
        _meta(9, "Agreements, tensions, and contradictions", "heuristic", validation="method_dependent",
              provenance=["configured output comparison"],
              limitations=["Output agreement is not personal similarity or objective compatibility."]),
        _meta(10, "Provenance, limitations, and reproduction", "mathematical", validation="calculation_reproducible",
              provenance=["analysis-v1", "signature-v2", EVIDENCE_MODEL],
              limitations=["Reproducibility establishes stable computation, not empirical validity."]),
    ]


def _data_report(sig: dict, psychology: dict | None = None, comparisons: list[dict] | None = None) -> dict:
    """Build a compact evidence-first report without interpretive prose."""
    encoders = sig.get("encoders", {})
    pyth = encoders.get("pythagorean", {})
    ling = encoders.get("linguistic", {})
    resonance = sig.get("resonance", {})
    lines = [
        f"# Identity Resonance Data Report — {_md(sig.get('text', 'Unknown'))}",
        "",
        "> **How to read this report**",
        "> Data mode reports reproducible string measurements, provenance, and configured comparison outputs. It does not infer personality, fate, cultural origin, or real-world similarity from a name.",
        "",
        "## 1. Input and method",
        "",
        f"- Contract: `{_md(sig.get('contract_version', 'signature-v2'))}`",
        "- Analysis mode: `data`",
        f"- Encoder outputs available: `{len(available_encoder_names(sig))}`",
        f"- Computed dimensions: `{sig.get('computed_dimensions', sig.get('dimensions', 0))}`",
        "- Exact birth location, coordinates, and time are intentionally excluded from this export.",
        "",
        "## 2. Computed measurements",
        "",
        f"- Pythagorean expression: `{pyth.get('expression', '—')}`; total `{pyth.get('total', '—')}`",
        f"- Chaldean name number: `{encoders.get('chaldean', {}).get('name_number', '—')}`",
        f"- Ordinal reduced value: `{encoders.get('ordinal', {}).get('ordinal_reduced', '—')}`",
        f"- Letter count: `{ling.get('letter_count', '—')}`",
        f"- Entropy ratio: `{float(ling.get('entropy_ratio', 0)):.3f}`",
        f"- Pattern convergence index: `{resonance.get('score', '—')}/100` (configured output agreement; not accuracy or probability)",
        "",
        "## 3. Evidence coverage",
        "",
        "Computed string structure, self-report, astronomical calculations, and symbolic layers remain separate. Missing evidence is not imputed.",
        f"- Psychology supplied: `{'yes' if psychology else 'no'}`",
        f"- Reference rows returned: `{len(comparisons or [])}`",
        "",
        "## 4. Limitations",
        "",
        "These outputs describe configured encoders over an input string. They do not establish personality, causation, cultural origin, employment suitability, health status, compatibility, or a relationship between people.",
    ]
    markdown = "\n".join(lines) + "\n"
    return {
        "markdown": markdown,
        "word_count": len(markdown.split()),
        "sections": [1, 2, 3, 4],
        "section_metadata": [
            _meta(1, "Input and method", "user_reported", validation="not_applicable",
                  provenance=["analysis-v1 normalized input"],
                  limitations=["Exact birth location, coordinates, and time are omitted from the export."]),
            _meta(2, "Computed measurements", "mathematical", validation="calculation_reproducible",
                  provenance=["signature-v2 public encoder outputs"],
                  limitations=["Traditional meanings assigned to calculated numbers are not measurements."]),
            _meta(3, "Evidence coverage", "heuristic", validation="method_dependent",
                  provenance=[EVIDENCE_MODEL],
                  limitations=["Coverage is not accuracy and missing evidence is not imputed."]),
            _meta(4, "Limitations", "mathematical", validation="not_applicable",
                  provenance=["analysis-v1 public claim policy"],
                  limitations=["The listed exclusions apply to every Data report output."]),
        ],
        "evidence_model": EVIDENCE_MODEL,
        "mode": "data",
    }


def _psychology_summary(psychology: dict | None) -> list[str]:
    if not psychology:
        return ["No psychology fields were supplied. The engine does not infer them from the name."]
    lines: list[str] = []
    if psychology.get("mbti"):
        lines.append(f"MBTI: `{_md(psychology['mbti'])}` (user supplied)")
    enneagram = psychology.get("enneagram") or {}
    if enneagram.get("type"):
        wing = f"w{enneagram['wing']}" if enneagram.get("wing") else "no wing supplied"
        lines.append(f"Enneagram: `Type {enneagram['type']} {wing}` (user supplied)")
    relational = psychology.get("relational_patterns") or {}
    if relational.get("attachment_style"):
        lines.append(f"Relational patterns — attachment style: `{_md(relational['attachment_style'])}` (user supplied)")
    answered_big_five = sorted(
        key for key, value in (psychology.get("big_five") or {}).items() if value is not None
    )
    if answered_big_five:
        lines.append("Big Five fields supplied: " + ", ".join(_md(key) for key in answered_big_five))
    return lines or ["Psychology metadata was supplied, but no supported scored field was answered."]


def _magic_report(sig: dict, psychology: dict | None, comparisons: list[dict] | None) -> dict:
    encoders = sig.get("encoders", {})
    pyth = encoders.get("pythagorean", {})
    chaldean = encoders.get("chaldean", {})
    ordinal = encoders.get("ordinal", {})
    linguistic = encoders.get("linguistic", {})
    astrology = encoders.get("astrology") or {}
    human_design = encoders.get("human_design") or {}
    resonance = sig.get("resonance") or {}
    has_astrology = bool(astrology and not astrology.get("error") and astrology.get("sun_sign"))
    hd_available = human_design.get("available") is True and human_design.get("status") == "provisional_calculation"
    extensions = [
        value for value in encoders.values()
        if isinstance(value, dict) and value.get("system") and value.get("provenance")
    ]
    roots = [
        pyth.get("expression"), chaldean.get("name_number"),
        encoders.get("gematria", {}).get("absolute_reduced"),
        encoders.get("isopsephy", {}).get("reduced"),
    ]
    psychology_lines = _psychology_summary(psychology)
    closest = (comparisons or [{}])[0]

    if has_astrology:
        if astrology.get("date_only") or astrology.get("time_sensitive_fields_withheld"):
            astronomy_lines = [
                f"- Sun sign: `{astrology.get('sun_sign')}`.",
                "- Birth time was unavailable or uncertain; Moon, rising sign, houses, aspects, and Human Design are withheld.",
            ]
        else:
            astronomy_lines = [
                f"- Sun: `{astrology.get('sun_sign', '—')}`; Moon: `{astrology.get('moon_sign', '—')}`; rising sign: `{astrology.get('ascendant', '—')}`.",
                f"- Major aspects returned: `{len(astrology.get('aspects') or [])}`; `{len(astrology.get('house_cusps') or [])}` {astrology.get('house_system', 'configured')} house cusps returned.",
            ]
    else:
        astronomy_lines = ["- No usable birth-chart calculation is available for this run."]

    if hd_available:
        hd_lines = [
            f"- Versioned calculation status: `{human_design.get('status')}`.",
            f"- Type: `{human_design.get('type', '—')}`; strategy: `{human_design.get('strategy', '—')}`; authority: `{human_design.get('authority', '—')}`; profile: `{human_design.get('profile', '—')}`.",
            "- Within this symbolic framework, these are rule-derived labels. They are not a validated personality assessment.",
        ]
    else:
        reason = human_design.get("reason") or human_design.get("unavailable") or "Required precise birth inputs were not available."
        hd_lines = [f"- Human Design status: unavailable — {_md(reason)}"]
        if human_design.get("user_reported_type"):
            hd_lines.append(f"- User-reported type: **{_md(human_design['user_reported_type'])}** (self-report only).")

    lines = [
        f"# Identity Resonance Report — {_md(sig.get('text', 'Unknown'))}",
        "",
        "> **How to read this report**",
        "> Direct calculations, astronomy, self-report, traditional symbolic interpretation, and synthesis are labeled separately. The pattern convergence index is not a percentage of accuracy. This report is not diagnosis, prediction, destiny, or an empirical personality assessment.",
        "",
        "## 1. Identity and input summary",
        "",
        f"- Analyzed identity: **{_md(sig.get('text', 'Unknown'))}**.",
        f"- Analysis mode: `magic`; contract: `{_md(sig.get('contract_version', 'signature-v2'))}`.",
        f"- Birth-derived calculation present: `{'yes' if has_astrology else 'no'}`; psychology supplied: `{'yes' if psychology else 'no'}`.",
        "- Exact birth location, coordinates, and time are omitted from this export.",
        "",
        "## 2. Data quality and calculation coverage",
        "",
        f"- Available encoder outputs: `{len(available_encoder_names(sig))}`; computed dimensions: `{sig.get('computed_dimensions', sig.get('dimensions', 0))}`.",
        f"- Provenance-aware symbolic extensions: `{len(extensions)}`.",
        "- Missing inputs remain missing. The engine does not substitute a noon birth time or current UTC offset.",
        "",
        "## 3. Plain-English overview",
        "",
        f"The configured pattern convergence index is **{resonance.get('score', '—')}/100**. It summarizes agreement among configured output components. A higher number is not greater accuracy, ability, worth, compatibility, or certainty.",
        "",
        "Within this symbolic framework, repeated patterns can be used as reflection prompts. Treat any prompt as a hypothesis to compare with observed behavior, not as a fact about the person.",
        "",
        "## 4. Deterministic name calculations",
        "",
        f"- Pythagorean: expression `{pyth.get('expression', '—')}`, soul urge `{pyth.get('soul_urge', '—')}`, personality `{pyth.get('personality', '—')}`.",
        f"- Chaldean: name number `{chaldean.get('name_number', '—')}`, compound `{chaldean.get('compound_number', '—')}`.",
        f"- Ordinal: total `{ordinal.get('ordinal_total', '—')}`, reduced `{ordinal.get('ordinal_reduced', '—')}`.",
        f"- Linguistic: `{linguistic.get('letter_count', '—')}` letters, entropy ratio `{float(linguistic.get('entropy_ratio', 0)):.3f}`.",
        "",
        "The arithmetic above is reproducible. Traditional meanings assigned to those numbers are symbolic conventions and are not scientifically established personality measurements.",
        "",
        "## 5. Astronomical birth-chart calculations",
        "",
        *astronomy_lines,
        "",
        "Astronomical positions are ephemeris calculations. Zodiac-based personality meanings are a separate traditional interpretation layer.",
        "",
        "## 6. Human Design or related derived systems",
        "",
        *hd_lines,
        "",
        "## 7. User-supplied psychology",
        "",
        *[f"- {item}" for item in psychology_lines],
        "",
        "Status labels preserve what the user reported. They are not an independently verified capability claim and do not constitute clinical assessment.",
        "",
        "## 8. Cross-system synthesis",
        "",
        "The public synthesis compares eight reduced-digit feature categories and six continuous features under fixed rules. Some name-number outputs are mathematically related, so repeated values must not be counted as independent confirmation.",
        f"The configured roots returned by four mapping families are: `{', '.join(_md(value) for value in roots if value is not None) or 'unavailable'}`.",
        "",
        "This is a synthesis, not an empirical assessment.",
        "",
        "## 9. Agreements, tensions, and contradictions",
        "",
        f"- Highest returned reference-row agreement: `{_md(closest.get('text', 'unavailable'))}` at `{closest.get('agreement', '—')}`.",
        "- That value describes configured feature proximity, not personal similarity or relationship compatibility.",
        "- If symbolic wording conflicts with lived behavior or validated assessment, the direct evidence should take precedence.",
        "",
        "## 10. Provenance, limitations, and reproduction details",
        "",
        f"- Evidence model: `{EVIDENCE_MODEL}`.",
        f"- Signature contract: `{_md(sig.get('contract_version', 'signature-v2'))}`.",
        f"- Extension records with per-system convention and source metadata: `{len(extensions)}` (available in the structured API response).",
        "- Repeating the same normalized inputs, engine version, convention set, and as-of year produces the same deterministic calculation output.",
        "- Reproducibility establishes stable computation, not scientific validity of symbolic interpretation.",
    ]
    markdown = "\n".join(str(line) for line in lines) + "\n"
    return {
        "markdown": markdown,
        "word_count": len(markdown.split()),
        "sections": list(range(1, 11)),
        "section_metadata": _common_metadata(),
        "evidence_model": EVIDENCE_MODEL,
        "mode": "magic",
    }


def generate_report(
    sig: dict,
    psychology: dict | None = None,
    comparisons: list[dict] | None = None,
    *,
    mode: str = "magic",
) -> dict:
    """Generate the public Data or Magic report contract."""
    if mode == "data":
        return _data_report(sig, psychology=psychology, comparisons=comparisons)
    if mode != "magic":
        raise ValueError("report mode must be either 'data' or 'magic'.")
    return _magic_report(sig, psychology=psychology, comparisons=comparisons)


__all__ = ["EVIDENCE_MODEL", "generate_report"]
