# Deep-Anchor Validation Protocol

**Date:** 2026-07-11
**Status:** Approved validation requirement
**Applies to:** True Human Design Engine

## 1. Purpose

Use a consented deep-reference subject as an anchor case because the project has unusually rich, longitudinal context for that person:

- a precise private birth record;
- extensive self-report;
- repeated observed behavior across many domains;
- project and authorship history;
- explicit contradictions and revisions;
- a user-reported Human Design result;
- willingness to challenge results rather than protect a preferred answer.

The anchor subject is a high-information reference case, not the definition of Human Design and not the sole basis for any rule.

Representativeness is not required. An atypical or outlier subject can still provide exceptional validation value when the data are deep, longitudinal, internally cross-checkable, and compared against competing hypotheses.

## 2. Privacy Boundary

No identifying birth record, family information, health history, or private narrative corpus is committed to Git.

The repository stores only:

- the validation protocol;
- schemas for consented observations;
- synthetic fixtures;
- hashes of frozen private runs when audit continuity is required.

The exact subject record is supplied through a private runtime fixture outside version control. Public chart exports must not expose the private validation corpus.

The subject may revise or revoke use of any observation. Historical test records may retain an audit marker, but revoked evidence becomes inactive and unavailable to future scoring.

## 3. What the Anchor Can Validate

The anchor can validate four distinct things:

1. **Calculation integrity** — whether the same private birth record produces the same astronomical and bodygraph ledger under the same versioned rules.
2. **Within-person explanatory power** — whether preregistered claims describe repeated behavior across time rather than isolated anecdotes.
3. **Comparative explanatory power** — whether one rule set predicts the subject's holdout observations better than competing rule sets.
4. **Failure visibility** — whether contradictions remain visible instead of being explained away after the fact.

The anchor cannot, by itself, validate:

- population prevalence;
- universal Human Design claims;
- causal biological mechanisms;
- empirical psychological validity;
- generalization to people unlike the anchor.

Those require separate multi-subject testing.

## 4. Source-of-Truth Principle

The source of truth for the anchor run is the subject's actual data and the comparison ledger, not whether the subject resembles an expected group profile.

The engine evaluates:

- exact input data;
- deterministic calculation;
- repeated real-world observations;
- competing explanations;
- prediction on held-out evidence;
- documented attempts to disprove the result.

A subject being unusual does not invalidate the data. It only limits claims about how well the result generalizes to a broader population.

## 5. Anti-Circularity Rules

The engine must not be tuned until it reproduces the subject's reported result merely because that result is expected.

Required safeguards:

1. **Blind calculation first** — calculate astronomical positions, gates, channels, centers, Type, Authority, Definition, and Profile without consulting the expected result.
2. **Freeze the ledger** — preserve the pre-interpretation calculation output by hash.
3. **Separate expectation from result** — store user-reported results outside calculated fields.
4. **No single-subject rule edits** — a rule may not be changed solely to improve fit for the anchor.
5. **Competing-rule execution** — run every plausible rule set against the same frozen primitive activations.
6. **Predeclared criteria** — define what evidence would support or contradict each interpretation before reviewing the narrative corpus.
7. **Holdout evidence** — reserve part of the behavioral record from rule development and use it only after the interpretation is frozen.
8. **Negative controls** — compare the result against alternative Types and generic descriptions.
9. **No adjective matching** — validation must evaluate decisions, timing, energy mechanics, and repeated behavior, not vague personality words.
10. **Mismatch remains visible** — disagreement is logged as a challenge; it is never edited away.

## 6. Evidence Corpus

Behavioral observations use a structured private record:

```json
{
  "observation_id": "",
  "claim_domain": "initiation|response|energy|decision_process|conflict|work_pattern|relationship|creative_output",
  "observation": "",
  "source": "self_report|conversation_record|project_history|external_record",
  "occurred_at": "",
  "recorded_at": "",
  "confidence": 0.0,
  "supports": [],
  "contradicts": [],
  "privacy": "private",
  "active": true
}
```

Observations describe behavior rather than assign a Human Design label.

Good:

> Initiated a new project without an external request, built the first version, then informed collaborators after the structure existed.

Bad:

> Behaved like a Manifestor.

## 7. Initial Validation Domains

### 7.1 Initiation versus response

Evaluate the frequency and conditions under which the subject:

- begins projects without an external prompt;
- waits for an external stimulus;
- experiences momentum before social permission;
- creates a path where no offered path exists;
- abandons or resists externally imposed sequences.

A useful rule must distinguish spontaneous initiation from ordinary human agency and retrospective storytelling.

### 7.2 Informing and resistance

