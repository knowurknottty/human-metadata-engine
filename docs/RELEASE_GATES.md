# The Human Manual Release Gates

This document turns the human-usability review into testable release criteria.
It is the source of truth for what can ship as a local demo, paid beta, or
general consumer product. A green repository test suite does not imply that a
deployment, payment boundary, or privacy posture is production-ready.

## Current evidence

| Area | Evidence | Status |
| --- | --- | --- |
| Deterministic engine and API contracts | `python tools/run_tests.py --quiet`; `python -m pytest -q`; `python tools/validate_contracts.py` | Verified locally; the latest pushed commit must also pass CI |
| Structured Know Thyself profile | Adjacent-wing API validation, compatibility tests, status round-trip tests | Verified locally |
| Browser flow | Name-only, full Kirk fixture, unknown time, ambiguity selection, multi-error recovery, alias tokens, report focus/actions, and 320 CSS-pixel completion | Verified in the local in-app browser; physical-device QA remains |
| Location-only birth flow | A place name is geocoded server-side; coordinates and the date-specific historical UTC offset are derived automatically | Verified locally; external service dependency remains |
| Visual knowledge layer | Six computed visual surfaces, a shared provenance inspector, Explorer/Research modes, and text/print equivalents | Verified locally in headless Chrome; physical-device QA remains |
| Narrative synthesis layer | Versioned evidence/plan/narrative contracts, explicit ontology, deterministic compositor, 90+ phrase initial lexicon, verifier, sentence-level evidence links, and local Grounded/Story/Sources views | Automated contracts verified locally; complete physical-device interaction QA remains |
| Human Capacity / 𒈨 reflection | Historical/textual ontology, explicit modern crosswalk, opt-in observation tags, no semantic inference, no score/rank, public-text redaction | API/frontend contracts verified locally; refreshed browser baseline and physical-device interaction QA remain |
| Optional Big Five handling | Untouched sliders render `Not answered` and are omitted from the request payload | Verified locally |
| External deployment reachability | Must be checked from an independent network against the deployed HTTPS domain | Unverified until run |
| Commerce | Checkout, card fields, paywall, and client-side entitlement simulation are absent | Not part of v1.0.0 |
| Report truth boundary | Ten ordered public sections carry controlled machine-readable epistemic metadata and reproduction fields | Verified by public-contract tests |
| Persistence | Public web process does not intentionally retain profile inputs; infrastructure logs require separate policy | Process-local only |

## Gate A — Public demo

Release only when every item below is true:

- [ ] A stable domain serves the app over HTTPS with a valid certificate.
- [ ] `/healthz` and `/readyz` is reachable from an independent network.
- [ ] The deployed process is supervised with restart policy. Application request timeouts and structured error codes are implemented locally.
- [ ] Security headers are present at the actual ingress, including HSTS, CSP, Referrer-Policy, Permissions-Policy, and X-Content-Type-Options.
- [ ] The UI says that inputs are processed for the report, are not intentionally retained by the web process, and may still appear in infrastructure logs.
- [x] A regular user can provide a birth place without calculating latitude, longitude, or UTC offset; the server resolves those values for the requested date (verified by API and browser tests).
- [x] The privacy notice names Open-Meteo and explains that the supplied place is sent to it; production availability monitoring remains an operations gate.
- [x] No checkout, card field, paywall, or simulated entitlement is shipped.
- [x] Optional household roster intake is browser-memory-only: spouse/partner, adult family, child/adolescent, and pet entries are not submitted with the primary scan; paid US/WE composition remains fail-closed.
- [x] Untouched Big Five fields remain “Not answered” and are not submitted as neutral scores (verified in local browser flow and frontend contract test).
- [x] The first result view preserves the six protected computed visual surfaces and adds the versioned Atlas expansion layer with declared visual homes for the broader backend, plus the provenance/limitations inspector. The complete report remains the Research-mode reference layer (verified by frontend contracts; browser interaction verification is release-candidate evidence).
- [x] Magic mode exposes The Living Pattern from a deterministic evidence/claim plan. Grounded, Story, and Sources preserve identical claims, support strength, contradictions, and evidence links. Story is generated in-process by the deterministic compositor and versioned prose lexicon; no remote model is required or called. Data mode keeps narrative disabled.
- [x] Active synthesis packets are v2-only, use full-width content identities, exact claim/evidence binding, fail-closed strength/mapping validation, and separate calculation/presentation replay identities.
- [x] Pattern Map explains alignment, preserved divergence, statement authorship/support provenance, and input sensitivity without adding evidence or motif votes.
- [x] Agent Handoff v2 rejects legacy synthesis evidence packets and exports a reviewed projection rather than arbitrary nested response data.
- [x] Existing generated `output/` artifacts are cryptographically indexed as quarantined historical material and excluded from active synthesis evidence.
- [x] The development manifest records the current dirty source state as `release_candidate: false`; a clean immutable release manifest remains a release-candidate gate.
- [x] The Human Capacity / Sumerian me request contract is opt-in, requires explicit user-selected capacity tags, rejects unknown/duplicate domain IDs, and returns no automatic score/rank/assignment.
- [ ] Browser and physical-device QA confirms the new Sumerian me observation/tag controls and three-layer result remain understandable, keyboard-operable, and overflow-free at release target widths.
- [x] Dynamic Enneagram wing choices expose only the two adjacent wings, and the API rejects impossible pairings (frontend and API tests).
- [x] CSS-viewport QA confirms readable explanatory text, stacked controls, expandable technical detail, and zero horizontal overflow at 320, 360, 390, 412, and 768 CSS pixels.
- [x] Release-owner acceptance: the 320/360/390/412/768 CSS-viewport emulator/browser matrix is accepted in lieu of separate physical-device QA for this 2026-09-24 release.

