# Interpret a null result with the study's power and MDE — not as "no effect"

**Status:** Absolute rule
**Domain:** Hypothesis testing / null results
**Applies to:** `applied-statistics`

---

## Why this exists

"We ran the test and it wasn't significant" is one of the most misinterpreted sentences in business analytics. A null result from an underpowered study does not mean there is no effect — it means the study was too small to detect effects below the minimum detectable effect (MDE). A study powered to detect a 10% lift at 80% power will fail to detect a 3% lift — which may still be economically meaningful. Presenting a null result without the power analysis and the MDE is presenting an uninformative result as if it were evidence of absence.

## How to apply

In every null-result report, add a "What we could have detected" section:

```python
from statsmodels.stats.power import TTestIndPower

analysis = TTestIndPower()

# Given: n=500 per group, alpha=0.05, two-tailed
# What was the minimum detectable effect?
power_at_small_effect = analysis.solve_power(
    effect_size=0.2,   # Cohen's d = 0.2 (small)
    nobs1=500,
    alpha=0.05,
    alternative='two-sided'
)
print(f"Power to detect d=0.2 (small effect): {power_at_small_effect:.2f}")

mde = analysis.solve_power(
    nobs1=500,
    power=0.80,
    alpha=0.05,
    alternative='two-sided'
)
print(f"MDE (80% power, n=500 per group): Cohen's d = {mde:.3f}")
```

**Null result report template:**

```markdown
## Result: Not statistically significant

**Test:** Welch's t-test, two-sided, alpha=0.05
**Result:** p=0.34, 95% CI for the mean difference: [-2.1, 6.2]
**Effect observed:** mean difference = 2.1 (small, not significant)

## What we can conclude

This study was powered to detect a mean difference of 5.8 or larger
(Cohen's d >= 0.41) with 80% power (n=150 per group).

The observed difference of 2.1 is consistent with both "no effect" and
"a real effect smaller than our MDE." We cannot conclude there is no effect.

**Recommendation:** If a difference of 2.1 is operationally meaningful,
run a larger study (n=700 per group needed to detect d=0.20 at 80% power).
If 2.1 is too small to matter, this null result is informative.
```

**Do:**
- Always report the MDE and the observed CI alongside every null result.
- Ask the business question: "Is an effect smaller than the MDE economically meaningful?"
- Present the null result as "inconclusive" rather than "no effect" when the study is underpowered.

**Don't:**
- Report "the test wasn't significant" without the power and MDE context.
- Use a null result from an underpowered study to justify NOT making a change.
- Accept "we ran the test and it's not significant" as a complete answer without checking the power.

## Edge cases / when the rule does NOT apply

- A well-powered study (80%+ power at the pre-specified MDE) that returns a null result is informative evidence of absence for effects above the MDE. State this clearly: "The study had 82% power to detect d=0.30; the null result is evidence that any true effect is smaller than 0.30."

## See also

- [`../agents/applied-statistician.md`](../agents/applied-statistician.md) — drives the power-and-sample-size skill
- [`./design-power-and-sample-size-before-collecting.md`](./design-power-and-sample-size-before-collecting.md) — the pre-collection power rule that makes null results interpretable

## Provenance

Codifies applied-statistics CLAUDE.md §3 house opinion #6 ("An underpowered null is not 'no effect.' Report the CI and the MDE the study could detect") and §4 anti-patterns ("Reporting a null result from an underpowered study as 'no effect'").

---

_Last reviewed: 2026-06-05 by `claude`_
