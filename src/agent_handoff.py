"""Agent-ready Markdown handoff for Human Manual exports."""
from __future__ import annotations

AGENT_HANDOFF_VERSION = "human-manual-agent-handoff-v1"


def agent_handoff_markdown(*, analysis_mode: str, synthesis_available: bool) -> str:
    narrative_note = (
        "The deterministic Living Pattern is included above and may be rewritten stylistically, but its evidence links and limitations remain authoritative."
        if synthesis_available
        else "Narrative synthesis was disabled for this Data-mode export; work only from the structured material present above."
    )
    return "\n".join([
        "## Agent Handoff — tell this story in another voice",
        "",
        f"- Handoff contract: `{AGENT_HANDOFF_VERSION}`",
        f"- Analysis mode: `{analysis_mode}`",
        "",
        "This Markdown file is intentionally formatted for a favorite agent, local model, or other assistant to digest without needing access to this application.",
        narrative_note,
        "",
        "### Instructions for the receiving agent",
        "",
        "1. Treat the material above as the supplied record. Do not silently replace calculations, source values, or provenance with your own assumptions.",
        "2. Keep calculated, historical, user-supplied, traditional, and project-authored material visibly distinct.",
        "3. Do not invent missing personal facts, birth details, observations, diagnoses, motives, memories, relationships, or biographical events.",
        "4. Preserve contradictions instead of forcing every system into agreement. Different maps are allowed to disagree.",
        "5. You may make the prose vivid, funny, intimate, lyrical, technical, or story-like, but clearly mark any new interpretation as your own narration.",
        "6. Do not turn symbolic material into prediction, diagnosis, certainty, spiritual rank, or a claim that a system has scientifically measured the person.",
        "7. Prefer specific examples already present in the file. When no example exists, ask the human for one rather than manufacturing it.",
        "8. Keep provenance and limitations available even when simplifying the explanation for a nontechnical reader.",
    ]) + "\n"
