"""Release manifest and legacy-output quarantine integrity tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tools.verify_release_manifest import verify_manifest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release" / "manifest.dev.json"
LEGACY_INDEX = ROOT / "release" / "legacy-output-index.json"


@pytest.fixture(scope="module", autouse=True)
def _fresh_development_manifest():
    subprocess.check_call([
        sys.executable, str(ROOT / "tools" / "build_development_manifest.py"),
        "--verification-status", "in_progress",
        "--verification-command", "pytest-release-manifest-contract",
        "--required-skips", "0",
        "--browser-manifest", "release/qa/atlas-browser-manifest.json",
        "--physical-device-qa", "pending",
    ], cwd=ROOT)
    yield


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_development_manifest_is_valid_but_cannot_claim_release_candidate():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert verify_manifest(MANIFEST) == []
    assert isinstance(manifest["source_dirty"], bool)
    assert manifest["release_candidate"] is False
    assert manifest["verification"]["status"] in {"in_progress", "passed"}
    if manifest["verification"]["status"] == "passed":
        assert manifest["verification"]["commands"]
    assert manifest["worktree"]["schema_version"] == "human-manual-worktree-identity-v1"
    assert len(manifest["worktree"]["digest"]) == 64
    assert manifest["epistemic"]["empirical_validation"] == "not_established"
    assert manifest["runtime"] == {"default": "offline", "remote_ai": False}


def test_release_manifest_artifacts_are_content_bound():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for artifact in manifest["artifacts"]:
        path = ROOT / artifact["path"]
        assert path.is_file()
        assert path.stat().st_size == artifact["bytes"]
        assert _sha(path) == artifact["sha256"]


def test_legacy_output_index_is_byte_bound_and_never_active_evidence():
    index = json.loads(LEGACY_INDEX.read_text(encoding="utf-8"))
    assert index["active_evidence_version"] == "synthesis-evidence-v2"
    assert index["artifacts"]
    for artifact in index["artifacts"]:
        path = ROOT / artifact["path"]
        assert path.is_file()
        assert path.stat().st_size == artifact["bytes"]
        assert _sha(path) == artifact["sha256"]
        assert artifact["active_evidence"] is False
        assert artifact["public_status"] == "quarantined_historical"


def test_dirty_manifest_cannot_be_promoted_to_candidate(tmp_path):
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["source_dirty"] = True
    manifest["release_candidate"] = True
    candidate = tmp_path / "candidate.json"
    candidate.write_text(json.dumps(manifest), encoding="utf-8")
    errors = verify_manifest(candidate)
    assert "dirty source cannot be a release candidate" in errors


def test_active_synthesis_does_not_read_legacy_output_directory():
    synthesis_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "src" / "synthesis").glob("*.py"))
    )
    assert "output/" not in synthesis_source
    assert "legacy-output-index.json" not in synthesis_source


def test_manifest_worktree_digest_is_content_bound(tmp_path):
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["worktree"]["digest"] = "0" * 64
    candidate = tmp_path / "stale-worktree.json"
    candidate.write_text(json.dumps(manifest), encoding="utf-8")
    errors = verify_manifest(candidate)
    assert "worktree digest does not match current source state" in errors


def test_release_candidate_requires_browser_and_physical_evidence(tmp_path):
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["source_dirty"] = False
    manifest["release_candidate"] = True
    manifest["verification"]["browser_manifest"] = None
    manifest["verification"]["physical_device_qa"] = "pending"
    candidate = tmp_path / "candidate-without-device-evidence.json"
    candidate.write_text(json.dumps(manifest), encoding="utf-8")
    errors = verify_manifest(candidate)
    assert "release candidate requires current browser evidence" in errors
    assert "release candidate requires passed physical-device QA" in errors
