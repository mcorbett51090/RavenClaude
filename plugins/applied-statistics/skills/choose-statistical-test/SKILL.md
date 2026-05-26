---
name: choose-statistical-test
description: Pick the right hypothesis test for a described scenario by traversing the test-selection decision tree (data type → #groups → paired? → assumption gate → test), then return the recommended test, its assumption checks, its nonparametric fallback, and a ≤10-line runnable snippet. Reach for this when the user asks "which test do I use?" or hands over two-or-more groups/variables to compare. Used by `applied-statistician` (primary).
---

# Skill: choose-statistical-test

> **Invoked by:** `applied-statistician` (primary). Also consulted by `experiment-analysis` and `statistical-qa-of-metrics` when they need to name the underlying test.
>
> **When to invoke:** "which test should I use?"; "is the difference between these groups significant?"; any comparison of 2+ groups or relationship between 2 variables.
>
> **Output:** the recommended test + the assumption checks that gate it + the nonparametric fallback + a short runnable snippet (method-before-library) + the effect-size/CI to report alongside.

## Procedure

1. **Restate the question** in the tree's terms: is it a *group difference*, a *relationship*, or a *prediction*?
2. **Traverse the decision tree** in [`../../knowledge/test-selection-decision-tree.md`](../../knowledge/test-selection-decision-tree.md) against:
   - outcome **data type** (continuous / categorical / ordinal / count / time-to-event),
   - **number of groups** (1 / 2 / 3+),
   - **paired vs independent**,
   - the **assumption gate** (normality, equal variance, independence).
3. **Name the method first, the library second.** Resolve to the parametric leaf only if the assumption gate passes; otherwise take the nonparametric fallback.
4. **Emit a ≤10-line snippet** (Tier-1 tooling — `scipy.stats` / `pingouin` / `statsmodels`; see [`../../knowledge/statistics-tooling-2026.md`](../../knowledge/statistics-tooling-2026.md)) that (a) checks the assumption, (b) runs the test, (c) reports **effect size + CI**, not just p.
5. **State the fallback explicitly:** "if normality fails, switch to <nonparametric test>."

## Worked example

> User: "I have conversion counts for two landing pages. Which test?"

- Question type: group difference. Outcome: the per-user binary "converted?" → **two independent groups, categorical outcome** → **chi-square test of independence** (Fisher's exact if any expected cell < 5).
- If instead the outcome were a continuous per-user value (e.g., revenue) and roughly normal → independent t-test (Welch if variances differ); non-normal → Mann-Whitney U.
- Report: the effect (e.g., difference in conversion rate or odds ratio) **with a confidence interval**, not just the p-value.

```python
# two landing pages, conversion counts — chi-square of independence
import numpy as np
from scipy.stats import chi2_contingency
# rows = page A / page B; cols = converted / not
table = np.array([[120, 1880], [150, 1850]])
chi2, p, dof, expected = chi2_contingency(table)
if (expected < 5).any():
    from scipy.stats import fisher_exact          # small expected cells → exact test
    _, p = fisher_exact(table)
# report the effect (rate difference + CI), not just p — see experiment-analysis skill
```

## Guardrails
- Never return a parametric test without naming its assumption check **and** its fallback.
- 3+ groups → ANOVA/Kruskal-Wallis + a multiplicity-correcting post-hoc, **never** a stack of pairwise t-tests (pitfall #2).
- Always pair the result with an effect size + CI (pitfall #6). See [`../../knowledge/statistical-pitfalls.md`](../../knowledge/statistical-pitfalls.md).
