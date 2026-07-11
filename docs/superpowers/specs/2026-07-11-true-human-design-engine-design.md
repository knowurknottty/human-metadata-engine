# True Human Design Engine — Design Specification

**Date:** 2026-07-11
**Status:** Design approved in principle
**Branch:** `design/true-human-design-engine`

## 1. Purpose

Build a first-principles Human Design calculation engine whose rules are transparent, versioned, reproducible, and falsifiable.

The engine must not treat consensus, institutional authority, commercial calculators, or inherited doctrine as automatic truth. Each rule begins as a hypothesis with provenance. It remains active only while it survives explicit attempts to disprove it.

In the product name **True Human Design**, “true” means truth-seeking by transparent calculation, adversarial validation, and correction when disproven. It does not mean infallible, final, or exempt from challenge.

The product goal is not merely to reproduce existing Human Design software. It is to separate:

1. astronomical calculation,
2. mandala mapping,
3. bodygraph topology,
4. traditional interpretation,
5. user research and proposed corrections,
6. Inversion interpretation,
7. empirical status.

This separation permits exact reproduction where the underlying mechanics are sound and principled correction where they are not.

## 2. Governing Constitution

### 2.1 Authority is evidence, not sovereignty

A source may contribute evidence, definitions, historical context, test vectors, or a competing rule. No source is accepted solely because it is canonical, popular, credentialed, old, or commercially dominant.

### 2.2 The user model is the active hypothesis

The user's researched model is represented explicitly as a versioned hypothesis set. It is not silently converted into established fact.

A hypothesis remains active when:

- its inputs and transformation are fully specified;
- it is internally coherent;
- it survives known counterexamples;
- no competing rule explains the evidence better with fewer unsupported assumptions.

### 2.3 Prove-me-wrong protocol

Every promoted rule must include:

- precise claim;
- source and author;
- required inputs;
- deterministic transformation;
- expected outputs;
- known edge cases;
- falsification conditions;
- test cases attempted;
- contradictions found;
- current status.

Rule statuses:

- `proposed`
- `under_test`
- `survives_current_tests`
- `provisionally_adopted`
- `superseded`
- `falsified`
- `underdetermined`

No rule is marked `true`. The strongest status is `provisionally_adopted`.

### 2.4 Contradiction handling

Contradictions are retained, not erased. When two rules disagree, the engine must expose:

- the exact divergent step;
- both outputs;
- the input conditions producing divergence;
- comparative evidence;
- whether the disagreement is astronomical, geometric, topological, interpretive, or terminological.

### 2.5 No black-box dependency

External calculators may supply comparison vectors, but they may not define truth. A result that cannot be traced to inspectable arithmetic remains comparison evidence only.

Two calculators count as independent evidence only when their code paths, source tables, or underlying services are demonstrably independent. Multiple interfaces backed by the same library, API, copied table, or upstream calculator count as one lineage of evidence.

## 3. Scope

### 3.1 Version 1 calculation scope

The first validated engine will calculate:

- UTC birth instant from local date, time, timezone, and location provenance;
- tropical ecliptic longitudes;
- Personality planetary activations;
- exact Design timestamp by solar-arc root solving;
- Design planetary activations;
- gate and line;
- optional color, tone, and base when their mapping rules are separately validated;
- complete channels;
- defined centers;
- bodygraph connected components;
- Type;
- Strategy;
- Authority;
- Definition;
- Profile;
- four Sun/Earth gates used by Incarnation Cross;
- an auditable calculation ledger.

### 3.2 Explicitly deferred

The following are excluded until their rules are independently specified and tested:

- Variable interpretation;
- dietary or medical guidance;
- relationship compatibility claims;
- prediction;
- psychological diagnosis;
- transit forecasting;
- Gene Keys interpretation;
- any claim of empirical personality validity.

## 4. Architecture

### 4.1 Astronomical kernel

Responsibilities:

- normalize civil birth data to UTC;
- calculate Julian day;
- compute geocentric tropical longitudes using a pinned Swiss Ephemeris version;
- compute Earth as exact opposition to the Sun;
- calculate lunar-node convention explicitly;
- preserve raw precision;
- expose ephemeris flags and errors;
- solve the Design instant when the Design Sun is approximately 88 degrees of solar arc behind the Personality Sun.

The active compatibility hypothesis defines the Design instant as the earlier root nearest roughly 88 solar days before birth for which:

```text
(Personality Sun longitude − Design Sun longitude) mod 360° = 88.0°
```

The arc target, direction, search window, and numerical tolerance are versioned rule parameters. The timestamp must be found by numerical root solving, not by subtracting a fixed number of days.

Output contract per body:

```json
{
  "body": "Sun",
  "julian_day": 0.0,
  "longitude": 0.0,
  "latitude": 0.0,
  "distance": 0.0,
  "speed_longitude": 0.0,
  "retrograde": false,
  "ephemeris_version": "",
  "calculation_flags": []
}
```

