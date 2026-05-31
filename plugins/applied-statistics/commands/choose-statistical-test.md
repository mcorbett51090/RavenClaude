---
description: "Pick the right statistical test by traversing the decision tree on the outcome's data type, group count, and pairing, then check assumptions and drop to the named nonparametric fallback when the gate fails."
argument-hint: "[the comparison, e.g. 'is conversion different between three checkout variants?']"
---

# Choose the statistical test

You are running `/applied-statistics:choose-statistical-test`. Select a defensible test for the question (`$ARGUMENTS`) by traversing the decision tree, not by pattern-matching a familiar test name onto keywords — the discipline the `applied-statistician` agent enforces (house opinion #1, method before library).

## When to use this

You have data (or are about to) and need to know which test answers "is this difference / relationship real?" Use this whenever someone reached for a t-test "because we're comparing things." NOT for designing the experiment first (that is `/applied-statistics:design-experiment-and-power`).

## Steps

1. **Resolve the outcome's data type first** — continuous / ordinal / nominal / count / time-to-event. It gates the entire branch (`test-match-the-test-to-the-data-type.md`).
2. **Then group count, then paired vs. independent**, walking the tree top-to-bottom (`test-match-the-test-to-the-data-type.md`): e.g. continuous + 2 groups + independent + normal → independent t-test; categorical + 2 groups → chi-square (Fisher if cells < 5); ordinal → Mann-Whitney / Kruskal-Wallis on ranks; both continuous + linear → Pearson, else Spearman.
3. **For 3+ groups use the omnibus test** (ANOVA / Kruskal-Wallis), never a stack of pairwise t-tests, then a multiplicity-correcting post-hoc (Tukey / Dunn) — see `test-correct-for-multiple-comparisons.md`.
4. **Run the assumption gate before quoting any result** (`check-assumptions-before-the-test.md`): normality (Shapiro-Wilk / Q-Q), equal variance (Levene), independence (from design). If a check fails and a transform won't fix it, drop to the named fallback (`test-use-the-nonparametric-fallback-when-the-gate-fails.md`).
5. State the **path you took through the tree** on the Output Contract `Method:` line and the **assumption results / fallback** on the `Assumptions checked:` line (CLAUDE.md §6).
6. Produce the recommended test + a runnable Tier-1 snippet (`scipy`/`statsmodels`/`pingouin`), and flag anything that outgrows the flat tree (clustered/repeated-measures → mixed model; multivariate → MANOVA).

## Guardrails

- The wrong test on the right data is as broken as the right test on the wrong data — never name a test before resolving the data type.
- Don't over-trust a normality *test* at large n (it rejects trivially); read the Q-Q plot too.
- A chi-square needs adequate expected cell counts (>= 5; Fisher's exact for small cells), not a normality check.
