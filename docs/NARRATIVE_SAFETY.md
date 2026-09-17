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

Core synthesis is in-process, deterministic, and not persisted. The optional remote Mythic adapter is a separate presentation path and is used only when configured/selected; it receives a redacted derived-facts packet rather than the raw profile. No raw profile is added to application request logs. Markdown
downloads use a random, short-lived, process-memory token. The visible browser
action submits a same-origin form, receives a `303` redirect, and follows that
redirect to a GET attachment in the same user-initiated navigation instead of
waiting on an asynchronous handoff.
The JSON POST variant remains available for bounded API clients. Both paths
queue the generated report for at most 120 seconds and serve it with
`Cache-Control: no-store`. The bounded queue holds at most 32 reports and writes
no server-side report file.

Exports intentionally omit exact coordinates, exact birth location, and raw
observation text under the existing public redaction/report policy. The optional Sumerian *me* reflection likewise returns observation references, source/confidence metadata, explicit capacity tags, and matched corpus categories without copying raw observation prose into the reflection object. A user who saves a Markdown or PDF file is responsible for the resulting local copy.

## Optional AI boundary

The core narrative remains deterministic and local. The current UI also exposes an optional remote Mythic narration adapter when configured. That adapter receives a redacted packet of derived symbolic facts and plan/theme hints; the implementation excludes the person's name, aliases, raw birth date/time/location/coordinates, raw psychology, user observations, and user-context evidence. Remote failure falls back to the deterministic Mythic realization and never blocks core analysis.

Any future remote adapter must preserve the same rule: disclose provider/model and transmitted field classes, never make remote operation mandatory, validate the returned structure/facts, and fail back to deterministic output. The Sumerian *me* reflection is not transmitted as personal observation evidence to the remote Mythic adapter under the current contract.

## Resource limits and isolation

The analysis request remains bounded to 64 KiB and the existing concurrency and
rate limits. Evidence extraction iterates only bounded response collections.
Evidence IDs incorporate path and canonical value, preventing silent collisions
within a response; tests require uniqueness. Synthesis has no cross-user cache.
Reset replaces the dashboard DOM and resets the in-memory evidence map so a new
analysis cannot retain stale sentences.
