---
description: "Run the assumption gate on a candidate test before quoting any result, and drop to the named nonparametric fallback when a check fails — normality, equal variance, and independence, with the fallback chosen up front."
argument-hint: "[the test in play, e.g. 't-test comparing two cohorts' conversion']"
---

# Check the test assumptions (or take the named fallback)

You are running `/applied-statistics:check-test-assumptions`. For the test the user named (`$ARGUMENTS`), run the assumption gate and decide — before any p-value is quoted — whether the parametric test holds or you drop to its named nonparametric fallback, the discipline the `applied-statistician` agent treats as non-negotiable.

## When to use this

You have a candidate test (already chosen) and need to confirm it is defensible before reporting it. Use this right after `/applied-statistics:choose-statistical-test` and before any `Result:` line goes out. NOT for picking the test in the first place, and NOT for regression coefficient diagnostics (that is `/applied-statistics:diagnose-regression`).

## Steps

1. **Identify the assumptions the candidate test rests on** (`check-assumptions-before-the-test.md`): a parametric test handed over with no assumption check is a result you cannot defend — name normality, equal variance, and independence as the gate the test must clear.
2. **Run each check with the right tool** (`check-assumptions-before-the-test.md`): normality per group via Shapiro-Wilk (n ≲ 50) and a Q-Q plot; equal variance via Levene; independence read from the study design (paired? clustered?). At large n, read the Q-Q plot rather than over-trusting a normality *test* that rejects trivially.
3. **Try a transformation before abandoning the parametric test** (`check-assumptions-before-the-test.md`): a log / Box-Cox can restore normality or stabilize variance — re-check after transforming.
4. **If the gate still fails, drop to the named fallback** (`test-use-the-nonparametric-fallback-when-the-gate-fails.md`): Mann-Whitney U, Wilcoxon signed-rank, Kruskal-Wallis, Friedman, or Spearman — the fallback is chosen *before* a result is reported, not retrofitted after a reviewer objects.
5. **For 3+ groups, never run a stack of pairwise t-tests** (`test-correct-for-multiple-comparisons.md`): use the omnibus test (ANOVA / Kruskal-Wallis) then a multiplicity-correcting post-hoc (Tukey / Dunn).
6. State the checks run and the fallback taken (if any) on the Output Contract `Assumptions checked:` line, and produce a runnable Tier-1 snippet (`scipy` / `statsmodels` / `pingouin`).

## Guardrails

- Never push skewed, heteroscedastic, or non-independent data through a t-test or OLS unchecked — the p-value will look authoritative and be quietly wrong.
- Pick the fallback before reporting; a fallback "discovered" after the parametric result looked bad is p-hacking by another name.
- A chi-square needs adequate expected cell counts (≥ 5; Fisher's exact for small cells), not a normality check — match the gate to the test.
