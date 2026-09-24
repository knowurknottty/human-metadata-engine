# Narrative safety and privacy

## Trust boundary

Names, aliases, places, psychology fields, source labels, and any future model
output are untrusted. Existing public validation rejects markup/control input.
Narrative rendering passes every dynamic value through HTML escaping. The
synthesis engine consumes validated structured values, not prompts, DOM text,
SVG geometry, or CSS.

## Verifier

The deterministic post-realization verifier rejects:

- unknown claim or evidence IDs;
- sentence evidence outside its allowed claim;
- interpretive sentences without claim IDs;
- omitted planned claims (including contradiction claims);
- every configured sensitive/predictive topic and the destiny, certainty,
  diagnosis, and guarantee phrases.

Critical values appear only by copying structured evidence values. The v1
realizer does not accept free text, remote model output, or arbitrary template
instructions. Dedicated tests mutate valid output to prove the verifier fails
closed on invented IDs, prohibited language, and prohibited topics.

## Privacy

Core synthesis and all three public narrative views are in-process, deterministic, and not persisted. No remote language model receives profile or narrative data from the public application path. No raw profile is added to application request logs. Markdown downloads use a random, short-lived, process-memory token. The visible browser
action submits a same-origin form, receives a `303` redirect, and follows that
redirect to a GET attachment in the same user-initiated navigation instead of
waiting on an asynchronous handoff.
The JSON POST variant remains available for bounded API clients. Both paths
queue the generated report for at most 120 seconds and serve it with
`Cache-Control: no-store`. The bounded queue holds at most 32 reports and writes
no server-side report file.

Exports intentionally omit exact coordinates, exact birth location, and raw
observation text under the existing public redaction/report policy. The optional Sumerian *me* reflection likewise returns observation references, source/confidence metadata, explicit capacity tags, and matched corpus categories without copying raw observation prose into the reflection object. A user who saves a Markdown or PDF file is responsible for the resulting local copy.

## External-agent boundary

The public application does not call a remote language model for narrative prose. Story mode is produced by the deterministic compositor and versioned prose lexicon. The Markdown export includes an **Agent Handoff** section so a person may deliberately take the file to an assistant of their choice after download. That external use is outside this server's trust boundary; the handoff instructs the receiving agent to preserve provenance, contradictions, missing data, and epistemic labels and not invent personal facts.

## Resource limits and isolation

The analysis request remains bounded to 64 KiB and the existing concurrency and
rate limits. Evidence extraction iterates only bounded response collections.
Evidence IDs incorporate path and canonical value, preventing silent collisions
within a response; tests require uniqueness. Synthesis has no cross-user cache.
Reset replaces the dashboard DOM and resets the in-memory evidence map so a new
analysis cannot retain stale sentences.


## Active v2 safety boundary

Current narrative synthesis fails closed on malformed support-strength values, unsupported mapping provenance, mixed evidence packet versions, duplicate evidence identities, unknown evidence, and sentence evidence that differs from the exact planned claim evidence. `support_strength` is an internal deterministic synthesis-policy label and must not be presented as empirical confidence.

Agent Handoff v2 accepts only the active `synthesis-evidence-v2` packet. Its evidence and normalized-input sections are explicit projections. Generated narrative text, external-agent text, and deterministic prose assets remain text provenance and cannot become evidence.

The Pattern Map is explanatory only. It may state that an uncertain input *could affect* dependent calculations. It may say a value *changed* only after an actual deterministic paired recomputation; it never invents a substitute birth time, location, name, or other private value.
