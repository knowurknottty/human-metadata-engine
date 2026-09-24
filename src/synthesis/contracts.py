"""Version and safety contracts for narrative synthesis."""

EVIDENCE_SCHEMA_VERSION = "synthesis-evidence-v2"
PLAN_SCHEMA_VERSION = "synthesis-plan-v2"
NARRATIVE_SCHEMA_VERSION = "narrative-v2"

EVIDENCE_ID_SCHEME_VERSION = "evidence-id-v2"
CLAIM_ID_SCHEME_VERSION = "claim-id-v3"
ONTOLOGY_VERSION = "motif-ontology-v1"
MAPPING_VERSION = "project-authored-symbolic-normalization-v1"
MAPPING_POLICY_VERSION = MAPPING_VERSION
MOTIF_RANKING_POLICY_VERSION = "motif-ranking-v2"
REALIZATION_POLICY_VERSION = "deterministic-realization-v2"
SYNTHESIS_REPLAY_SCHEMA_VERSION = "synthesis-replay-v2"
TEMPLATE_VERSION = "narrative-templates-v3"

POLICY_VERSIONS = {
    "evidence_id": EVIDENCE_ID_SCHEME_VERSION,
    "claim_id": CLAIM_ID_SCHEME_VERSION,
    "ontology": ONTOLOGY_VERSION,
    "mapping": MAPPING_POLICY_VERSION,
    "motif_ranking": MOTIF_RANKING_POLICY_VERSION,
    "realization": REALIZATION_POLICY_VERSION,
    "replay": SYNTHESIS_REPLAY_SCHEMA_VERSION,
    "templates": TEMPLATE_VERSION,
}

EPISTEMIC_TIERS = {
    "deterministic_calculation": 1,
    "deterministic_relationship": 2,
    "traditional_symbolic_interpretation": 3,
    "historical_textual_reference": 3,
    "user_supplied": 4,
    "project_authored_crosswalk": 5,
    "interpretive_synthesis": 5,
    "system_state": 0,
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
