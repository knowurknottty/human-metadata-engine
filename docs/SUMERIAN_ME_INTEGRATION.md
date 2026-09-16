# Sumerian *me* Integration Contract

## Purpose

Human Metadata exposes the Sumerian *me* as an evidence-bearing historical corpus layer without converting it into an invented ancient personality system.

## Layer 1 — historical/textual inventory

Source of record for the bounded runtime inventory: ETCSL 1.3.1, *Inana and Enki*. The current implementation retains 81 legible named items visible in the surviving final recitation. Damaged or illegible placeholders are excluded rather than reconstructed.

Runtime identity: `sumerian_me_ontology`, interpretation level `historical`, ontology version `etcsl-1.3.1-visible-inventory-v1`.

The value 81 is a bounded surviving-text count, not a claim that ancient Sumerian tradition contained exactly 81 *me* in total.

## Layer 2 — modern analytical grouping

The nine thematic categories in `src/encoders/sumerian_me.py` are Human Metadata classifications. ETCSL does not present the list under those nine headings, and the grouping does not preserve source order.

Each category therefore carries `classification_epistemic_layer = modern_analytic`.

## Layer 3 — Human Capacity crosswalk

`inversion-labs-human-capacity-crosswalk-v1` maps the nine analytical categories onto modern capacity domains such as governance, technical skill, communication, care, judgment, conflict, intimacy, transition, and social norms.

This crosswalk is an Inversion Labs interpretive artifact. It is not ancient Sumerian doctrine and must never be cited as source-text evidence.

## Layer 4 — optional personal reflection

Personal mapping is disabled by default. A future reflection layer may compare explicitly observed or self-reported evidence with the modern capacity domains, but only under a separately versioned convention.

Forbidden automatic bases include name, birth data, numerology, astrology, and symbolic resonance scores. None establishes that a modern person possesses or corresponds to a particular *me*.

## Invariants

1. Historical inventory changes require source evidence and provenance updates.
2. Damaged text remains damaged unless a separately cited scholarly reconstruction is intentionally added.
3. Modern classifications and crosswalks remain visibly distinct from historical claims.
4. The *me* layer remains excluded from identity resonance/fingerprint scoring.
5. Any future personalized result must identify its observed/self-reported inputs and its modern mapping version.
6. Reports and APIs must preserve `interpretation_level = historical` for the corpus layer.

## Verification

Focused tests: `tests/test_symbolic_roadmap.py` and `tests/test_symbolic_contract.py`.
Full regression gate: `pytest -q`.

## Opt-in personal reflection contract

`sumerian-me-reflection-v1` is disabled by default. When explicitly enabled, it may use only
`capacity_domains` tags that the user attached to observation records. It does not infer tags
from free text and does not use a name, birth data, numerology, astrology, Human Design, or
resonance score as evidence.

The result reports modern category matches and the historical corpus items grouped under those
categories. This is a comparison surface, not a claim that the subject possesses a Sumerian *me*.
Raw observation text is never copied into the reflection result.