### 4.2 Mandala mapper

Responsibilities:

- store a versioned 360-degree gate sequence;
- map longitude to gate and fractional gate position;
- derive line from the fractional position;
- later derive color, tone, and base from separately validated subdivisions;
- report angular distance from every relevant boundary.

The mapper must never assign gates sequentially from `1` through `64` unless that exact sequence is itself the active, tested mapping.

Output contract:

```json
{
  "longitude": 0.0,
  "gate": 0,
  "line": 0,
  "fraction_within_gate": 0.0,
  "distance_to_previous_boundary": 0.0,
  "distance_to_next_boundary": 0.0,
  "mapping_version": ""
}
```

### 4.3 Activation assembler

Responsibilities:

- combine astronomical positions with mandala results;
- keep Personality and Design activations distinct;
- preserve duplicate activations rather than collapsing provenance;
- produce the unique activated-gate set only as a derived view.

### 4.4 Bodygraph topology engine

This module is pure graph logic and has no astronomical responsibilities.

Inputs:

- activated gates;
- versioned channel table;
- gate-to-center table;
- motor-center definitions;
- authority hierarchy version.

Outputs:

- complete channels;
- defined centers;
- adjacency graph;
- connected components;
- motor-to-Throat paths;
- Sacral state;
- Solar Plexus state;
- Splenic state;
- Ego state;
- G-to-Throat state;
- Head/Ajna-to-Throat state.

All topology decisions must include a trace explaining which gates and channels caused the result.

### 4.5 Type resolver

Type is derived from bodygraph topology, never from activation count.

The initial compatibility resolver evaluates, in this explicit order:

1. no defined centers → Reflector;
2. defined Sacral plus a defined path from any motor center to the Throat → Manifesting Generator;
3. defined Sacral without such a motor-to-Throat path → Generator;
4. undefined Sacral plus a defined path from a motor center to the Throat → Manifestor;
5. otherwise → Projector.

The active motor-center set is versioned with the rule. This ordering is itself a hypothesis subject to the prove-me-wrong protocol.

### 4.6 Authority resolver

Authority is resolved through an explicit hierarchy. Each candidate authority must specify the topology condition that activates it.

Initial compatibility hierarchy:

1. Solar Plexus / Emotional;
2. Sacral;
3. Splenic;
4. Ego Manifested;
5. Ego Projected;
6. Self-Projected;
7. Environmental / Mental;
8. Lunar.

The engine must expose both the selected authority and every rejected candidate with reasons.

### 4.7 Definition resolver

Definition is determined from connected components of defined centers, not from gate count.

Outputs include:

- component count;
- centers in each component;
- bridging gates and channels;
- resulting label;
- topology trace.

### 4.8 Profile resolver

Profile is derived from:

- Personality Sun line;
- Design Sun line.

No modulo arithmetic over gate numbers is permitted.

### 4.9 Incarnation Cross resolver

The resolver stores the exact four gates:

- Personality Sun;
- Personality Earth;
- Design Sun;
- Design Earth.

Cross naming remains unavailable until the naming table and angle/profile rules are independently sourced, encoded, and tested. The engine may return the four-gate cross signature before it returns a traditional name.

### 4.10 Interpretation layers

Interpretation is downstream from calculation.

Required layers:

- `calculated_facts`
- `traditional_interpretation`
- `user_research_interpretation`
- `inversion_interpretation`
- `empirical_status`

A change in interpretation must never alter the calculated chart.

## 5. Rule Registry

Every nontrivial rule is represented as data.

```json
{
  "rule_id": "hd.type.v1",
  "claim": "Type is determined from Sacral definition and motor-to-Throat connectivity.",
  "status": "under_test",
  "provenance": [],
  "algorithm_version": "1.0.0",
  "parameters": {},
  "falsification_conditions": [],
  "test_vectors": [],
  "counterexamples": [],
  "supersedes": null,
  "notes": ""
}
```

The registry must support competing active hypotheses. Comparison runs can execute the same chart through multiple rule sets and produce a structured diff.

## 6. Validation Strategy

### 6.1 Mathematical invariants

Examples:

- every longitude maps to exactly one gate except an explicitly represented boundary ambiguity;
- all 64 gate spans cover exactly 360 degrees without overlap or gap;
- each complete channel defines its two endpoint centers;
- an incomplete channel cannot define a center by itself;
- Earth is 180 degrees opposite the Sun within numerical tolerance;
- the Design solver reaches the configured solar-arc tolerance;
- Profile lines are always in the range 1–6;
- Type resolution is deterministic for the same topology.

### 6.2 Boundary tests

Test exact and near-boundary positions for:

- gate changes;
- line changes;
- color, tone, and base changes when enabled;
- UTC date rollover;
- daylight-saving transitions;
- historical timezone offsets;
- retrograde stations;
- lunar-node convention changes.

### 6.3 Golden vectors

Golden vectors must include:

- charts with independently verified astronomical longitudes;
- charts near gate and line boundaries;
- examples for every Type;
- examples for every Authority;
- examples for every Definition class;
- examples with duplicate gate activations;
- examples that force disagreement among external calculators.

External calculators are recorded by name, version/date, exact output, implementation lineage when known, and any inaccessible assumptions. Agreement may raise confidence only after dependency between calculators has been assessed. Disagreement triggers investigation rather than majority voting.

### 6.4 Mutation and adversarial testing

The test suite deliberately introduces plausible mistakes:

- fixed 88-day subtraction;
- sequential gate numbering;
- mean-node/true-node substitution;
- local-time treated as UTC;
- missing Earth opposition;
- one-sided channel activation;
- hardcoded center definition;
- Type derived from gate count;
- Profile derived by modulo.

Each mutation must be caught by at least one test.

### 6.5 Challenge ledger

Every challenge records:

```json
{
  "challenge_id": "",
  "target_rule": "",
  "challenger": "",
  "counterclaim": "",
  "evidence": [],
  "reproduction_steps": [],
  "result": "open|survived|partially_survived|falsified|underdetermined",
  "decision": "",
  "timestamp": ""
}
```

Challenges are permanent audit records, including failed attempts to disprove a rule.

## 7. Confidence and Uncertainty

The engine reports separate confidence dimensions:

- input confidence;
- astronomical confidence;
- mapping confidence;
- topology confidence;
- rule confidence;
- interpretation confidence.

These must never be collapsed into one global truth score.

Birth-time uncertainty is propagated by recomputing a time window and reporting which outputs remain stable versus which cross a boundary.

## 8. Data Flow

```text
Civil birth record
    ↓
Timezone and UTC normalization
    ↓
Astronomical kernel
    ↓
Design solar-arc solver
    ↓
Mandala mapper
    ↓
Personality + Design activations
    ↓
Bodygraph topology
    ↓
Type / Authority / Definition / Profile / Cross signature
    ↓
Validation ledger and confidence report
    ↓
Traditional, research, and Inversion interpretations
```

## 9. Error Handling

The engine fails closed.

Examples:

- unknown timezone history → chart unavailable unless the user explicitly supplies an offset and accepts reduced confidence;
- missing ephemeris dependency → no synthetic or random planetary positions;
- unresolved mapping boundary → return ambiguity, not an arbitrary side;
- incomplete rule registry → return calculated primitives while withholding derived labels;
- failed Design root solve → no Design activations;
- inconsistent channel table → validation error at startup.

Random fallback positions are forbidden.

## 10. Public Output

Every chart response includes:

- normalized input;
- UTC conversion ledger;
- Personality and Design timestamps;
- planetary longitudes;
- mandala mapping for each activation;
- channel and center derivation;
- Type trace;
- Authority trace;
- Definition components;
- Profile derivation;
- four-gate cross signature;
- rule-set version;
- unresolved disputes;
- challenge history relevant to active rules;
- interpretation layers;
- explicit symbolic-status notice.

The user must be able to answer “why did the engine produce this?” without reading source code.

## 11. Release Gates

A release called **True Human Design** requires all of the following:

1. no random or synthetic calculation fallback;
2. exact Design timestamp solver;
3. complete versioned mandala table;
4. complete channel and center topology table;
5. deterministic Type, Authority, Definition, and Profile traces;
6. passing invariant and boundary suites;
7. mutation suite catches every known legacy failure mode;
8. a documented comparison set against multiple implementation lineages;
9. every disagreement classified and unresolved disagreements surfaced;
10. no output represented as empirical psychology;
11. complete calculation ledger;
12. active rules have survived the documented prove-me-wrong process.

## 12. Migration from the Legacy Calculator

The legacy calculator remains disabled.

It may contribute only:

- output-field inventory;
- test cases demonstrating failure modes;
- compatibility fixtures.

The following legacy behaviors are explicitly prohibited:

- sequential gate numbering;
- fixed 88-day Design timestamp;
- gate-count Type;
- hardcoded centers;
- modulo Profile;
- gate-count Definition;
- random fallback ephemerides.

No legacy result is grandfathered into the new engine.

## 13. Success Criteria

The design succeeds when:

- two independent implementations using the same active rule set produce identical ledgers within declared numerical tolerances;
- every derived label is traceable to primitive calculations and versioned rules;
- a challenger can submit a counterexample and reproduce the decision process;
- a rule can be superseded without rewriting historical charts;
- the engine can say “underdetermined” without pressure to fabricate certainty;
- the Inversion interpretation can evolve without corrupting the calculation core.
