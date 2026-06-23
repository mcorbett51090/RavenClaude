# Convergence rubric library

> Library version: **1.0.0** — the externalized, versioned rubric SPINE for the
> Convergence Engine (`refine-to-rubric`). This file is the **anti-reward-hack**
> boundary: rubrics are retrieved from here, not invented at runtime by a model.
> A model may _additively_ propose "commonly-missed" dimensions, but those are
> marked `[unverified — derived]` and are NEVER auto-graded — they are surfaced
> to the human. The deterministic `terminate()` predicate (in `converge.py`)
> lives entirely outside any model and caps how hard any single dimension is
> optimized (Goodhart guard).

## How a rubric is assembled (`derive-rubric`)

1. **Detect the artifact kind** (agent-file / visual-report / prose / code / data
   / generic). Low-confidence kind → fall back to the **generic** rubric AND pause
   for a design check-in (do not guess kind-specific gates).
2. **Retrieve the kind's dimensions** from the table below. Each dimension is
   `source: library` and `verified: true` (sanctioned for automatic grading).
   Where an **objective signal** exists, bind the dimension to it and set
   `hard_gate: true` — objective gates are evaluated BEFORE any model judge.
3. **Add explicit user requirements** as `source: explicit`, `verified: true`,
   and `weight: <max>` (a stated requirement always outranks a library default).
4. **(Additive, optional) the "commonly-missed" pass** — a model may propose
   dimensions the library + user requirements missed. Each proposed dimension is
   emitted with `source: derived`, `verified: false`, and
   `provenance: "[unverified — derived]"`. `weighted_score()` and `terminate()`
   ignore unverified dimensions for the verdict; they appear only in
   `residual_gaps` for human review. A human promotes a derived dimension to
   `verified: true` by editing the rubric — never the model silently.
5. **`agent-file` is delegated**, not reimplemented: route to the existing
   `agent-quality-rubric` skill (6 anchored dimensions) and translate its scores
   into the scorecard. See the agent-file row.

Weights are relative (the engine normalizes). "Weight-max" for explicit
requirements means: at least the largest library weight for that kind.

## Objective-signal vocabulary

A dimension's `objective_signal` names the deterministic evaluator that produces
its score (reused from the marketplace — never duplicated). These are wired in
P2 (`evaluate`); P1 only records the binding.

| signal token | evaluator | produces |
| --- | --- | --- |
| `driver.py` | `skills/visual-feedback-loop/driver.py` | merged visual pass/fail (layout + console + lighthouse) |
| `svg-report-lint` | `skills/svg-report-lint` | SVG geometry + security verdict |
| `declarative-viz` | `skills/declarative-visualization` linter | Vega-Lite/Vega spec safety verdict |
| `pbir` | `skills/pbir-layout-engine/lint.py` | PBIR layout verdict |
| `dod-cmd` | the project's `dod-gate.sh` command | definition-of-done pass/fail |
| `lint-cmd` | a project-provided lint/test command | exit-coded pass/fail |
| _(empty)_ | — | judged by the cross-model judge AFTER objective gates pass |

## Rubric dimensions by artifact kind

### generic (fallback — also the low-confidence-kind default)

| id | title | weight | hard_gate | objective_signal |
| --- | --- | --- | --- | --- |
| `requirements-met` | Stated requirements are all addressed | 40 | no | _(judge)_ |
| `internally-consistent` | No internal contradictions | 25 | no | _(judge)_ |
| `lints-clean` | Project lint/test command passes | 20 | **yes** | `lint-cmd` |
| `scoped` | No scope creep beyond the ask | 15 | no | _(judge)_ |

### code

| id | title | weight | hard_gate | objective_signal |
| --- | --- | --- | --- | --- |
| `tests-pass` | The test/lint command is green | 35 | **yes** | `lint-cmd` |
| `correctness` | Logic matches the stated behavior | 30 | no | _(judge)_ |
| `no-regression` | No new failures vs the prior iteration | 20 | **yes** | `dod-cmd` |
| `readable` | Clear naming + structure, no dead code | 15 | no | _(judge)_ |

### visual-report

| id | title | weight | hard_gate | objective_signal |
| --- | --- | --- | --- | --- |
| `layout-valid` | Layout/console/lighthouse merged pass | 35 | **yes** | `driver.py` |
| `spec-safe` | Viz spec passes the security linter | 20 | **yes** | `declarative-viz` |
| `data-faithful` | Chart represents the data without distortion | 25 | no | _(judge)_ |
| `legible` | Labels, contrast, hierarchy are clear | 20 | no | _(judge)_ |

### prose

| id | title | weight | hard_gate | objective_signal |
| --- | --- | --- | --- | --- |
| `answers-the-ask` | Directly answers the stated question | 40 | no | _(judge)_ |
| `claim-grounded` | Consequential claims cite a source or are marked unverified | 25 | no | _(judge)_ |
| `no-overclaim` | No "perfect"/absolute claims; honest residual gaps | 20 | no | _(judge)_ |
| `structured` | Scannable structure (headings/lists where useful) | 15 | no | _(judge)_ |

### data

| id | title | weight | hard_gate | objective_signal |
| --- | --- | --- | --- | --- |
| `schema-valid` | Output validates against its declared schema | 35 | **yes** | `lint-cmd` |
| `complete` | No missing required fields/rows | 30 | no | _(judge)_ |
| `quality-checks` | Data-quality assertions pass | 20 | **yes** | `dod-cmd` |
| `documented` | Fields/units are documented | 15 | no | _(judge)_ |

### agent-file (DELEGATED to `agent-quality-rubric`)

Do NOT reimplement the agent rubric here. Route to the `agent-quality-rubric`
skill and translate its 6 anchored (1–5) dimensions into scorecard dimensions:

| id | source dimension (agent-quality-rubric) | weight |
| --- | --- | --- |
| `mission-clarity` | Dimension 1 — Mission clarity | 20 |
| `scope-sharpness` | Dimension 2 — Scope sharpness | 20 |
| `capability-grounding` | Dimension 3 — Capability Grounding alignment | 20 |
| `output-contract` | Dimension 4 — Output-Contract completeness | 15 |
| `escalation-paths` | Dimension 5 — Escalation paths | 15 |
| `example-scenarios` | Dimension 6 — Example scenarios | 10 |

Each 1–5 anchor maps to a `[0,1]` score as `(anchor - 1) / 4` (so 5 → 1.0,
3 → 0.5, 1 → 0.0). All are `source: library`, `verified: true`. None is a hard
gate (the agent rubric is a judge-style scorecard, not an objective tripwire),
but `check-frontmatter.py` already gates description length + scenario schema as
the objective floor for agent files — bind that as a `lint-cmd` hard gate when an
agent file is the artifact.

## The "commonly-missed" derived-dimension pass (additive only)

When invoked, the model is asked ONLY to propose dimensions the library + user
requirements did not cover — the unknown-unknowns. The prompt is constrained:

- Propose at most a small number of dimensions (default ≤ 3).
- Each MUST be emitted with `source: derived`, `verified: false`,
  `provenance: "[unverified — derived]"`, and a low default `weight`.
- The model MUST NOT restate or re-weight an existing library/explicit dimension
  (additive only — it cannot mutate the spine).
- Output is surfaced to the human in `residual_gaps`; nothing derived is graded
  until a human edits the rubric to set `verified: true`.

This is the only place a model touches the rubric, and it can only ADD candidates
for human review — it can never change what is graded. That is the structural
defense against rubric reward-hacking.