## Gate B — Optional future paid US / WE beta

Gate A must be green, plus. The complete single-person Human Manual remains free; payment applies only to additional household subjects and relational composition.

- [x] `analysis-v1` remains the complete free single-person product; no report sections are withheld to manufacture an upsell.
- [x] `household-v1`, `relational-view-v1`, child-profile-v1, pet-profile-v1, and provider-neutral entitlement verification seams exist behind a default-off paid feature state.
- [x] Disabled deployments expose no fake checkout, fake unlock, client-minted entitlement, household persistence, or webhook receiver.
- [ ] A real hosted checkout/payment provider is configured; raw card data never passes through the application HTML.
- [ ] The payment provider webhook is verified server-side over raw request bytes, with timestamp/replay checks and durable event deduplication.
- [ ] Only a verified payment event creates a signed, expiring `entitlement-v1`.
- [ ] `/api/household/compose` verifies household binding, expiry, signature, and added-subject limits before returning `relational-view-v1`.
- [ ] US Pair and WE Household prices, receipts, refunds, support contact, and deletion/retention terms are published.
- [ ] Any persisted household registry has an explicit retention/deletion policy and does not put names, birth inputs, or result bodies into the household manifest.
- [ ] Child/guardian authority wording and jurisdictional obligations receive legal/policy review before public child-profile enrollment.
- [ ] Paid-mode accessibility review covers US/WE focus management, table summaries, member cards, unavailable/stale states, keyboard use, reduced motion, contrast, mobile layout, and print/export.
- [ ] At least 20–30 observed-user sessions complete the US/WE flow without assistance and do not interpret same-system observations as compatibility scores.

## Gate C — General consumer release

Gate B must be green, plus:

- [ ] Nontechnical adults can explain the result in two sentences after reading it.
- [ ] At least 90% of testers identify the resonance/pattern index as non-accuracy and non-diagnostic.
- [ ] At least 90% distinguish measured calculations, self-report, traditional interpretation, and experimental index output.
- [ ] At least 80% identify one low-risk practical reflection or experiment.
- [ ] Fewer than 10% interpret the output as diagnosis, fate, objective ranking, or relationship compatibility.
- [ ] Mobile QA covers current iPhone Safari and low-end Android Chrome.
- [ ] A documented reference-population policy exists; comparison output is clearly mathematical proximity, not human similarity.
- [ ] An independent security review and dependency/SBOM review are complete.
- [ ] A rollback, backup, monitoring, and incident-response runbook has an owner and a successful drill.

## Required comprehension test

Give a tester a generated report and ask:

1. What does the main index measure?
2. Which outputs are direct calculations?
3. Which values came from the tester?
4. Which outputs are traditional or symbolic interpretations?
5. Does a high index mean the report is accurate?
6. What changed because birth data was supplied?
7. What is one useful action to take?
8. What does the report not prove?
9. What would make the report worth paying for?
10. Which sentence was hardest to understand?

Record answers, completion time, abandonment point, and whether the tester
misread symbolic language as diagnosis or prediction. Do not use likes or
general enthusiasm as the release metric.

## Scope deliberately deferred

Stress response and boundary style remain out of the public profile until the
product has an established self-observation model for them. Additional unreviewed symbolic encoders are deferred: increasing breadth before improving comprehension,
trust, payment boundaries, and actionability would increase apparent complexity without improving the user outcome. The Sumerian *me* addition is treated differently because its corpus layer is historical/textual and its optional personal crosswalk is explicitly user-tagged and separately versioned.

## Repository release checklist

These gates apply to each candidate commit and are distinct from deployment
and observed-user gates above:

- [x] Canonical runner and standard pytest pass locally.
- [x] Server starts with the pinned Swiss Ephemeris dependency.
- [x] `/healthz`, `/readyz`, and `/api/version` return their documented contracts locally.
- [x] Historical timezone fixtures cover Evanston, Chicago summer/winter, Arizona, Newfoundland, and India.
- [x] The Kirk Evan Brown fixture preserves 1982-02-04 01:42 America/Denver and its UTC conversion.
- [x] Public request, report, and static-rendering security regression checks pass.
- [x] Public report wording and metadata separate calculations, astronomy, self-report, symbolic conventions, heuristics, and synthesis.
- [x] Narrative evidence paths resolve to returned values; all deterministic sentences pass the claim/evidence, prohibited-language, and prohibited-topic verifier; sparse profiles fail closed.
- [ ] Mobile layout has been checked in a real current iPhone Safari and low-end Android Chrome; a 320 CSS-pixel browser check alone is insufficient.
- [x] Markdown download and browser HTML renderer have structural/escaping tests; the v1.0 Atlas exposes native download and print actions while preserving the reference report actions.
- [x] Print CSS removes interactive controls, preserves heading order, and applies page-break protections; Chrome 149 print-preview and saved-PDF inspection passed locally with browser headers and footers disabled.
- [x] README version, dependency, route, geocoding, privacy, and duplicate-contract descriptions distinguish the v1.0.0 application from the `analysis-v1` API, `signature-v2` engine, and `report-v1` report contracts.
- [x] Production payment behavior is removed.
- [x] Public versus legacy analytics/report paths are documented and tested.
- [ ] Git status is clean after the release commit.
