from pathlib import Path

from narrative_helpers import exact_payload
from server import analyze

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "webapp/static/app.js").read_text(encoding="utf-8")
ATLAS = (ROOT / "webapp/static/atlas.js").read_text(encoding="utf-8")
SERVER = (ROOT / "webapp/server.py").read_text(encoding="utf-8")


def test_storytelling_lexicon_is_substantial_and_versioned():
    from synthesis.prose_lexicon import LEXICON_BANKS, LEXICON_VERSION
    assert LEXICON_VERSION.startswith("deterministic-prose-lexicon-")
    assert sum(len(items) for items in LEXICON_BANKS.values()) >= 80
    assert all(len(items) >= 10 for items in LEXICON_BANKS.values())


def test_compositor_is_deterministic_but_seed_sensitive():
    from synthesis.prose_lexicon import enrich_synthesis_sentence
    base = "The evidence remains bounded."
    a1 = enrich_synthesis_sentence(base, seed="alpha", mode="mythic", claim_type="integrative", contradiction=False)
    a2 = enrich_synthesis_sentence(base, seed="alpha", mode="mythic", claim_type="integrative", contradiction=False)
    b = enrich_synthesis_sentence(base, seed="beta", mode="mythic", claim_type="integrative", contradiction=False)
    assert a1 == a2
    assert a1 != b


def test_magic_analysis_uses_local_deterministic_compositor_only():
    result = analyze(exact_payload())
    story = result["synthesis"]["narratives"]["mythic"]
    meta = story["generation_metadata"]
    assert meta["engine"] == "deterministic-compositor"
    assert meta["remote_provider_used"] is False
    assert result["synthesis"]["ai_realization"] == {
        "enabled": False, "required": False, "remote_provider_used": False
    }
    assert result["synthesis"]["versions"]["lexicon"].startswith("deterministic-prose-lexicon-")


def test_public_story_mode_has_no_remote_model_path():
    public = "\n".join((APP, ATLAS, SERVER)).casefold()
    assert "/api/narrative/mythic" not in public
    assert "loadremotemythic" not in public
    assert "openrouter" not in APP.casefold()
    assert "qwen3.8" not in APP.casefold()
    assert "story" in ATLAS.casefold()
    assert "deterministic" in ATLAS.casefold()


def test_downloadable_markdown_contains_agent_handoff_contract():
    markdown = analyze(exact_payload())["report"]["markdown"]
    assert "## Agent Handoff" in markdown
    assert "Do not invent missing personal facts" in markdown
    assert "preserve contradictions" in markdown.casefold()
    assert "calculated, historical, user-supplied, traditional, and project-authored" in markdown
    assert "favorite agent" in markdown.casefold()


def test_story_is_richer_than_grounded_without_changing_evidence_links():
    synthesis = analyze(exact_payload())["synthesis"]
    plain = synthesis["narratives"]["plain"]
    story = synthesis["narratives"]["mythic"]
    plain_sentences = [s for sec in plain["sections"] for p in sec["paragraphs"] for s in p["sentences"]]
    story_sentences = [s for sec in story["sections"] for p in sec["paragraphs"] for s in p["sentences"]]
    assert [s["evidence_ids"] for s in plain_sentences] == [s["evidence_ids"] for s in story_sentences]
    assert sum(len(s["text"]) for s in story_sentences) > sum(len(s["text"]) for s in plain_sentences)


def test_replay_identity_is_stable_but_mode_sensitive():
    first = analyze(exact_payload())["synthesis"]
    second = analyze(exact_payload())["synthesis"]
    assert first["plan"]["calculation_replay_id"] == second["plan"]["calculation_replay_id"]
    for mode in ("plain", "mythic", "research"):
        assert first["narratives"][mode]["generation_metadata"]["presentation_replay_id"] == second["narratives"][mode]["generation_metadata"]["presentation_replay_id"]
    identities = {
        first["narratives"][mode]["generation_metadata"]["presentation_replay_id"]
        for mode in ("plain", "mythic", "research")
    }
    assert len(identities) == 3


def test_replay_rejects_evidence_semantics_changed_under_stale_identity():
    from copy import deepcopy
    from synthesis.analysis import detect_agreements, detect_contradictions, rank_motifs
    from synthesis.plan import build_plan

    synthesis = analyze(exact_payload())["synthesis"]
    changed = deepcopy(synthesis["evidence"])
    changed["evidence_items"][0]["limitations"] = [
        *changed["evidence_items"][0]["limitations"],
        "test semantic change",
    ]
    changed.pop("packet_digest", None)
    motifs = rank_motifs(changed)
    try:
        build_plan(changed, motifs, detect_agreements(motifs), detect_contradictions(motifs))
    except ValueError as exc:
        assert "Evidence record identity mismatch" in str(exc)
    else:
        raise AssertionError("Semantic evidence mutation under stale identity must be rejected.")
