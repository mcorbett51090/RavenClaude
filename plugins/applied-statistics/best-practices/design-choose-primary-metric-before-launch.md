# Declare exactly one primary metric before the experiment launches — no post-hoc primaries

**Status:** Absolute rule
**Domain:** Experiment design / A/B testing
**Applies to:** `applied-statistics`

---

## Why this exists

An experiment that starts with five "equally important" outcomes and reports whichever one came out significant has not found a result — it has found noise. The primary metric is the single number that determines whether the experiment is a win or a loss, agreed upon before launch, before any data is seen. Secondary metrics (guardrail metrics, supportive indicators) are fine and useful, but they are not the decision criterion. Selecting the primary metric after seeing the data is the operational definition of p-hacking, and it is invisible to anyone reading the final report.

## How to apply

In the `experiment-design-doc.md`, fill this field before the feature is launched:

```markdown
## Primary metric (required, exactly one)

**Metric:** 7-day activation rate
**Definition:** % of new users who complete the core activation event within 7 days of sign-up.
**Direction:** higher is better
**MDE (minimum detectable effect):** 5 percentage point lift (from 30% baseline)
**Why this is the primary:** This is the leading indicator of long-term retention per [internal analysis].
  A secondary revenue metric would take 8 weeks to observe; activation is measurable in 2 weeks.

## Secondary / guardrail metrics
- Churn-7 rate (guardrail — must not increase by more than 1 pp)
- Day-1 return rate (supportive — expected to move with activation; not the decision criterion)
```

**If the primary metric is changed after launch:** document the change explicitly in the design doc with a timestamp and a reason. Any report that uses a post-launch-changed primary is labeled a "directional / exploratory" result, not a confirmatory one.

**Do:**
- Name the primary metric in the design doc before ANY data is collected.
- Get stakeholder sign-off on the primary metric definition before launch.
- Analyze secondary metrics after the primary metric decision is made — not before.

**Don't:**
- Launch with a list of outcomes and decide which is "primary" after seeing the data.
- Retroactively reframe a secondary metric as the primary because it moved significantly.
- Change the primary metric mid-experiment without a new pre-registration and a reasoning audit trail.

## Edge cases / when the rule does NOT apply

- Pure exploratory experiments (designed explicitly to measure many things to decide what to measure in a future confirmatory experiment) are exempt, but must be labeled "exploratory" in all reports and outputs.

## See also

- [`../agents/applied-statistician.md`](../agents/applied-statistician.md) — enforces pre-registration discipline
- [`./design-pre-register-to-avoid-p-hacking.md`](./design-pre-register-to-avoid-p-hacking.md) — the pre-registration rule this specializes

## Provenance

Standard pre-registration discipline in confirmatory research. Codifies applied-statistics CLAUDE.md §3 house opinion #5 ("Pre-register the analysis plan. Metric, test, stopping rule, segments — written before seeing data. The cheapest defense against p-hacking") at the single-primary-metric level.

---

_Last reviewed: 2026-06-05 by `claude`_
