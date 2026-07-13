# Human Metadata Engine Release Gates

This document turns the human-usability review into testable release criteria.
It is the source of truth for what can ship as a local demo, paid beta, or
general consumer product. A green repository test suite does not imply that a
deployment, payment boundary, or privacy posture is production-ready.

## Current evidence

| Area | Evidence | Status |
| --- | --- | --- |
| Deterministic engine and API contracts | `python3 tools/run_tests.py --quiet`; `python3 -m pytest -q`; `python3 tools/validate_contracts.py` | Verified locally; CI pending this commit |
| Structured Know Thyself profile | Adjacent-wing API validation, compatibility tests, status round-trip tests | Verified locally |
| Browser flow | Name-only, full Kirk fixture, unknown time, ambiguity selection, multi-error recovery, alias tokens, report focus/actions, and 320 CSS-pixel completion | Verified in the local in-app browser; physical-device QA remains |
| Location-only birth flow | A place name is geocoded server-side; coordinates and the date-specific historical UTC offset are derived automatically | Verified locally; external service dependency remains |
| Plain-English result layer | Report identity, coverage, overview, information-type labels, explicit tensions, and neutral convergence language | Verified locally |
| Optional Big Five handling | Untouched sliders render `Not answered` and are omitted from the request payload | Verified locally |
| External deployment reachability | Must be checked from an independent network against the deployed HTTPS domain | Unverified until run |
| Commerce | Checkout, card fields, paywall, and client-side entitlement simulation are absent | Not part of v0.8.0 |
| Report truth boundary | Ten ordered public sections carry controlled machine-readable epistemic metadata and reproduction fields | Verified by public-contract tests |
| Persistence | Public web process does not intentionally retain profile inputs; infrastructure logs require separate policy | Process-local only |

## Gate A — Public demo

Release only when every item below is true:

- [ ] A stable domain serves the app over HTTPS with a valid certificate.
- [ ] `/api/health` (or an equivalent public health endpoint) is reachable from an independent network.
- [ ] The deployed process is supervised with restart policy. Application request timeouts and structured error codes are implemented locally.
- [ ] Security headers are present at the actual ingress, including HSTS, CSP, Referrer-Policy, Permissions-Policy, and X-Content-Type-Options.
- [ ] The UI says that inputs are processed for the report, are not intentionally retained by the web process, and may still appear in infrastructure logs.
- [x] A regular user can provide a birth place without calculating latitude, longitude, or UTC offset; the server resolves those values for the requested date (verified by API and browser tests).
- [x] The privacy notice names Open-Meteo and explains that the supplied place is sent to it; production availability monitoring remains an operations gate.
- [x] No checkout, card field, paywall, or simulated entitlement is shipped.
- [x] Untouched Big Five fields remain “Not answered” and are not submitted as neutral scores (verified in local browser flow and frontend contract test).
- [x] The first result view contains report identity, plain-English coverage, an interpretive boundary, information-type labels, and explicit disagreement between systems (verified in local browser flow and frontend contract tests).
- [x] Dynamic Enneagram wing choices expose only the two adjacent wings, and the API rejects impossible pairings (frontend and API tests).
- [x] CSS-viewport QA confirms readable explanatory text, stacked controls, expandable technical detail, and zero horizontal overflow at 320, 360, 390, 412, and 768 CSS pixels.
- [ ] Physical-device QA confirms the same behavior in current iPhone Safari and Android Chrome.

## Gate B — Optional future paid beta

Gate A must be green, plus:

- [ ] Free analysis returns preview data only; the full report is not present in the free response or hidden only with CSS.
- [ ] Stripe-hosted Checkout or PaymentIntent is used; raw card data never passes through the application HTML.
- [ ] A server-verified webhook creates a signed, expiring entitlement.
- [ ] The paid endpoint checks entitlement before returning the full report.
- [ ] Receipts, refunds, support contact, and deletion/retention terms exist.
- [x] Report exports include engine version, report schema version, convention-set version, build revision, and reproducibility ID.
- [ ] At least 20–30 observed-user sessions complete the core flow without assistance.
- [ ] Accessibility review covers focus management, form errors, chart summaries, keyboard use, reduced motion, contrast, and print output.

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
product has an established self-observation model for them. More symbolic
encoders are also deferred: increasing breadth before improving comprehension,
trust, payment boundaries, and actionability would increase apparent complexity
without improving the user outcome.

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
- [ ] Mobile layout has been checked in a real current iPhone Safari and low-end Android Chrome; a 320 CSS-pixel browser check alone is insufficient.
- [x] Markdown download and browser HTML renderer have structural/escaping tests; the v0.8 interface exposes native download and print actions at the report top and end.
- [x] Print CSS removes interactive controls, preserves heading order, and applies page-break protections; Chrome 149 print-preview and saved-PDF inspection passed locally with browser headers and footers disabled.
- [x] README version, dependency, route, geocoding, privacy, and duplicate-contract descriptions distinguish the v0.8.0 application from the `analysis-v1` API, `signature-v2` engine, and `report-v1` report contracts.
- [x] Production payment behavior is removed.
- [x] Public versus legacy analytics/report paths are documented and tested.
- [ ] Git status is clean after the release commit.
