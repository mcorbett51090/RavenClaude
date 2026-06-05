# Distinguish practical significance from statistical significance — size matters, not just p

**Status:** Absolute rule
**Domain:** Hypothesis testing / effect size
**Applies to:** `applied-statistics`

---

## Why this exists

At large sample sizes, even negligibly small effects become statistically significant. A conversion rate improvement of 0.04% is "significant" at p<0.001 with n=500,000 per group — but it may represent $200/year in revenue on a $5M product, making it irrelevant to any business decision. Statistical significance tells you the effect is distinguishable from zero. Practical significance (effect size) tells you whether it is large enough to matter to the decision. Every result report must address both questions explicitly; a p-value with no effect size does not constitute a complete answer.

## How to apply

**Report both together, always:**

```python
from scipy import stats
import numpy as np

# Example: conversion rates
control_n, control_conversions = 1000, 200     # 20%
treatment_n, treatment_conversions = 1000, 220  # 22%

# Statistical significance (chi-square or z-test)
from statsmodels.stats.proportion import proportions_ztest
z_stat, p_value = proportions_ztest(
    [treatment_conversions, control_conversions],
    [treatment_n, control_n]
)

# Effect size: absolute lift, relative lift, Cohen's h
abs_lift = treatment_conversions/treatment_n - control_conversions/control_n
rel_lift = abs_lift / (control_conversions/control_n)
cohens_h = 2 * np.arcsin(np.sqrt(treatment_conversions/treatment_n)) - \
           2 * np.arcsin(np.sqrt(control_conversions/control_n))

print(f"p-value: {p_value:.4f}")
print(f"Absolute lift: {abs_lift:.4f} ({abs_lift*100:.2f} pp)")
print(f"Relative lift: {rel_lift:.4f} ({rel_lift*100:.1f}%)")
print(f"Cohen's h: {cohens_h:.4f} ({'small' if abs(cohens_h) < 0.2 else 'medium' if abs(cohens_h) < 0.5 else 'large'})")
```

**Effect size benchmarks (Cohen's conventions):**

| Test type | Small | Medium | Large |
|---|---|---|---|
| Proportions (Cohen's h) | 0.2 | 0.5 | 0.8 |
| Means (Cohen's d) | 0.2 | 0.5 | 0.8 |
| Correlation (r) | 0.1 | 0.3 | 0.5 |
| Chi-square (Cramer's V) | 0.1 | 0.3 | 0.5 |

**Standard report section:**

```markdown
## Result

**Statistical significance:** p=0.031 (significant at alpha=0.05)
**Effect size:** Absolute lift = +2.0 pp; Relative lift = +10%; Cohen's h = 0.05 (small)
**Practical significance:** A 2 pp lift on this funnel step represents approximately $X/month
in additional revenue. [Stakeholder: assess whether this justifies shipping the change.]
```

**Do:**
- Always report effect size alongside every p-value.
- Translate the effect size into business terms (revenue, customer count, time saved).
- Let the stakeholder make the practical-significance judgment — the statistician provides the size.

**Don't:**
- Use "significant" as a synonym for "important."
- Skip the effect size because the p-value is very small.
- Claim an effect is "large" without computing a formal effect size metric.

## Edge cases / when the rule does NOT apply

- Guardrail metrics in A/B tests (metrics that must NOT move significantly) are evaluated for statistical significance only, not for practical significance — their role is to confirm an absence of harm, not to quantify a benefit.

## See also

- [`../agents/applied-statistician.md`](../agents/applied-statistician.md) — enforces the effect-size-first discipline
- [`./effect-size-and-ci-not-bare-p.md`](./effect-size-and-ci-not-bare-p.md) — the parent rule this specializes to the practical vs statistical distinction

## Provenance

Codifies applied-statistics CLAUDE.md §3 house opinion #3 ("Significance does not equal importance. 'Significant' on huge n can be trivially small. Ask 'is it big enough to matter to the decision?'"). Cohen (1988) established the effect-size conventions cited above.

---

_Last reviewed: 2026-06-05 by `claude`_