Evaluate whether informing relevant people before action reliably changes friction, obstruction, or relational fallout.

This is tested as a behavioral hypothesis, not assumed because traditional Human Design associates informing with Manifestors.

### 7.3 Energy mechanics

Evaluate longitudinal patterns of:

- sustained repetitive output;
- burst-and-recovery cycles;
- capacity under self-directed versus assigned work;
- completion behavior;
- overload and recovery;
- whether activity creates or depletes usable energy.

Do not infer energy mechanics from project count alone.

### 7.4 Decision process and Authority

The engine derives Authority from topology before interpreting decisions.

Then compare the derived mechanism against documented major decisions:

- time between stimulus and decision;
- emotional-wave effects;
- immediate bodily clarity;
- instinctive threat recognition;
- will and commitment language;
- identity-direction language;
- environmental sounding-board behavior.

No Authority is accepted from a single anecdote.

### 7.5 Signature and not-self themes

Terms such as peace, anger, satisfaction, frustration, success, bitterness, surprise, and disappointment must be operationalized before testing.

For example, “anger” cannot mean any instance of anger. It must describe a repeatable relationship between blocked initiation or control and the resulting state.

### 7.6 Profile

Profile validation focuses on longitudinal learning and social-role patterns, not flattering archetypal descriptions.

The calculation comes from the two Sun lines. Behavioral evidence may evaluate interpretation but may not change those calculated lines.

## 8. Evaluation

The protocol does not produce one global accuracy percentage.

Each claim receives:

- calculation status;
- evidence coverage;
- supporting observations;
- contradicting observations;
- independence assessment;
- alternative explanations;
- result: `supported`, `mixed`, `contradicted`, or `underdetermined`.

A Type-level summary may count supported and contradicted preregistered claims, but it must retain the individual ledger.

## 9. Falsification Conditions

A reported-result hypothesis is weakened when:

- validated topology produces a different result under the active rule set;
- the result depends on an unsupported mandala or channel mapping;
- alternative interpretations predict holdout behavior materially better;
- initiation, response, informing, energy, or decision-process claims do not survive operationalization;
- apparent fit disappears when generic language and retrospective reinterpretation are controlled.

It is strengthened when:

- independent astronomical and mapping implementations produce the same primitive chart;
- topology deterministically produces the reported result;
- preregistered result-specific predictions outperform alternatives on holdout evidence;
- contradictory observations are sparse, explained without special pleading, and remain visible;
- the result survives active attempts by the subject and reviewers to disprove it.

Neither outcome alone validates the full Human Design system.

## 10. Outlier Handling

An anchor may be an outlier in temperament, cognition, life history, productivity, or social behavior.

The engine must therefore distinguish:

- **model failure** — the rule does not explain the anchor's data;
- **interpretation failure** — the calculation may be correct but the inherited description is too coarse or wrong;
- **population mismatch** — the rule may describe a broad tendency but not this subject;
- **true outlier behavior** — the subject exhibits a rare but coherent expression of the same underlying mechanics;
- **insufficient evidence** — the available record cannot discriminate among alternatives.

The label “outlier” is not an excuse. It must be supported by comparison data and cannot be used to rescue a failed rule.

## 11. Multi-Subject Requirement

The anchor may guide development and expose obvious errors, but no interpretive rule is promoted from the anchor case alone.

Before release, the engine requires additional consented subjects representing:

- every Type;
- every Authority;
- multiple Profiles;
- boundary-sensitive birth times;
- people who strongly identify with their conventional chart;
- people who reject it;
- people whose external calculators disagree.

The anchor remains the deepest case, while the broader cohort tests generalization.

## 12. Required Outputs for the Anchor Run

The canonical validation run must publish privately:

1. normalized birth record and timezone provenance;
2. exact Personality timestamp;
3. solved Design timestamp and residual solar-arc error;
4. planetary longitude ledger;
5. gate and line mappings with boundary distances;
6. activated channels and center derivation;
7. Type trace;
8. Authority trace;
9. Definition components;
10. Profile derivation;
11. four-gate cross signature;
12. competing-rule diffs;
13. user-reported result shown separately;
14. preregistered behavioral tests;
15. supporting and contradicting evidence;
16. unresolved challenges;
17. final provisional status.

## 13. Success Condition

The deep-anchor protocol succeeds when the project can state, without circular reasoning:

> Here is the exact chart produced from the private birth record. Here is every rule used. Here is the result before we looked at expectations. Here is where it agrees and disagrees with the subject's reported result and observed life. Here are the strongest attempts to disprove it. Here is what survived, what failed, and what remains unknown.
