"""Public composition boundary for the deterministic Narrative Synthesis Engine."""

from __future__ import annotations

from .analysis import detect_agreements, detect_contradictions, rank_motifs
from .contracts import MAPPING_VERSION, ONTOLOGY_VERSION, TEMPLATE_VERSION
from .extractors import extract_evidence
from .plan import build_plan
from .realize import realize
from .verify import verify_narrative


def build_synthesis(signature: dict, psychology: dict | None, analysis_id: str) -> dict:
    evidence = extract_evidence(signature, psychology, analysis_id)
    motifs = rank_motifs(evidence)
    agreements = detect_agreements(motifs)
    contradictions = detect_contradictions(motifs)
    plan = build_plan(evidence, motifs, agreements, contradictions)
    narratives = {mode: realize(plan, mode) for mode in ("plain", "mythic", "research")}
    verification = {mode: verify_narrative(evidence, plan, narrative) for mode, narrative in narratives.items()}
    if not all(report["valid"] for report in verification.values()):
        raise ValueError("Deterministic narrative failed its claim verifier.")
    return {
        "evidence": evidence, "plan": plan, "narratives": narratives, "verification": verification,
        "versions": {"ontology": ONTOLOGY_VERSION, "mapping": MAPPING_VERSION, "templates": TEMPLATE_VERSION},
        "ai_realization": {"enabled": False, "required": False, "remote_provider_used": False},
    }


def narrative_markdown(synthesis: dict, mode: str = "plain") -> str:
    narrative = synthesis["narratives"][mode]
    evidence = {item["evidence_id"]: item for item in synthesis["evidence"]["evidence_items"]}
    lines = ["## Human Metadata Narrative — The Living Pattern", "", f"- Mode: `{mode}`", f"- Schema: `{narrative['schema_version']}`", f"- Evidence schema: `{synthesis['evidence']['schema_version']}`", "", f"> {narrative['disclaimer']}", ""]
    for section in narrative["sections"]:
        lines.extend([f"### {section['heading']}", ""])
        for paragraph in section["paragraphs"]:
            for sentence in paragraph["sentences"]:
                refs = ", ".join(f"`{item}`" for item in sentence["evidence_ids"])
                lines.extend([sentence["text"], "", f"Evidence: {refs} · confidence: `{sentence['strength']}`", ""])
    lines.extend(["### Evidence ledger", ""])
    used = sorted({eid for section in narrative["sections"] for paragraph in section["paragraphs"] for sentence in paragraph["sentences"] for eid in sentence["evidence_ids"]})
    for evidence_id in used:
        item = evidence[evidence_id]
        lines.append(f"- `{evidence_id}` — {item['system']} · `{item['source_path']}` = `{item['source_value']}`; {item['limitations'][0] if item['limitations'] else 'No interpretive claim attached.'}")
    quality = synthesis["evidence"]["data_quality"]
    lines.extend(["", "### Missing-data limits", "", *[f"- {key.replace('_', ' ')}: `{value}`" for key, value in quality.items()], ""])
    return "\n".join(lines)
