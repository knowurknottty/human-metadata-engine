"""Integrity contract for the completed local Inversion Tarot art deck."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import tarot_reading
DECK_DIR = ROOT / "webapp/static/assets/tarot"
DEPLOY = json.loads((DECK_DIR / "manifest.json").read_text(encoding="utf-8"))
INTAKE = json.loads((ROOT / "release/tarot-art-intake-2026-09-24.json").read_text(encoding="utf-8"))
ART_JS = (ROOT / "webapp/static/tarot-art.js").read_text(encoding="utf-8")
CSS = (ROOT / "webapp/static/styles.css").read_text(encoding="utf-8")
def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def served_path(item: dict) -> Path: return ROOT / "webapp/static" / item["served_asset"].lstrip("/")
def test_deployment_manifest_covers_exactly_the_runtime_78_card_ids():
    expected = {card["id"] for card in tarot_reading.DECK}
    mapped = {item["runtime_id"] for item in DEPLOY["cards"]}
    assert DEPLOY["version"] == "inversion-tarot-art-v2"
    assert DEPLOY["finished_card_count"] == 78 and DEPLOY["finished_major_count"] == 22
    assert DEPLOY["remaining_major_indices"] == [] and DEPLOY["remaining_minor_count"] == 0
    assert DEPLOY["remaining_total_artworks"] == 0 and mapped == expected
def test_all_served_assets_exist_are_unique_and_match_manifest_hashes():
    seen=set()
    for item in DEPLOY["cards"]:
        path=served_path(item); assert path.is_file() and path.suffix == ".webp"
        digest=sha256(path); assert digest == item["served_sha256"] and digest not in seen
        seen.add(digest); assert item["served_bytes"] == path.stat().st_size
    assert len(seen) == 78

def test_intake_manifest_is_78_of_78_mapped_unique_and_source_bound():
    assert INTAKE["asset_count"] == INTAKE["expected_asset_count"] == 78
    assert INTAKE["asset_set_complete"] is True and INTAKE["mapping_complete"] is True
    assert INTAKE["visual_review_complete"] is True
    assert INTAKE["deployment_asset_manifest"] == "webapp/static/assets/tarot/manifest.json"

def test_recovered_missing_card_is_knight_of_swords_and_bound_by_hash():
    item = next(item for item in INTAKE["assets"] if item["filename"] == "image-gen-9(4).png")
    assert item["slot"] == 62 and item["card_id"] == "swords-12"
    assert item["card_title"] == "Knight of Swords"
    assert item["sha256"] == "510ef44ba1d5d746f6341dd102b2a20b2f40810b78137ec2e4850ca0ab4af935"

def test_frontend_prefers_unified_local_art_and_falls_back_to_svg():
    assert "CARD_ASSETS" in ART_JS and "MAJOR_ASSETS" in ART_JS
    assert "renderFallbackArt" in ART_JS and 'img.addEventListener("error"' in ART_JS
    assert "renderMajor(svg,card)" in ART_JS and "renderPips(svg,card)" in ART_JS and "renderCourt(svg,card)" in ART_JS
    assert ".tarot-card-art-image" in CSS and "object-fit: contain" in CSS
