#!/usr/bin/env python3
"""Build a content-bound development manifest that cannot masquerade as a release candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release" / "manifest.dev.json"
MANIFEST_REL = "release/manifest.dev.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(role: str, rel: str, media_type: str = "application/json") -> dict:
    path = ROOT / rel
    return {
        "role": role,
        "path": rel,
        "media_type": media_type,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def git(*args: str, binary: bool = False):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=not binary)


def worktree_identity() -> dict:
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
    return {
        "schema_version": "human-manual-worktree-identity-v1",
        "digest": hashlib.sha256(encoded).hexdigest(),
        "tracked_diff_sha256": payload["tracked_diff_sha256"],
        "untracked_count": len(untracked),
        "dirty_path_count": len(git("status", "--porcelain=v1").splitlines()) - (1 if MANIFEST.exists() else 0),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verification-status", choices=("in_progress", "passed", "failed"), default="in_progress")
    parser.add_argument("--verification-command", action="append", default=[])
    parser.add_argument("--verification-summary", action="append", default=[])
    parser.add_argument("--required-skips", type=int)
    parser.add_argument("--browser-manifest")
    parser.add_argument("--physical-device-qa", choices=("pending", "passed", "failed"), default="pending")
    args = parser.parse_args()
    if args.verification_status == "passed" and not args.verification_command:
        parser.error("--verification-status passed requires at least one --verification-command")

    source_commit = git("rev-parse", "HEAD").strip()
    dirty = bool(git("status", "--porcelain"))
    payload = {
        "schema_version": "human-manual-release-manifest-v1",
        "release_id": "human-manual-r3-development",
        "product": "The Human Manual",
        "source_commit": source_commit,
        "source_dirty": dirty,
        "release_candidate": False,
        "build_revision": source_commit,
        "worktree": worktree_identity(),
        "contracts": {
            "api": "analysis-v1",
            "engine": "signature-v2",
            "record": "system-result-v2",
            "synthesis_evidence": "synthesis-evidence-v2",
            "synthesis_plan": "synthesis-plan-v2",
            "narrative": "narrative-v2",
            "pattern_map": "pattern-map-v1",
            "report": "report-v1",
            "handoff": "human-manual-agent-handoff-v2",
            "household": "household-v1",
            "relational_view": "relational-view-v1",
            "child_profile": "child-profile-v1",
            "pet_profile": "pet-profile-v1",
            "entitlement": "entitlement-v1",
            "tarot_art": "tarot-art-deck-v1",
        },
        "artifacts": [
            artifact("active-evidence-schema", "schemas/synthesis-evidence-v2.schema.json"),
            artifact("system-record-schema", "schemas/system-result-v2.schema.json"),
            artifact("household-schema", "schemas/household-v1.schema.json"),
            artifact("relational-view-schema", "schemas/relational-view-v1.schema.json"),
            artifact("child-profile-schema", "schemas/child-profile-v1.schema.json"),
            artifact("pet-profile-schema", "schemas/pet-profile-v1.schema.json"),
            artifact("tarot-art-manifest", "webapp/static/tarot-deck-v1/manifest.json"),
            artifact("release-schema", "schemas/release-manifest-v1.schema.json"),
            artifact("legacy-quarantine-index", "release/legacy-output-index.json"),
        ],
        "legacy": {
            "active_evidence_version": "synthesis-evidence-v2",
            "migration_policy": "regenerate_from_source_inputs; never promote legacy prose to active evidence",
            "quarantined_indexes": ["release/legacy-output-index.json"],
        },
        "verification": {
            "status": args.verification_status,
            "required_skips": args.required_skips,
            "commands": args.verification_command,
            "summaries": args.verification_summary,
            "browser_manifest": args.browser_manifest,
            "physical_device_qa": args.physical_device_qa,
        },
        "runtime": {"default": "offline", "remote_ai": False},
        "epistemic": {"deterministic_replay": True, "empirical_validation": "not_established"},
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"DEVELOPMENT_MANIFEST_WRITTEN dirty={dirty} worktree={payload['worktree']['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
