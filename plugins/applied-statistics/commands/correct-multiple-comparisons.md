---
description: "Control the error rate across a family of tests — count every test in the family, then pick FWER (Holm/Bonferroni) for confirmatory decisions or FDR (Benjamini-Hochberg) for screening, before calling any one result significant."
argument-hint: "[the family of tests, e.g. '8 metrics x 3 segments in this A/B readout']"
---

# Correct for multiple comparisons

You are running `/applied-statistics:correct-multiple-comparisons`. For the analysis the user described (`$ARGUMENTS`), enumerate the family of tests and apply the correction the *decision* needs — FWER vs FDR are not interchangeable — before any single result is called significant, the way the `applied-statistician` agent would.

## When to use this

Your analysis tests several metrics, segments, time windows, or arms, and you are about to report which ones are "significant." Use this whenever someone reaches for the one p < 0.05 out of many. NOT needed for a single pre-registered primary metric tested once.

## Steps

1. **Count the whole family** (`test-correct-for-multiple-comparisons.md`): every secondary metric, every segment, every interim look, and every post-hoc pairwise comparison counts — run twenty tests at α=0.05 and you expect one false positive by chance alone.
2. **Pick the correction family by the cost of a single false positive** (`test-correct-for-multiple-comparisons.md`): confirmatory work (a launch / contract / medical decision; one false positive is costly) → control FWER with **Holm** (uniformly more powerful than Bonferroni) or Bonferroni. Exploratory / screening (which of 200 features look promising; you'll follow up the hits) → control FDR with **Benjamini-Hochberg**.
3. **Apply it with Tier-1 tooling** (`test-correct-for-multiple-comparisons.md`): `from statsmodels.stats.multitest import multipletests; multipletests(pvals, alpha=0.05, method='holm')` — or `'fdr_bh'`.
4. **For 3+ group comparisons, gate through the omnibus test first** (`test-correct-for-multiple-comparisons.md`): ANOVA / Kruskal-Wallis, then a multiplicity-correcting post-hoc (Tukey / Dunn) rather than raw pairwise tests.
5. **Lead the readout with corrected results, effect size, and CI** (`effect-size-and-ci-not-bare-p.md`): report the effect size + 95% CI for the survivors, the p-value secondary, and disclose how many tests were run.
6. Produce the corrected results table and the runnable snippet, noting which family (FWER/FDR) was chosen and why.

## Guardrails

- Treating FDR as a universal drop-in for Bonferroni is wrong — FDR controls a *proportion* of false discoveries, not the probability of any one; match the family to the decision.
- The family is defined by the analysis plan, not by which tests turned out significant — correcting after the fact to rescue a result is p-hacking.
- Never report the lone p < 0.05 out of many without disclosing the family size.
