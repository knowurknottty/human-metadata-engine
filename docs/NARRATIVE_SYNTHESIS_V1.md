# Narrative Synthesis Engine v1

The public feature is named **Human Metadata Narrative** and appears in the
Atlas as **The Living Pattern**. The first name describes the versioned data
product; the second matches the Atlas's visual, exploratory language without
claiming that a symbolic synthesis is a scientific model of a person.

## Boundary and data flow

The subsystem consumes the structured `analysis-v1` result before public
redaction and never reads the DOM or rendered SVGs:

```text
analysis-v1 / signature-v2
  -> fail-closed system extractors
  -> synthesis-evidence-v1
  -> motif-ontology-v1 normalization
  -> independent-group motif ranking
  -> agreement and polarity analysis
  -> synthesis-plan-v1
  -> deterministic plain, mythic, and research realization
  -> claim verifier
  -> narrative-v1 + Atlas + Markdown/print
```

The code boundaries are:

- `src/synthesis/extractors.py` — separate extractors for number systems,
  measurable name structure, astrology, Human Design, Tree of Life, Chinese
  mappings, and user-supplied context.
- `src/synthesis/data/motif_ontology_v1.json` and `ontology.py` — inspectable,
  versioned, project-authored normalization decisions.
- `src/synthesis/analysis.py` — motif ranking, agreement, and contradiction.
- `src/synthesis/plan.py` — deterministic claims and section architecture.
- `src/synthesis/realize.py` — bounded mode-specific templates.
- `src/synthesis/verify.py` — sentence/claim/evidence, prohibited-language, and
  prohibited-topic verification.
- `src/synthesis/pipeline.py` — composition only; no extraction or scoring
  rules are hidden here.

## Ranking

Each evidence record belongs to an `independence_group`. A motif receives only
the strongest mapping weight from each group. Further records in the same group
add a capped `0.05` recurrence bonus, up to `0.30`; they do not create new
independent support. Mapping weights are strong `1.0`, moderate `0.65`, and weak
`0.35`. Missing astronomy applies a `0.15` data-quality penalty and partial
astronomy applies `0.05`.

Confidence is high only with at least three independent groups and weighted
support of at least `2.4`; two independent groups produce medium confidence;
one group remains low. The full arithmetic, excluded evidence, recurrence, and
penalties are serialized in every motif record.

## Agreement and contradiction

An agreement requires at least two independence groups normalized to the same
motif. It is labeled thematic agreement and explicitly warns that symbolic
systems are not independent empirical measurements.

Contradiction detection uses an explicit polarity table (for example autonomy
and belonging, freedom and structure, or analysis and intuition). Both poles
retain their own evidence. The plan records context, possible distortion,
possible integrated expression, uncertainty, and `unresolved: true`; realization
cannot erase that state.

## Central pattern and modes

A central archetypal title is composed only when the leading motif has at least
two independent groups. Otherwise the output says that no single archetype
dominates. Titles compose the highest supported motifs instead of selecting a
generic personality from a small fixed catalog.

Plain, mythic, and research modes use the same claim IDs, evidence IDs,
strengths, contradictions, and section plan. Only wording changes. Default
operation is deterministic and local. The v1 release has no model adapter and
sends no profile data to a remote AI provider.

## Data quality

- Name-only synthesis omits astrology and Human Design evidence and explicitly
  describes the profile as partial.
- Unknown-time astrology can contribute only returned non-time-sensitive data;
  Human Design remains unavailable.
- Ambiguous locations fail before analysis and therefore cannot produce a
  narrative.
- Psychology is absent unless supplied. When present it is labeled
  `user_supplied`, remains one independence group, and is never represented as
  calculated.
- Data mode keeps its existing computed-measurements-only policy; narrative
  synthesis is explicitly disabled there.

## Deterministic seal

The central seal is a text mark made from the first two letters of the dominant
motif IDs. It encodes no additional result, does not claim occult provenance,
and is not biometric. Its accessible name gives the full central title.
