"""Version and safety contracts for narrative synthesis."""

EVIDENCE_SCHEMA_VERSION = "synthesis-evidence-v1"
PLAN_SCHEMA_VERSION = "synthesis-plan-v1"
NARRATIVE_SCHEMA_VERSION = "narrative-v1"
ONTOLOGY_VERSION = "motif-ontology-v1"
MAPPING_VERSION = "project-authored-symbolic-normalization-v1"
TEMPLATE_VERSION = "narrative-templates-v2"

EPISTEMIC_TIERS = {
    "deterministic_calculation": 1,
    "deterministic_relationship": 2,
    "traditional_symbolic_interpretation": 3,
    "user_supplied": 4,
    "interpretive_synthesis": 5,
}

PROHIBITED_TOPICS = [
    "medical diagnosis", "psychiatric diagnosis", "trauma diagnosis", "abuse history",
    "addiction", "criminality", "violence", "sexuality", "gender identity", "fertility",
    "pregnancy", "death", "lifespan", "legal outcomes", "financial destiny",
    "political ideology", "religious truth", "spiritual rank", "supernatural powers",
    "psychic certainty", "guaranteed compatibility", "guaranteed career success",
    "guaranteed relationship outcomes", "exact future events",
]

PROHIBITED_LANGUAGE = [
    "you are destined", "you were born to", "this proves", "you always", "you cannot",
    "will definitely", "guaranteed", "diagnosis", "disorder", "mental illness",
    "psychic powers", "supernatural power", "exactly what will happen",
]

SYMBOLIC_LIMITATION = (
    "Traditional symbolic interpretation, not scientific personality measurement or prediction."
)
SYNTHESIS_LIMITATION = (
    "Project-authored interpretive synthesis; use as a reflection prompt, not a fact about the person."
)
