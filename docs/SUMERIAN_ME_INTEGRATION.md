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

`src/sumerian_me_reflection.py` implements `sumerian-me-reflection-v1`. It is disabled by default and becomes available only when the request explicitly sets `sumerian_me_reflection: true` and supplies observations with user-selected `capacity_domains`.

The mapper does not classify observation prose. It aggregates only explicit tags, records observation references/source/confidence without copying raw prose into the reflection object, and exposes the corresponding modern category/crosswalk plus the historical corpus items grouped under that category.

Forbidden automatic bases include name, birth data, numerology, astrology, Human Design, and symbolic resonance scores. None establishes that a modern person possesses or corresponds to a particular *me*.

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

## Public UI contract

The v1.0 Optional context form exposes **Human Capacity / 𒈨 Reflection** as an explicit checkbox. Each reflection observation has text/source/confidence fields plus the nine modern Human Metadata categories. The user must deliberately choose the categories; the browser and server do not infer them from the observation sentence.

The result renders three visible steps: **Personal evidence → Modern analytical bridge → Historical corpus**. Category matches are expandable and show the modern capacity crosswalk separately from the historical *me* items. The interface never displays a *me* score, rank, destiny claim, or automatic assignment.

Automated frontend/API contracts cover opt-in behavior, validation, redaction, and the no-score boundary. Because the form/result layout is new, existing v1.0 screenshot/physical-device evidence does not by itself verify this surface; refreshed browser/device QA remains a release gate.
