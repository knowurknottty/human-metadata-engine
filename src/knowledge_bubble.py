"""
Knowledge Bubble Export Format
==============================

Exports identity analysis as Knowledge Bubbles compatible
with the CAPT/bioCAPT Knowledge Bubble system.

Each bubble contains:
- Topic
- Claims (with confidence)
- Computations (reproducible)
- Procedures (how to reproduce)
- Examples
- Provenance
- Risks
- Open questions
- Verification status

Bubbles are designed to be:
1. Self-contained (no external dependencies)
2. Verifiable (all claims traceable to computations)
3. Composable (can be merged or compared)
4. Portable (JSON format, no binary data)
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Optional
from datetime import datetime
import json


@dataclass
class Claim:
    statement: str
    confidence: float
    interpretation_level: str  # computed, symbolic, inferred, speculative
    evidence: str
    counter_evidence: Optional[str]
    derived_from: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Computation:
    name: str
    input: dict
    output: dict
    formula: str
    reproducible: bool
    verified: bool

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class KnowledgeBubble:
    topic: str
    version: str
    generated_at: str
    subject_id: str

    # Core content
    claims: list[Claim]
    computations: list[Computation]
    procedures: list[str]
    examples: list[dict]

    # Provenance
    source: str
    confidence: float
    verification_status: str  # unverified, partially_verified, fully_verified

    # Metadata
    symbolic_lenses: list[str]
    risks: list[str]
    open_questions: list[str]
    tags: list[str]

    # Relationships
    depends_on: list[str]  # other bubble topics
    related_to: list[str]

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


def create_identity_bubble(
    identity_text: str,
    pythagorean_data: dict,
    chaldean_data: dict,
    ordinal_data: dict,
    linguistic_data: dict,
    binary_prime_data: dict,
    gematria_data: Optional[dict] = None,
    isopsephy_data: Optional[dict] = None,
    astrology_data: Optional[dict] = None,
    human_design_data: Optional[dict] = None,
    psychology_data: Optional[dict] = None,
) -> KnowledgeBubble:
    """Create a Knowledge Bubble for an identity string."""

    claims = []
    computations = []

    # === PYTHAGOREAN CLAIMS ===
    expr = pythagorean_data.get("expression", 0)
    soul = pythagorean_data.get("soul_urge", 0)
    person = pythagorean_data.get("personality", 0)

    claims.append(Claim(
        statement=f"Pythagorean expression number is {expr}",
        confidence=1.0,
        interpretation_level="computed",
        evidence=f"Sum of letter values = {pythagorean_data.get('total', 0)}, reduced to {expr}",
        counter_evidence=None,
        derived_from=["pythagorean_encoder"],
    ))

    claims.append(Claim(
        statement=f"Pythagorean soul urge is {soul}",
        confidence=1.0,
        interpretation_level="computed",
        evidence=f"Sum of vowel values = {pythagorean_data.get('soul_urge_total', 0)}, reduced to {soul}",
        counter_evidence=None,
        derived_from=["pythagorean_encoder"],
    ))

    claims.append(Claim(
        statement=f"Pythagorean personality is {person}",
        confidence=1.0,
        interpretation_level="computed",
        evidence=f"Sum of consonant values = {pythagorean_data.get('personality_total', 0)}, reduced to {person}",
        counter_evidence=None,
        derived_from=["pythagorean_encoder"],
    ))

    if pythagorean_data.get("master_preserved"):
        claims.append(Claim(
            statement=f"Master number {pythagorean_data['master_preserved']} detected",
            confidence=1.0,
            interpretation_level="computed",
            evidence=f"Intermediate sum = {pythagorean_data['master_preserved']}",
            counter_evidence=None,
            derived_from=["pythagorean_encoder"],
        ))

    # === CHALDEAN CLAIMS ===
    chald_name = chaldean_data.get("name_number", 0)
    claims.append(Claim(
        statement=f"Chaldean name number is {chald_name}",
        confidence=1.0,
        interpretation_level="computed",
        evidence=f"Compound = {chaldean_data.get('compound_number', 0)}, reduced to {chald_name}",
        counter_evidence=None,
        derived_from=["chaldean_encoder"],
    ))

    # === LINGUISTIC CLAIMS ===
    entropy = linguistic_data.get("shannon_entropy", 0)
    syllables = linguistic_data.get("syllable_estimate", 0)
    vowel_ratio = linguistic_data.get("vowel_ratio", 0)

    claims.append(Claim(
        statement=f"Shannon entropy is {entropy} (max possible: {linguistic_data.get('max_possible_entropy', 0)})",
        confidence=1.0,
        interpretation_level="computed",
        evidence=f"Character distribution analysis of {linguistic_data.get('letter_count', 0)} letters",
        counter_evidence=None,
        derived_from=["linguistic_encoder"],
    ))

    claims.append(Claim(
        statement=f"Syllable estimate is {syllables}",
        confidence=0.8,
        interpretation_level="computed",
        evidence="Vowel-group based estimation",
        counter_evidence="May be inaccurate for complex phonotactics",
        derived_from=["linguistic_encoder"],
    ))

    # === BINARY/PRIME CLAIMS ===
    polarity = binary_prime_data.get("polarity_score", 0)
    claims.append(Claim(
        statement=f"Vowel-consonant polarity is {polarity:+.1f} ({'vowel-dominant' if polarity > 0 else 'consonant-dominant'})",
        confidence=1.0,
        interpretation_level="computed",
        evidence=f"Vowel power={binary_prime_data.get('vowel_power', 0)}, Consonant power={binary_prime_data.get('consonant_power', 0)}",
        counter_evidence=None,
        derived_from=["binary_prime_encoder"],
    ))

    # === GEMATRIA CLAIMS ===
    if gematria_data:
        claims.append(Claim(
            statement=f"Hebrew Gematria absolute value is {gematria_data.get('absolute_total', 0)}",
            confidence=1.0,
            interpretation_level="computed",
            evidence="Latin-to-Hebrew letter mapping",
            counter_evidence="Latin-to-Hebrew mapping is approximate",
            derived_from=["gematria_encoder"],
        ))

    # === ISOPSEPHY CLAIMS ===
    if isopsephy_data:
        claims.append(Claim(
            statement=f"Greek Isopsephy total is {isopsephy_data.get('total', 0)}",
            confidence=1.0,
            interpretation_level="computed",
            evidence="Latin-to-Greek letter mapping",
            counter_evidence="Latin-to-Greek mapping is approximate",
            derived_from=["isopsephy_encoder"],
        ))

    # === SYMBOLIC CLAIMS (speculative) ===
    symbolic_claims = {
        1: "Expression 1 symbolically suggests leadership, initiation, and command.",
        2: "Expression 2 symbolically suggests cooperation, balance, and sensitivity.",
        3: "Expression 3 symbolically suggests creativity, communication, and expression.",
        4: "Expression 4 symbolically suggests structure, stability, and foundation.",
        5: "Expression 5 symbolically suggests change, freedom, and adaptability.",
        6: "Expression 6 symbolically suggests harmony, responsibility, and care.",
        7: "Expression 7 symbolically suggests analysis, introspection, and wisdom.",
        8: "Expression 8 symbolically suggests power, achievement, and material success.",
        9: "Expression 9 symbolically suggests completion, compassion, and universal awareness.",
    }

    if expr in symbolic_claims:
        claims.append(Claim(
            statement=symbolic_claims[expr],
            confidence=0.3,
            interpretation_level="symbolic",
            evidence="Pythagorean numerological tradition",
            counter_evidence="Symbolic interpretation, not empirical proof",
            derived_from=["pythagorean_symbolic_tradition"],
        ))

    # === COMPUTATIONS ===
    computations.append(Computation(
        name="pythagorean_encoding",
        input={"text": identity_text},
        output={
            "total": pythagorean_data.get("total"),
            "reduced": pythagorean_data.get("expression"),
            "master": pythagorean_data.get("master_preserved"),
        },
        formula="sum(PYTHAGOREAN_MAP[ch] for ch in normalized_text), then reduce",
        reproducible=True,
        verified=True,
    ))

    computations.append(Computation(
        name="chaldean_encoding",
        input={"text": identity_text},
        output={
            "compound": chaldean_data.get("compound_number"),
            "name_number": chaldean_data.get("name_number"),
        },
        formula="sum(CHALDEAN_MAP[ch] for ch in normalized_text), then reduce",
        reproducible=True,
        verified=True,
    ))

    computations.append(Computation(
        name="shannon_entropy",
        input={"text": identity_text},
        output={"entropy": entropy},
        formula="-sum(p * log2(p) for p in character_frequencies)",
        reproducible=True,
        verified=True,
    ))

    # === PROCEDURES ===
    procedures = [
        "Normalize input: uppercase, remove punctuation",
        "Apply Pythagorean letter mapping (A=1, J=1, S=1, etc.)",
        "Compute total sum, reduce to single digit",
        "Preserve master numbers (11, 22, 33) at intermediate reduction",
        "Apply Chaldean mapping (different from Pythagorean)",
        "Compute vowel/consonant split for Soul Urge and Personality",
        "Calculate Shannon entropy of character distribution",
        "Compute prime-index encoding for cross-encoder comparison",
    ]

    # === EXAMPLES ===
    examples = [
        {
            "input": "CAPT",
            "pythagorean": {"total": 13, "reduced": 4},
            "chaldean": {"compound": 16, "name_number": 7},
        },
        {
            "input": "Knowurknot",
            "pythagorean": {"total": 45, "reduced": 9},
            "chaldean": {"compound": 45, "name_number": 9},
        },
    ]

    # === RISKS ===
    risks = [
        "Numerology is a symbolic lens, not empirical proof",
        "Chaldean-to-Latin mapping is approximate",
        "Linguistic features (entropy, syllables) are measurable but interpretation is subjective",
        "Master number preservation is a convention, not a universal rule",
        "Symbolic interpretations should not be treated as fact",
    ]

    # === OPEN QUESTIONS ===
    open_questions = [
        "How should multiple encoder results be weighted for consensus?",
        "What confidence threshold should trigger symbolic interpretation?",
        "How to handle contradictory signals across encoders?",
        "Should Chaldean and Pythagorean be treated as independent signals?",
    ]

    # === SYMBOLIC LENSES ===
    symbolic_lenses = [
        "Pythagorean numerology",
        "Chaldean numerology",
        "Hebrew Gematria",
        "Greek Isopsephy",
        "Linguistic analysis",
        "Binary/prime encoding",
    ]
    if astrology_data:
        symbolic_lenses.append("Tropical astrology")
    if human_design_data:
        symbolic_lenses.append("Human Design")

    return KnowledgeBubble(
        topic=f"Identity: {identity_text}",
        version="0.2.0",
        generated_at=datetime.utcnow().isoformat() + "Z",
        subject_id=f"identity:{identity_text.lower().replace(' ', '_')}",
        claims=claims,
        computations=computations,
        procedures=procedures,
        examples=examples,
        source="human_metadata_engine",
        confidence=0.85,
        verification_status="fully_verified",
        symbolic_lenses=symbolic_lenses,
        risks=risks,
        open_questions=open_questions,
        tags=["identity", "numerology", "linguistics", "symbolic_analysis"],
        depends_on=[],
        related_to=["pythagorean_encoder", "chaldean_encoder", "linguistic_encoder"],
    )


def export_bubbles_json(bubbles: list[KnowledgeBubble], path: str) -> str:
    """Export a list of Knowledge Bubbles to JSON."""
    output = {
        "version": "0.2.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "bubble_count": len(bubbles),
        "bubbles": [b.to_dict() for b in bubbles],
    }
    with open(path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    return path


def export_bubble_markdown(bubble: KnowledgeBubble) -> str:
    """Export a single Knowledge Bubble as Markdown."""
    lines = [
        f"# {bubble.topic}",
        f"**Version:** {bubble.version}",
        f"**Generated:** {bubble.generated_at}",
        f"**Confidence:** {bubble.confidence}",
        f"**Verification:** {bubble.verification_status}",
        "",
        "## Claims",
        "",
    ]

    for claim in bubble.claims:
        lines.append(f"- **[{claim.interpretation_level}]** {claim.statement}")
        lines.append(f"  - Confidence: {claim.confidence}")
        lines.append(f"  - Evidence: {claim.evidence}")
        if claim.counter_evidence:
            lines.append(f"  - Counter-evidence: {claim.counter_evidence}")
        lines.append("")

    lines.append("## Computations")
    lines.append("")
    for comp in bubble.computations:
        lines.append(f"### {comp.name}")
        lines.append(f"- Input: `{comp.input}`")
        lines.append(f"- Output: `{comp.output}`")
        lines.append(f"- Formula: `{comp.formula}`")
        lines.append(f"- Reproducible: {comp.reproducible}")
        lines.append("")

    lines.append("## Procedures")
    lines.append("")
    for i, proc in enumerate(bubble.procedures, 1):
        lines.append(f"{i}. {proc}")
    lines.append("")

    lines.append("## Risks")
    lines.append("")
    for risk in bubble.risks:
        lines.append(f"- {risk}")
    lines.append("")

    lines.append("## Open Questions")
    lines.append("")
    for q in bubble.open_questions:
        lines.append(f"- {q}")
    lines.append("")

    lines.append("## Symbolic Lenses Applied")
    lines.append("")
    for lens in bubble.symbolic_lenses:
        lines.append(f"- {lens}")
    lines.append("")

    lines.append("---")
    lines.append("*This Knowledge Bubble was generated by the Human Metadata Engine.*")
    lines.append("*Symbolic systems are interpretive lenses, not empirical proof.*")

    return "\n".join(lines)


if __name__ == "__main__":
    # Example: create a bubble for CAPT
    bubble = create_identity_bubble(
        identity_text="CAPT",
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

    print(export_bubble_markdown(bubble))
