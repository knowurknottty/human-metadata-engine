# Narrative schema contracts v1

The synthesis schemas are embedded under `analysis-v1.synthesis`. They version
independently from `analysis-v1`, `signature-v2`, and `report-v1`.

## `synthesis-evidence-v1`

Top-level fields are `schema_version`, `analysis_id`, `source_contracts`,
`data_quality`, `evidence_items`, `unsupported_topics`, and `warnings`.
`unsupported_topics` explicitly enumerates the sensitive and predictive domains
that v1 cannot infer or discuss.

Each evidence item contains:

- stable `evidence_id` derived from source path and canonical source value;
- `system`, `subsystem`, `source_path`, and exact `source_value`;
- normalized symbol, symbol family, role, tags, mapping strength/provenance/notes;
- epistemic and interpretation classes plus confidence;
- source provenance reference, one or more exact Atlas selection targets,
  report target, limitations, and independence group.

Every source path is tested against the response object. Missing/unavailable
systems emit no evidence.

## `synthesis-plan-v1`

The plan contains central archetype, strongest tension, ranked motifs,
agreements, productive contradictions, gifts, possible shadows, developmental
movements, recurring symbols, missing dimensions, prohibited claims, and
ordered narrative sections. Each claim has a stable ID, type, evidence IDs,
strength, allowed/forbidden language, contradicting evidence IDs, a limitation,
and bounded template metadata.

This object is the authoritative interpretation plan. Realizers cannot add
claims or upgrade confidence.

## `narrative-v1`

Each plain, mythic, or research result contains sections, paragraphs, and
sentences. Every interpretive sentence includes stable sentence ID, claim IDs,
evidence IDs, strength, epistemic label, and contradiction flag. Generation
metadata records deterministic-template engine, null model, temperature zero,
null generation time, template version, deterministic hash, and no remote
provider use.

The response returns all three modes so changing presentation requires no new
analysis, fetch, or recomputation.

## Version discovery

`GET /api/version` reports:

- `synthesis_evidence_schema_version: synthesis-evidence-v1`
- `synthesis_plan_schema_version: synthesis-plan-v1`
- `narrative_schema_version: narrative-v1`

The Markdown export records narrative/evidence schema versions, mode,
sentence evidence references, confidence, limits, and data-quality states.
