# Narrative synthesis contract v2

This is the active nested synthesis contract. The public API remains `analysis-v1`, the compatibility engine remains `signature-v2`, and the public report remains `report-v1`.

## Active contracts

- `synthesis-evidence-v2` — provenance-bound evidence records with full-width content identities.
- `synthesis-plan-v2` — deterministic claim graph with exact evidence ownership and calculation replay identity.
- `narrative-v2` — deterministic presentation records with statement-level text provenance, support provenance, and presentation replay identity.
- `pattern-map-v1` — explanations of alignment, divergence, statement authorship, and input sensitivity derived from the same evidence/claim graph.

The v2 contracts are nested under the existing public response. They do not imply a top-level API major migration.

## Identity and replay

Machine evidence, record, claim, statement, and replay identities use full SHA-256 content digests. Shortened identifiers are display-only and must never be used as machine references.

Evidence identities bind the analysis, source path and value, source contract, record identity, and mapping version. Claim identities canonicalize the evidence set so equivalent evidence ordering produces the same identity while a different claim type produces a different identity.

`calculation_replay_id` binds the evidence packet, motif analysis, agreements, contradictions, and policy versions. Each presentation mode has a separate `presentation_replay_id` that additionally binds the plan, mode, templates, reading library, and lexicon. Incidental timestamps are not replay inputs.

## Epistemic classes

Evidence records keep calculation, supplied data, historical/textual material, traditional symbolic interpretation, project-authored crosswalks, and system-state metadata distinguishable. Project-authored crosswalk and system-state records cannot become motif votes merely by existing.

`support_strength` is a deterministic synthesis-policy label. It is not empirical confidence, scientific validity, or proof about a person. Current public synthesis surfaces state `empirical_status: not_established`.

## Exact binding and fail-closed behavior

Every realized interpretive sentence resolves to exactly one planned claim and exactly the planned evidence set. Dropping evidence, adding unknown evidence, duplicating a claim realization, mixing evidence packet versions, or supplying an unsupported strength/mapping version invalidates the realization.

Generated prose, deterministic composition assets, and external-agent prose are text provenance only. They never become evidence.

## Pattern Map

The Pattern Map adds no evidence and no motif votes.

- **Together** explains which systems map to the same authored theme and how many dependence families are involved.
- **Divergent** preserves tensions and differences without selecting a winner.
- **Statement provenance** separates authored text provenance from evidence/support provenance.
- **Input sensitivity** reports dependency-only effects for missing or uncertain inputs. It says an input *could affect* a result unless an actual paired deterministic recomputation establishes a change.

## Compatibility

Historical v1 synthesis artifacts remain historical. They are not mixed into v2 convergence or promoted to v2 evidence by rewriting their prose. Current results should be regenerated from the original structured inputs whenever those inputs remain available.
