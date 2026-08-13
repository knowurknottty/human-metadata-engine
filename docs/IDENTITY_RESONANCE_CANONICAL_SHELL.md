# Identity Resonance Canonical Visual Shell

## Decision

**Identity Resonance** is the canonical public-facing visual language. **Human Metadata Engine** remains the authoritative computation/data substrate, and the **Human Metadata Atlas** remains the deep interactive research/provenance layer.

This change is a presentation restoration, not an engine rollback.

## Implementation boundary

The current v1.0 frontend markup, input workflow, accessibility behavior, API contracts, report/download paths, provenance inspector, synthesis layer, and Atlas renderer remain intact.

The restoration is implemented as a CSS override loaded after the existing stylesheet. No historical application JavaScript or historical calculation behavior is restored.

## Visual invariants

- near-black observatory field with restrained gold instrumentation;
- Identity Resonance wordmark in the public shell;
- identity fingerprint visually anchored at the left on wide screens;
- astrology is the dominant central field;
- Tree of Life and Human Design remain graphical and integrated into the same instrument workspace;
- numerology is a dense right-side analytical rail;
- constellation/provenance depth follows the primary composition rather than replacing it;
- evidence-linked narrative and research report remain available below the visual instrument;
- no primary visual surface is hidden on narrow screens.

## Truth boundary

Visual hierarchy does not change epistemic status. Current engine output, schema versions, evidence rules, provenance, confidence labels, and limitations remain authoritative. A restored visual motif must never resurrect superseded calculations, claims, or synthetic data.

## Verification

The branch must pass the complete repository CI gates. Browser/pixel review remains a separate visual acceptance step; passing CI does not itself prove screenshot-level similarity on every device.
