"""Public-report hardening layer.

The legacy report remains available for compatibility. This wrapper corrects
claims that overstate independence or empirical meaning without altering the
underlying symbolic calculations. Invalidated Human Design output is removed
from both the data surface and the generated narrative.
"""

from __future__ import annotations

import re
from report import generate_report as generate_legacy_report


EVIDENCE_NOTICE = """> **How to read this report**
> Name arithmetic and linguistic counts are computed. Psychology is self-reported. Numerology, astrology, and cross-tradition correspondences are symbolic reflection systems rather than validated personality measurements. The resonance value is an interpretive engine index, not a percentage of accuracy. Human Design is withheld whenever its calculator has not passed validation.

"""


def _harden_language(markdown: str) -> str:
    text = markdown
    text = text.replace(
        "This is a high reading: several independent systems arrive at compatible readings.",
        "This is a higher value within this engine's interpretive index: several configured outputs coincide.",
    )
    text = text.replace(
        "the independent symbolic systems converge on this name far more often than chance would suggest",
        "the configured symbolic outputs coincide more strongly within this engine",
    )
    text = text.replace(
        "several independent systems arrive at compatible readings",
        "several configured symbolic outputs coincide",
    )
    text = text.replace(
        "five independent digit systems",
        "five configured digit outputs",
    )
    text = text.replace(
        "The reduced total",
        "The mathematically related reduced total",
    )
    text = text.replace(
        "gives a third, independent digit-vote that feeds the convergence analysis below.",
        "is retained as a consistency check, but is excluded as an independent convergence vote because it is mathematically coupled to the Pythagorean root.",
    )
    text = text.replace(
        "The deepest question this engine can ask is: *where do the independently specified core systems agree?*",
        "A useful question for this engine is: *where do separately configured mapping families agree, after dependent outputs are removed?*",
    )
    text = re.sub(
        r"(\d+) of (\d+) independent systems reduce this name",
        r"\1 of \2 configured outputs reduce this name",
        text,
    )
    text = re.sub(
        r"(\d+) of (\d+) digit-producing systems converge",
        r"\1 of \2 configured digit outputs coincide",
        text,
    )
    text = text.replace(
        "despite using unrelated letter-value tables.",
        "under their configured mappings; mathematically dependent mappings must not be counted as separate confirmation.",
    )
    text = text.replace(
        "quantifies exactly this: convergence weighted at 35%",
        "summarizes a related four-family interpretive index: convergence weighted at 35%",
    )
    text = text.replace(
        "The convergent themes of this analysis point to reliable capacities — the qualities multiple systems agree on are the ones to build strategy around rather than treat as accidents.",
        "Repeated symbolic themes can be useful reflection prompts, but they are not evidence of reliable capacities until confirmed by behavior, history, or validated assessment.",
    )
    text = text.replace(
        "**How others likely perceive this identity.**",
        "**One possible first impression of the name.**",
    )
    text = text.replace(
        "against a theoretical maximum of",
        "against the 26-letter alphabet ceiling of",
    )
    text = text.replace(
        "for its length — an entropy ratio",
        "— an alphabet-normalized entropy ratio",
    )
    text = text.replace(
        "a chain of 3 steps means the name holds three orders of magnitude of numeric structure before yielding its essence — a deep name in the Pythagorean-mystical sense",
        "a three-step reduction chain is recorded; any claim that this implies greater personal depth is symbolic interpretation rather than measurement",
    )
    text = text.replace(
        "Everything below is deterministic: run the engine again on the same inputs and you will get the same result, character for character.",
        "Everything below is deterministic for the same normalized inputs and convention versions. Reproducibility does not establish empirical validity.",
    )

    # Human Design failed validation and must not survive in legacy report copy.
    text = text.replace(
        "numerological, linguistic, Hebrew, Greek, astrological, and Human Design encoders",
        "numerological, linguistic, Hebrew, Greek, and astrological encoders",
    )
    text = text.replace(
        "Astrology uses the Swiss Ephemeris for tropical positions, houses, aspects, and lunar phase. Human Design combines birth and 88-days-prior ephemeris positions into gates, channels, type, and profile. The psychology layer",
        "Astrology uses the Swiss Ephemeris for tropical positions, houses, aspects, and lunar phase. Human Design output is withheld because the legacy calculator failed validation. The psychology layer",
    )
    text = text.replace(
        "The symbolic systems (numerology, gematria, astrology, Human Design) are interpretive traditions",
        "The available symbolic systems (numerology, gematria, and astrology) are interpretive traditions",
    )
    text = text.replace(
        "the Human Design implementation is a simplified model of the full bodygraph; ",
        "Human Design is withheld because the legacy implementation failed validation; ",
    )
    return text


def _human_design_status(sig: dict) -> str:
    human_design = sig.get("encoders", {}).get("human_design")
    if not isinstance(human_design, dict):
        return ""
    if human_design.get("status") != "disabled_failed_validation":
        return ""

    reason = human_design.get(
        "reason",
        "The legacy Human Design calculator failed validation.",
    )
    reported = human_design.get("user_reported_type")
    reported_text = (
        f" User-reported type: **{reported}** (self-report only; not calculator-verified)."
        if reported
        else ""
    )
    return (
        "> **Human Design status:** unavailable — "
        f"{reason}{reported_text}\n\n"
    )


def generate_report(sig: dict, psychology: dict | None = None, comparisons: list[dict] | None = None) -> dict:
    report = generate_legacy_report(sig, psychology=psychology, comparisons=comparisons)
    markdown = _harden_language(report["markdown"])
    first_break = markdown.find("\n\n")
    status = _human_design_status(sig)
    insert = EVIDENCE_NOTICE + status
    if first_break >= 0:
        markdown = markdown[: first_break + 2] + insert + markdown[first_break + 2 :]
    else:
        markdown = insert + markdown
    result = dict(report)
    result["markdown"] = markdown
    result["word_count"] = len(markdown.split())
    result["evidence_model"] = "computed-self_report-symbolic-experimental-v2"
    return result


__all__ = ["generate_report"]
