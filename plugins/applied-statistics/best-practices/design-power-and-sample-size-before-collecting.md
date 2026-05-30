# Compute power and sample size before collecting data, not after

**Status:** Absolute rule
**Domain:** Experiment design / power analysis
**Applies to:** `applied-statistics`

---

## Why this exists

Sample size is a design decision, not an analysis decision. If you collect first and size later, two failure modes are guaranteed: an **underpowered** study that returns a non-significant result you then misread as "no effect" (pitfall #8), or an **overpowered** study that flags a trivially-small effect as "highly significant" (pitfall #6). Both are artifacts of n, not findings about the world. A power analysis run *before* launch turns the four quantities — α, power, effect size (MDE), and n — into a deliberate trade you make with the stakeholder, instead of an accident you discover afterward. It is also the structural precondition for the fixed-horizon discipline: you cannot "collect until n is reached and not peek" if you never computed n.

## How to apply

Fix three of {α, power, MDE, n} and solve for the fourth — almost always solving for **n** before launch. Anchor the MDE to a business-meaningful effect, not a convention:

```
# Design-time: n from α / power / MDE  (Tier-1: pingouin)
from pingouin import power_ttest
# α = 0.05, power = 0.80 (conventions); MDE expressed as Cohen's d
n_per_group = power_ttest(d=0.30, power=0.80, alpha=0.05, contrast='two-samples')
#   -> if no pilot SD exists, anchor d with Cohen's small/medium/large = 0.2/0.5/0.8
#      [rule of thumb — prefer a business-meaningful MDE over the convention]

# Post-hoc INVERSION (the honest reading of a null on a fixed n):
power = power_ttest(d=0.30, n=n_observed, alpha=0.05, contrast='two-samples')
#   -> report the MDE this n could actually detect, NOT "no effect"
```

**Do:**
- Run the power analysis at design time and write n into the pre-registered plan and the experiment-design doc.
- Anchor the MDE to the smallest effect worth acting on for the business; use Cohen's conventions only as a fallback (and label them a rule of thumb).
- For a non-significant result, invert the calculation and report the **MDE the design could detect** plus the effect's CI.

**Don't:**
- Run a *post-hoc "observed-power"* calculation that plugs the observed effect back in to justify a null — it is circular and adds nothing the CI doesn't already say.
- Treat α=0.05 / power=0.80 as laws; they are conventions — state them and adjust when the cost of a false positive vs. false negative argues for it.
- Size on a vanity metric when the decision hinges on a different primary metric.

## Edge cases / when the rule does NOT apply

- **Proportion / count / survival outcomes** use their own power formulas (`statsmodels` `NormalIndPower`, `GofChisquarePower`, or simulation), not the t-test formula above.
- **Fixed-budget studies** (you get the n you get — all of last quarter's users) can't choose n; there, size the *MDE you can detect* up front and decide whether that MDE is decision-useful before running.
- **Sequential / always-valid designs** replace a single fixed n with a stopping rule, but still require an up-front design choice — see [`../knowledge/experiment-design-and-ab-testing.md`](../knowledge/experiment-design-and-ab-testing.md).

## See also

- [`../knowledge/experiment-design-and-ab-testing.md`](../knowledge/experiment-design-and-ab-testing.md) — the settled spine (one primary metric, guardrails, n from power+MDE).
- [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) — pitfall #8 (underpowered null) and #6 (significance ≠ effect).
- [`./effect-size-and-ci-not-bare-p.md`](./effect-size-and-ci-not-bare-p.md) — the CI+MDE you report when a null comes back.
- [`../skills/power-and-sample-size/SKILL.md`](../skills/power-and-sample-size/SKILL.md) — the sizing workhorse.

## Provenance

Codifies the "sample size from power + MDE" step of the settled spine in [`../knowledge/experiment-design-and-ab-testing.md`](../knowledge/experiment-design-and-ab-testing.md) and pitfall #8 in [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) (both last reviewed 2026-05-26; Tier 1 / consensus). α/power conventions and Cohen's d anchors per the experiment-design knowledge doc's cited sources (Meera/Univ. Michigan; PMC6736231).

---

_Last reviewed: 2026-05-30 by `claude`_
