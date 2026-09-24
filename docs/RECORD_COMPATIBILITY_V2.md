# Record compatibility and legacy quarantine v2

## Compatibility boundary

The stable public boundary remains `analysis-v1` + `signature-v2` + `report-v1`. Current nested synthesis uses `synthesis-evidence-v2`, `synthesis-plan-v2`, and `narrative-v2`.

Legacy generated files under `output/` are preserved byte-for-byte and indexed by `release/legacy-output-index.json`. The index records path, byte length, SHA-256 digest, and `active_evidence: false`.

## No silent migration

Legacy narrative/report prose is not sufficient to reconstruct all current evidence bindings, policy versions, source-value digests, and dependence semantics. Therefore this repository does **not** auto-promote v1 prose into active v2 evidence.

The safe migration path is:

1. preserve the legacy artifact and digest;
2. recover the original structured input/source records;
3. rerun the current deterministic engine;
4. produce a new v2 evidence packet and replay identities;
5. compare old and new outputs as separate historical/current artifacts.

If the original source records are unavailable, the legacy artifact remains quarantined historical material.

## Mixed-version rule

An active v2 narrative may use only the current v2 evidence packet. The verifier rejects mixed evidence packet versions. Agent Handoff v2 likewise refuses a legacy synthesis evidence packet rather than silently translating it.

## Development versus release evidence

`release/manifest.dev.json` may describe a dirty development worktree, but it must state `release_candidate: false`. A dirty source tree cannot be promoted to release-candidate status. Physical-device QA and deployment reachability remain independent release gates.
