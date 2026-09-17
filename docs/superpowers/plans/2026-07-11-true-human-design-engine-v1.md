# True Human Design Engine v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and run a first-principles Human Design calculation core that produces a complete audit ledger and a private anchor result without consulting the expected Type during calculation.

**Architecture:** Add a focused `true_human_design` package that separates ephemeris calculations, mandala mapping, bodygraph topology, and chart assembly. Tests exercise invariants and known legacy failure modes before any public API integration. The private anchor record is passed at runtime and never committed.

**Tech Stack:** Python 3.12, `pyswisseph==2.10.3.2`, standard-library `zoneinfo`, `unittest`.

## Global Constraints

- No random or synthetic astronomical fallback.
- No fixed 88-day subtraction; solve an 88-degree solar arc.
- No sequential gate numbering.
- Type derives from defined-channel topology, never gate count.
- Profile derives from Personality and Design Sun lines.
- Exact private anchor data must not be committed.
- Every derived field includes a trace or source version.
- Human Design remains labeled symbolic and non-empirical.

---

### Task 1: Mandala and topology primitives

**Files:**
- Create: `src/true_human_design/__init__.py`
- Create: `src/true_human_design/constants.py`
- Create: `src/true_human_design/mandala.py`
- Create: `src/true_human_design/topology.py`
- Test: `tests/test_true_human_design_core.py`

**Interfaces:**
- Produces: `map_longitude(longitude: float) -> GateActivation`
- Produces: `build_topology(gates: set[int]) -> TopologyResult`
- Produces: `resolve_type(topology: TopologyResult) -> Resolution`
- Produces: `resolve_authority(topology: TopologyResult) -> Resolution`

- [ ] Write failing tests proving 64 contiguous gate spans cover 360 degrees, boundary mapping is deterministic, one gate cannot define a center, complete channels define both centers, and Type cannot be inferred from gate count.
- [ ] Run `python3 tests/test_true_human_design_core.py` and verify failure because the package does not exist.
- [ ] Implement the versioned mandala sequence, center table, channel table, topology graph, Type resolver, and Authority resolver.
- [ ] Run the core test file and verify all tests pass.
- [ ] Commit the task.

### Task 2: Astronomical kernel and exact Design solver

**Files:**
- Create: `src/true_human_design/astronomy.py`
- Extend: `tests/test_true_human_design_core.py`

**Interfaces:**
- Produces: `civil_to_julian_day(...) -> TimeLedger`
- Produces: `planetary_positions(jd_ut: float, node_mode: str = "true") -> dict[str, PlanetPosition]`
- Produces: `solve_design_jd(personality_jd: float, target_arc: float = 88.0) -> DesignSolveResult`

- [ ] Write failing tests for Earth opposition, no fallback when Swiss Ephemeris is missing, solver residual below `1e-6` degrees, and solved Design time differing from a fixed 88-day subtraction.
- [ ] Run the focused tests and verify the expected failures.
- [ ] Implement UTC conversion, Swiss Ephemeris positions, Earth/South Node opposition, and a bracketed bisection solver over 70–110 days before birth.
- [ ] Run focused and core tests and verify all pass.
- [ ] Commit the task.

### Task 3: Chart assembly and audit ledger

**Files:**
- Create: `src/true_human_design/engine.py`
- Create: `tests/test_true_human_design_engine.py`

**Interfaces:**
- Produces: `calculate_chart(record: BirthRecord, *, expected_result: dict | None = None) -> dict`
- Output contains `calculated`, `topology`, `resolutions`, `ledger`, `expected_result`, and `comparison`.

- [ ] Write failing tests proving expected Type cannot affect calculated Type, Profile equals Personality/Design Sun lines, every resolution includes reasons, and private input is not copied into public output by default.
- [ ] Run the engine tests and verify failure because the engine is absent.
- [ ] Implement chart assembly, activation ledgers, channel/center traces, Type, Authority, Definition, Profile, four-gate cross signature, and expected-result comparison.
- [ ] Run all new tests and verify they pass.
- [ ] Commit the task.

### Task 4: Mutation guards and CI integration

**Files:**
- Create: `tests/test_true_human_design_mutations.py`
- Modify: `.github/workflows/fly-deploy.yml`

**Interfaces:**
- Produces: regression tests that fail for sequential gates, fixed 88 days, gate-count Type, hardcoded centers, one-sided channels, and modulo Profile.

- [ ] Write the mutation tests against deliberately incorrect local helper functions.
- [ ] Run the mutation suite and verify every mutation is detected.
- [ ] Add the three new test files to the GitHub Actions test step.
- [ ] Run the full repository suite through GitHub Actions.
- [ ] Commit the task.

### Task 5: Private anchor run

**Files:**
- Create locally only: `.private/anchor.json` (gitignored; never committed)
- Create: `scripts/run_true_human_design.py`
- Create: `docs/validation/true-human-design-anchor-run-template.md`

**Interfaces:**
- CLI: `python3 scripts/run_true_human_design.py --input /private/path/anchor.json --output /private/path/result.json`

- [ ] Add a CLI test using a synthetic fixture.
- [ ] Implement the CLI without logging raw private input.
- [ ] Run the engine privately with the anchor birth record.
- [ ] Freeze the pre-interpretation ledger hash.
- [ ] Compare calculated Type/Profile/Authority against the separately stored expected result.
- [ ] Report exact agreements, disagreements, residuals, and unresolved assumptions without tuning rules.
- [ ] Commit only the CLI and redacted template; do not commit the anchor fixture or result.
