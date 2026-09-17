from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "webapp" / "static"
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
APP = (STATIC / "app.js").read_text(encoding="utf-8")
ATLAS = (STATIC / "atlas.js").read_text(encoding="utf-8")


def test_public_identity_is_human_manual_by_inversion_labs():
    assert "The Human Manual, for and by Humans" in HTML
    assert "Inversion Labs" in HTML
    assert "/assets/inversion-labs-infinite-key.jpg" in HTML
    assert "Human Metadata" not in HTML
    assert "Human Metadata Narrative" not in ATLAS
    assert "Human Metadata Atlas" not in ATLAS
    assert "Human Metadata reflection surface" not in APP


def test_first_run_explains_network_boundary_before_name_input():
    disclosure = HTML.index('id="privacy-before-input"')
    name_input = HTML.index('id="name"')
    assert disclosure < name_input
    for phrase in (
        "sent to this site's server for the calculations you request",
        "Birthplace text may be sent to the configured location provider",
        "Optional means optional",
        "No hidden enrichment",
    ):
        assert phrase in HTML


def test_public_brand_assets_exist():
    assert (STATIC / "assets" / "inversion-labs-infinite-key.jpg").is_file()
    assert (STATIC / "assets" / "inversion-labs-more-human-possible.jpg").is_file()

def test_public_copy_names_human_lineage_and_agent_handoff():
    assert "Designed by humans across centuries. Computed, compared, and converged by Inversion Labs." in HTML
    lowered = APP.casefold()
    assert "cool fucking story" in lowered
    assert "favorite agent" in lowered
    assert "welcome to the inversion" in lowered
    assert "reportactions(true)" in lowered
