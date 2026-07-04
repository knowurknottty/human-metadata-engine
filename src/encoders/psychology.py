"""
Psychological Profiling Module
==============================

Stores and manages user-supplied psychological assessments.
These are NOT inferred — they must be explicitly provided by the user.

Supported frameworks:
- Big Five (OCEAN): Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism
- MBTI: 16 personality types
- Enneagram: 9 types with wings and levels
- Attachment Style: Secure, Anxious, Avoidant, Disorganized
- Cognitive Functions: MBTI function stack
- Learning Styles: Visual, Auditory, Kinesthetic, Reading/Writing

All data is treated as user-supplied, not computed.
Confidence depends on source:
- Self-assessment: 0.7
- Professional assessment: 0.9
- Informal/inferred: 0.4
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum


class AssessmentSource(Enum):
    SELF = "self_assessment"
    PROFESSIONAL = "professional_assessment"
    INFORMAL = "informal_inference"
    RESEARCH = "research_based"


@dataclass
class BigFive:
    """Big Five / OCEAN personality model. Scores 0.0-1.0."""
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    source: str
    confidence: float

    def to_dict(self) -> dict:
        return asdict(self)

    def dominant_trait(self) -> str:
        traits = {
            "Openness": self.openness,
            "Conscientiousness": self.conscientiousness,
            "Extraversion": self.extraversion,
            "Agreeableness": self.agreeableness,
            "Neuroticism": self.neuroticism,
        }
        return max(traits, key=traits.get)

    def summary(self) -> str:
        dominant = self.dominant_trait()
        return f"Big Five: {dominant}-dominant (O={self.openness:.2f}, C={self.conscientiousness:.2f}, E={self.extraversion:.2f}, A={self.agreeableness:.2f}, N={self.neuroticism:.2f})"


@dataclass
class MBTI:
    """MBTI personality type."""
    type_code: str  # e.g., "INTJ", "ENFP"
    cognitive_functions: list[str]  # e.g., ["Ni", "Te", "Fi", "Se"]
    source: str
    confidence: float

    def to_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        funcs = " → ".join(self.cognitive_functions) if self.cognitive_functions else "Unknown"
        return f"MBTI: {self.type_code} ({funcs})"

    @staticmethod
    def validate_type(code: str) -> bool:
        valid = True
        if len(code) != 4:
            return False
        if code[0] not in "EI":
            return False
        if code[1] not in "SN":
            return False
        if code[2] not in "TF":
            return False
        if code[3] not in "JP":
            return False
        return True

    @staticmethod
    def get_cognitive_functions(type_code: str) -> list[str]:
        """Get the cognitive function stack for an MBTI type."""
        functions = {
            "INTJ": ["Ni", "Te", "Fi", "Se"],
            "INTP": ["Ti", "Ne", "Si", "Fe"],
            "ENTJ": ["Te", "Ni", "Se", "Fi"],
            "ENTP": ["Ne", "Ti", "Fe", "Si"],
            "INFJ": ["Ni", "Fe", "Ti", "Se"],
            "INFP": ["Fi", "Ne", "Si", "Te"],
            "ENFJ": ["Fe", "Ni", "Se", "Ti"],
            "ENFP": ["Ne", "Fi", "Te", "Si"],
            "ISTJ": ["Si", "Te", "Fi", "Ne"],
            "ISFJ": ["Si", "Fe", "Ti", "Ne"],
            "ESTJ": ["Te", "Si", "Ne", "Fi"],
            "ESFJ": ["Fe", "Si", "Ne", "Ti"],
            "ISTP": ["Ti", "Se", "Ni", "Fe"],
            "ISFP": ["Fi", "Se", "Ni", "Te"],
            "ESTP": ["Se", "Ti", "Fe", "Ni"],
            "ESFP": ["Se", "Fi", "Te", "Ni"],
        }
        return functions.get(type_code, [])


@dataclass
class Enneagram:
    """Enneagram personality type."""
    core_type: int  # 1-9
    wing: Optional[int]  # 2-9 (adjacent to core)
    instinctual_variant: str  # SO, SX, SP
    level_of_development: int  # 1-9 (healthy to unhealthy)
    integration_point: int
    disintegration_point: int
    source: str
    confidence: float

    TYPE_NAMES = {
        1: "The Reformer", 2: "The Helper", 3: "The Achiever",
        4: "The Individualist", 5: "The Investigator", 6: "The Loyalist",
        7: "The Enthusiast", 8: "The Challenger", 9: "The Peacemaker",
    }

    INTEGRATION = {1: 7, 2: 4, 3: 6, 4: 1, 5: 8, 6: 9, 7: 5, 8: 2, 9: 3}
    DISINTEGRATION = {1: 4, 2: 8, 3: 9, 4: 2, 5: 7, 6: 3, 7: 1, 8: 5, 9: 6}

    def to_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        name = self.TYPE_NAMES.get(self.core_type, "Unknown")
        wing_str = f"w{self.wing}" if self.wing else ""
        return f"Enneagram: {self.core_type} {name} {wing_str} ({self.instinctual_variant})"


@dataclass
class AttachmentStyle:
    """Attachment style classification."""
    primary_style: str  # Secure, Anxious, Avoidant, Disorganized
    secondary_style: Optional[str]
    source: str
    confidence: float

    STYLES = ["Secure", "Anxious", "Avoidant", "Disorganized"]

    def to_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        secondary = f"/{self.secondary_style}" if self.secondary_style else ""
        return f"Attachment: {self.primary_style}{secondary}"


@dataclass
class PsychologicalProfile:
    """Complete psychological profile (all user-supplied)."""
    subject_id: str

    big_five: Optional[BigFive]
    mbti: Optional[MBTI]
    enneagram: Optional[Enneagram]
    attachment_style: Optional[AttachmentStyle]

    # Additional user-supplied data
    communication_style: Optional[str]  # direct, diplomatic, analytical, expressive
    risk_tolerance: Optional[str]  # low, medium, high
    ambiguity_tolerance: Optional[str]  # low, medium, high
    learning_style: Optional[str]  # visual, auditory, kinesthetic, reading_writing
    thinking_style: Optional[str]  # analytical, creative, practical, theoretical
    decision_style: Optional[str]  # rational, intuitive, dependent, spontaneous
    conflict_style: Optional[str]  # competing, collaborating, avoiding, accommodating, compromising

    # Metadata
    overall_confidence: float
    last_updated: str
    notes: str

    def to_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        parts = []
        if self.big_five:
            parts.append(self.big_five.summary())
        if self.mbti:
            parts.append(self.mbti.summary())
        if self.enneagram:
            parts.append(self.enneagram.summary())
        if self.attachment_style:
            parts.append(self.attachment_style.summary())
        return " | ".join(parts) if parts else "No psychological data provided"

    def dominant_traits(self) -> list[str]:
        """List all dominant/specified traits."""
        traits = []
        if self.big_five:
            traits.append(f"BigFive-{self.big_five.dominant_trait()}")
        if self.mbti:
            traits.append(f"MBTI-{self.mbti.type_code}")
        if self.enneagram:
            traits.append(f"Ennea-{self.enneagram.core_type}")
        if self.communication_style:
            traits.append(f"Comm-{self.communication_style}")
        if self.risk_tolerance:
            traits.append(f"Risk-{self.risk_tolerance}")
        return traits


def create_profile(
    subject_id: str,
    big_five: Optional[dict] = None,
    mbti_type: Optional[str] = None,
    enneagram_type: Optional[int] = None,
    enneagram_wing: Optional[int] = None,
    attachment: Optional[str] = None,
    **kwargs,
) -> PsychologicalProfile:
    """Factory function to create a psychological profile from user input."""

    b5 = None
    if big_five:
        b5 = BigFive(
            openness=big_five.get("openness", 0.5),
            conscientiousness=big_five.get("conscientiousness", 0.5),
            extraversion=big_five.get("extraversion", 0.5),
            agreeableness=big_five.get("agreeableness", 0.5),
            neuroticism=big_five.get("neuroticism", 0.5),
            source=big_five.get("source", "self_assessment"),
            confidence=big_five.get("confidence", 0.7),
        )

    mbti = None
    if mbti_type and MBTI.validate_type(mbti_type):
        mbti = MBTI(
            type_code=mbti_type,
            cognitive_functions=MBTI.get_cognitive_functions(mbti_type),
            source="self_assessment",
            confidence=0.7,
        )

    enne = None
    if enneagram_type and 1 <= enneagram_type <= 9:
        enne = Enneagram(
            core_type=enneagram_type,
            wing=enneagram_wing,
            instinctual_variant=kwargs.get("instinctual_variant", "SO"),
            level_of_development=kwargs.get("level_of_development", 5),
            integration_point=Enneagram.INTEGRATION.get(enneagram_type, 0),
            disintegration_point=Enneagram.DISINTEGRATION.get(enneagram_type, 0),
            source="self_assessment",
            confidence=0.7,
        )

    attach = None
    if attachment and attachment in AttachmentStyle.STYLES:
        attach = AttachmentStyle(
            primary_style=attachment,
            secondary_style=kwargs.get("secondary_attachment"),
            source="self_assessment",
            confidence=0.7,
        )

    return PsychologicalProfile(
        subject_id=subject_id,
        big_five=b5,
        mbti=mbti,
        enneagram=enne,
        attachment_style=attach,
        communication_style=kwargs.get("communication_style"),
        risk_tolerance=kwargs.get("risk_tolerance"),
        ambiguity_tolerance=kwargs.get("ambiguity_tolerance"),
        learning_style=kwargs.get("learning_style"),
        thinking_style=kwargs.get("thinking_style"),
        decision_style=kwargs.get("decision_style"),
        conflict_style=kwargs.get("conflict_style"),
        overall_confidence=kwargs.get("confidence", 0.7),
        last_updated=kwargs.get("last_updated", ""),
        notes=kwargs.get("notes", ""),
    )


if __name__ == "__main__":
    # Example: create a profile
    profile = create_profile(
        subject_id="john_michael_smith",
        big_five={"openness": 0.9, "conscientiousness": 0.8, "extraversion": 0.6,
                  "agreeableness": 0.7, "neuroticism": 0.3, "confidence": 0.7},
        mbti_type="INTJ",
        enneagram_type=5,
        enneagram_wing=4,
        attachment="Secure",
        communication_style="direct",
        risk_tolerance="high",
        thinking_style="analytical",
        notes="Creator/architect profile. High openness, high conscientiousness.",
    )
    print(profile.summary())
    print(f"Dominant traits: {profile.dominant_traits()}")
