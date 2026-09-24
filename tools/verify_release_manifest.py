#!/usr/bin/env python3
"""Verify Human Manual release/development manifests without mutating artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_REL = "release/manifest.dev.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args: str, binary: bool = False):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=not binary)


def current_worktree_digest() -> str:
    head = git("rev-parse", "HEAD").strip()
    diff = git("diff", "--binary", "HEAD", "--", ".", f":(exclude){MANIFEST_REL}", binary=True)
    raw_untracked = git("ls-files", "--others", "--exclude-standard", "-z", binary=True)
    untracked = []
    for raw in sorted(part for part in raw_untracked.split(b"\0") if part):
        rel = raw.decode("utf-8")
        if rel == MANIFEST_REL:
            continue
        path = ROOT / rel
        if path.is_file():
            untracked.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    payload = {
        "head": head,
        "tracked_diff_sha256": hashlib.sha256(diff).hexdigest(),
        "untracked": untracked,
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def verify_manifest(path: Path) -> list[str]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if manifest.get("schema_version") != "human-manual-release-manifest-v1":
        errors.append("unsupported manifest schema")
    if manifest.get("release_candidate") and manifest.get("source_dirty"):
        errors.append("dirty source cannot be a release candidate")
    if manifest.get("epistemic", {}).get("empirical_validation") != "not_established":
        errors.append("manifest must preserve empirical-validation boundary")
    if manifest.get("legacy", {}).get("active_evidence_version") != "synthesis-evidence-v2":
        errors.append("active evidence version is not synthesis-evidence-v2")

    head = git("rev-parse", "HEAD").strip()
    if manifest.get("source_commit") != head:
        errors.append("source commit does not match current HEAD")
    worktree = manifest.get("worktree") or {}
    if worktree.get("digest") != current_worktree_digest():
        errors.append("worktree digest does not match current source state")

    verification = manifest.get("verification") or {}
    if verification.get("status") == "passed":
        if not verification.get("commands"):
            errors.append("passed verification requires recorded commands")
        if verification.get("required_skips") not in (0, None):
            errors.append("passed verification cannot contain required skips")

    if manifest.get("release_candidate"):
        if verification.get("status") != "passed":
            errors.append("release candidate requires passed verification")
        if not verification.get("browser_manifest"):
            errors.append("release candidate requires current browser evidence")
        if verification.get("physical_device_qa") != "passed":
            errors.append("release candidate requires passed physical-device QA")

    for artifact in manifest.get("artifacts", []):
        artifact_path = ROOT / artifact["path"]
        if not artifact_path.is_file():
            errors.append(f"missing artifact: {artifact['path']}")
            continue
        actual_size = artifact_path.stat().st_size
        actual_digest = sha256_file(artifact_path)
        if actual_size != artifact.get("bytes"):
            errors.append(f"size mismatch: {artifact['path']}")
        if actual_digest != artifact.get("sha256"):
            errors.append(f"digest mismatch: {artifact['path']}")

    for index_path in manifest.get("legacy", {}).get("quarantined_indexes", []):
        resolved = ROOT / index_path
        if not resolved.is_file():
            errors.append(f"missing legacy index: {index_path}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", nargs="?", default=MANIFEST_REL)
    args = parser.parse_args()
    path = ROOT / args.manifest
    errors = verify_manifest(path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("RELEASE_MANIFEST_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
