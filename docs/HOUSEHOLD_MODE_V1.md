# Household / Multi-Subject Mode v1

Status: **foundation implemented; public paid additions disabled by default**

The Human Manual keeps its existing single-subject `analysis-v1` contract complete and free. Multi-subject modes are additive composition surfaces above independently computed subject records.

## Product modes

| Mode | Contract | Membership | Public availability |
| --- | --- | --- | --- |
| Single Human Manual | `analysis-v1` | one primary adult | Free and complete |
| US Pair | `household-v1` / `composition=pair` | exactly primary + partner | Paid, disabled until entitlement infrastructure is enabled |
| WE Household | `household-v1` / `composition=household` | primary + partner/adult family/child/pet, max 8 members | Paid, disabled until entitlement infrastructure is enabled |
| Historical reference | context-only | source-bound reference | Never counted as a paid member |

Prices and payment provider are intentionally unset in `config/household.json`.

## Contract topology

The single-subject API is frozen. The household layer composes records; it does not reimplement the analysis engine.

- `household-v1`: local composition manifest. It contains random subject IDs, role/class metadata, record contract/digest/state and authority attestations.
- `household-subject-projection-v1`: privacy-minimized adult projection containing only system inventory and curated same-system scalar markers.
- `child-profile-v1`: guardian-attested child-safe symbolic worksheet.
- `pet-profile-v1`: owner-attested care-context record with no human symbolic engine.
- `relational-view-v1`: deterministic derived composition view.
- `report-household-v1`: reserved export contract.
- `entitlement-v1`: future signed server-side paid entitlement.

The household manifest does **not** contain canonical names, raw birth inputs, coordinates, result bodies or prose reports.

## Roles and classes

`subject_role` and `subject_class` are separate axes.

| Role | Required class | Membership | Record contract |
| --- | --- | --- | --- |
| primary | person_adult | member | analysis-v1 projection |
| partner | person_adult | member | analysis-v1 projection |
| adult_family | person_adult | member | analysis-v1 projection |
| child | person_minor | member | child-profile-v1 |
| pet | nonhuman_animal | member | pet-profile-v1 |
| reference | historical_reference | context_only | historical-reference-v1 |

Exactly one primary is required. A pair is exactly primary + partner.

## Child policy

Child mode is deliberately narrower than adult analysis. It never calls the adult astrology, Human Design, Jyotish, BaZi, Classical Maya, Tarot or psychological-analysis pathways.

The v1 child worksheet may expose only deterministic structural transforms currently allowlisted by the code:

- Unicode codepoint structure
- base-60 representation
- base-12 representation
- Elder Futhark returned sequence
- Ogham returned sequence

Required public label:

> Child-safe symbolic worksheet — guardian-supplied input; not predictive, diagnostic, or a claim about the child's character or future.

No child self-enrollment is implemented. Guardian authority is an attestation contract, not a claim that the application independently verified legal guardianship.

## Pet policy

Pet mode does not run the human symbolic engine in v1. It stores a bounded care-context record: display alias, species, optional breed/breed mix and age band.

Required public label:

> Pet profile — care context only; no symbolic or health interpretation.

No temperament diagnosis, compatibility claim, health inference or destiny interpretation is permitted.

## Relational semantics

The composition layer may expose role presence, record readiness, system availability, provenance and same-system/same-field adult observations.

A same marker means only: two adult source records returned the same scalar value under the same system and field.

A different marker means only: the values differ under that same system and field.

Neither implies compatibility, incompatibility, harmony, conflict, quality, fate or outcome.

Children and pets do not produce adult-style marker-comparison edges.

Stale or unresolved member records fail closed and suppress the composed view.

## Paid entitlement boundary

The public application does not mint entitlements.

`src/entitlements.py` provides provider-neutral verification for future `entitlement-v1` tokens. A valid entitlement is bound to a household ID, expiry and added-subject limit and must pass server-side signature verification.

The public compose route remains disabled unless both:

1. `HME_HOUSEHOLD_PAID_ENABLED` is enabled; and
2. a sufficiently strong `HME_ENTITLEMENT_SIGNING_KEY` is configured.

There is currently no checkout, webhook receiver, registry persistence or export purchase route. Those remain absent rather than simulated.

## UI

`webapp/static/household.js` is a dormant renderer for already-authorized `relational-view-v1` artifacts.

- **US**: two independent lanes with a neutral composition axis and same-system observation table.
- **WE**: member cards plus provenance-bound adult observations.
- No score, percentage, gauge, winner, ranking or red/green compatibility encoding.
- Child and pet policy labels remain visible.
- Stale/unresolved views render an unavailable state, not a partial relational conclusion.

The module loads with the application but does not expose a public add-subject or checkout control while paid entitlement is disabled.

## Release gates

Before the paid mode can be enabled publicly:

- a real commerce provider must be selected;
- webhook signatures must be verified over raw provider bytes;
- webhook replay/deduplication must be implemented in a durable store;
- only verified payment events may mint signed, expiring entitlements;
- paid routes must verify those entitlements server-side;
- privacy/retention behavior for any persisted household registry must be reviewed;
- child/guardian wording and jurisdictional obligations require legal/policy review;
- mobile, keyboard, screen-reader, print and export QA must be rerun with paid mode enabled.

The free single-person Human Manual does not depend on completion of those gates.
