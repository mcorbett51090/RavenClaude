# applied-statistics

> The **applied-statistician** for Claude Code — the "statistician in the room" for SMB consulting work. Answers the question your dashboard and pipeline tools can't: **"is this difference / trend / relationship statistically REAL?"**

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "Which test should I use to compare these groups?" | The test (via a decision tree) + assumption checks + the nonparametric fallback + a short runnable snippet |
| "How big a sample do I need?" | n from α / power / MDE — before you launch |
| "Is this A/B winner real?" | Effect size + CI, guardrail check, multiplicity correction, and a ship / hold / inconclusive verdict |
| "Revenue is up 18% on the dashboard — is that real?" | Signal-vs-noise verdict + the uncertainty band to annotate the widget |
| "What drives this outcome? / forecast it" | Model choice + assumption checks + honest intervals + a leakage / overfitting / causation screen |

**Two rules it never breaks:** *method before library*, and *always report effect size + confidence interval, not just a p-value.*

## What's inside

- **1 agent** — `applied-statistician` (advisory; recommends methods + emits snippets you run locally on your data).
- **5 skills** — `choose-statistical-test`, `power-and-sample-size`, `experiment-analysis`, `statistical-qa-of-metrics`, `regression-and-forecasting-review`.
- **5 knowledge files** — a Mermaid test-selection decision tree, a 9-item pitfalls guardrail, experiment-design best practice, 2026 tooling tiers, and a causal-inference primer.
- **1 advisory hook** — `flag-statistical-smells.sh` (p-value-with-no-effect-size, uncorrected multiple comparisons, unchecked parametric assumptions, correlation→causation language).
- **4 templates** — analysis plan (pre-registration), experiment design doc, power-analysis worksheet, statistical report.

## How it seams with `data-platform`

```
data-platform        →  "is this number CORRECT?"   (present, in-range, reconciled, fresh)
applied-statistics   →  "is this number REAL?"       (significant, powered, not an artifact)
```

`data-platform/dashboard-builder` invokes this plugin's `statistical-qa-of-metrics` skill when a widget shows a comparison or trend that needs a significance/CI annotation.

## Tooling stance

Python-first. **Tier 1:** `scipy.stats`, `statsmodels`, `pingouin` (+ bootstrapping). **Tier 2** (reach for with a reason): `PyMC` / `bambi` (Bayesian), `linearmodels` (panel/IV). R is supported-but-contextual. Versions carry retrieval dates — re-verify before pinning in a client deliverable.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install applied-statistics@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
