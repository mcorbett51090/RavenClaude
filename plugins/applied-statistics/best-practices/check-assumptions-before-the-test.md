# Check the assumptions (or take the named fallback) before reporting a test

**Status:** Absolute rule
**Domain:** Hypothesis testing / test selection
**Applies to:** `applied-statistics`

---

## Why this exists

A parametric test handed over with no assumption check is a result you cannot defend. A t-test on skewed, heteroscedastic, or non-independent data, or an OLS fit on residuals that violate its assumptions, produces a p-value and a confidence interval that *look* authoritative and are quietly wrong. The discipline is non-negotiable in this plugin: **never hand over a parametric test without its assumption check and its named nonparametric fallback** (house opinion #4, pitfall #7). The cost of skipping it is an artifact — a "significant" finding that evaporates the moment someone checks normality or equal variance. The decision tree gates the test on the assumption check precisely so the fallback is chosen *before* a result is reported, not retrofitted after a reviewer objects.

## How to apply

Traverse the assumption gate in [`../knowledge/test-selection-decision-tree.md`](../knowledge/test-selection-decision-tree.md) after picking the candidate test; if a check fails and you can't fix it by transformation, drop to the named fallback rather than reporting a parametric result you can't stand behind:

```
Candidate: 2 groups, independent, continuous -> independent t-test
  Normality (per group)?   Shapiro-Wilk (n ≲ 50) / Q-Q plot
  Equal variance?          Levene's test
  Independence?            from study design (paired? clustered?)
    all OK            -> independent t-test (Welch's if variances differ)
    normality fails   -> Mann-Whitney U                 # the named fallback
    can transform     -> log / Box-Cox, then re-check
3+ groups -> ANOVA / Kruskal-Wallis, NEVER a stack of pairwise t-tests (inflates Type I error)
```

Report which checks were run and their result on the Output Contract's `Assumptions checked:` line — including the fallback taken when one failed.

**Do:**
- Run normality / equal-variance / independence checks appropriate to the candidate test before quoting its result.
- Drop to the named nonparametric fallback (Mann-Whitney, Wilcoxon, Kruskal-Wallis, Friedman, Spearman) when the gate fails and transformation won't fix it.
- For 3+ groups use the omnibus test (ANOVA / Kruskal-Wallis) then a multiplicity-correcting post-hoc (Tukey / Dunn).

**Don't:**
- Push skewed / heteroscedastic / non-independent data through a t-test or OLS unchecked.
- Run a stack of pairwise t-tests across 3+ groups instead of an omnibus test.
- Over-trust a normality *test* on huge n — read the Q-Q plot too; the test rejects trivially at large samples.

## Edge cases / when the rule does NOT apply

- **Tests with no parametric assumptions to gate** — a chi-square test of independence (with adequate expected cell counts ≥ 5; Fisher's exact for small cells) or a rank correlation isn't gated by normality. Check *its* precondition (expected cell counts), not normality.
- **Large-sample robustness** — some tests are robust to mild violations at large n via the CLT, but "robust" is a defended judgment with the diagnostic shown, not an excuse to skip the check.
- **Bootstrap / robust-SE route** — when neither the parametric assumption holds nor a clean nonparametric fallback fits (e.g. a regression with several predictors), bootstrap CIs or robust standard errors are a defensible third path — name it as the method taken.

## See also

- [`../knowledge/test-selection-decision-tree.md`](../knowledge/test-selection-decision-tree.md) — the decision tree, the parametric ↔ nonparametric fallback table, and the assumption gate this codifies.
- [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) — pitfall #7 (assumption violations) and the multiple-comparisons guidance for the post-hoc step.
- [`./report-effect-size-not-just-p.md`](./report-effect-size-not-just-p.md) — the companion rule on what to report once the test is valid.
- [`../agents/applied-statistician.md`](../agents/applied-statistician.md) — "never hand over a parametric test without its assumption check and its named nonparametric fallback".

## Provenance

Codifies house opinion #4 ("check assumptions or use the fallback") in [`../CLAUDE.md`](../CLAUDE.md) §3, pitfall #7 in [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md), and the assumption gate + fallback table in [`../knowledge/test-selection-decision-tree.md`](../knowledge/test-selection-decision-tree.md) (both last reviewed 2026-05-26; Tier 1 / consensus). The advisory hook [`../hooks/flag-statistical-smells.sh`](../hooks/flag-statistical-smells.sh) flags a parametric test with no nearby assumption check.

---

_Last reviewed: 2026-05-30 by `claude`_
