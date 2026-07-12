# Identity Resonance Release Gates

This document turns the human-usability review into testable release criteria.
It is the source of truth for what can ship as a local demo, paid beta, or
general consumer product. A green repository test suite does not imply that a
deployment, payment boundary, or privacy posture is production-ready.

## Current evidence

| Area | Evidence | Status |
| --- | --- | --- |
| Deterministic engine and API contracts | `python3 tools/run_tests.py --quiet`; `python3 tools/validate_contracts.py` | Verified locally |
| Structured Know Thyself profile | Adjacent-wing API validation, compatibility tests, status round-trip tests | Verified locally |
| Browser flow | Local Data → Magic profile rendering, dynamic wings, secondary-pattern warning, console health | Verified locally |
| Plain-English result layer | First-view synthesis, evidence legend, and neutral pattern-index language | Verified locally |
| Optional Big Five handling | Untouched sliders render `Not answered` and are omitted from the request payload | Verified locally |
| External deployment reachability | Must be checked from an independent network against the deployed HTTPS domain | Unverified until run |
| Commerce | Current checkout is explicitly a simulated demo and client-side unlock | Not production-ready |
| Persistence | Public web process does not intentionally retain profile inputs; infrastructure logs require separate policy | Process-local only |

## Gate A — Public demo

Release only when every item below is true:

- [ ] A stable domain serves the app over HTTPS with a valid certificate.
- [ ] `/api/health` (or an equivalent public health endpoint) is reachable from an independent network.
- [ ] The process is supervised with restart policy, bounded timeouts, and structured error IDs.
- [ ] Security headers are present at the actual ingress, including HSTS, CSP, Referrer-Policy, Permissions-Policy, and X-Content-Type-Options.
- [ ] The UI says that inputs are processed for the report, are not intentionally retained by the web process, and may still appear in infrastructure logs.
- [ ] The page clearly labels checkout as a demo and does not imply that a test card creates a real purchase.
- [x] Untouched Big Five fields remain “Not answered” and are not submitted as neutral scores (verified in local browser flow and frontend contract test).
- [x] The first result view contains a plain-English synthesis, an evidence legend, and an explicit “what this does not mean” statement (verified in local browser flow and frontend contract test).
- [ ] Dynamic Enneagram wing choices expose only the two adjacent wings, and the API rejects impossible pairings.
- [ ] Mobile QA confirms readable explanatory text, expandable technical detail, and no critical meaning encoded only by color.

## Gate B — Paid beta

Gate A must be green, plus:

- [ ] Free analysis returns preview data only; the full report is not present in the free response or hidden only with CSS.
- [ ] Stripe-hosted Checkout or PaymentIntent is used; raw card data never passes through the application HTML.
- [ ] A server-verified webhook creates a signed, expiring entitlement.
- [ ] The paid endpoint checks entitlement before returning the full report.
- [ ] Receipts, refunds, support contact, and deletion/retention terms exist.
- [ ] Report exports include engine version, report schema version, convention-set version, build revision, and reproducibility ID.
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
