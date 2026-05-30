# Match the test to the data type and group structure — traverse the tree, don't keyword-match

**Status:** Absolute rule
**Domain:** Hypothesis testing / test selection
**Applies to:** `applied-statistics`

---

## Why this exists

The wrong test on the right data is as broken as the right test on the wrong data. A Pearson correlation on ordinal Likert data, a t-test on a binary outcome, a chi-square on continuous measurements, or a stack of pairwise t-tests across five groups — each produces a number that looks like a result and isn't. The correct test is determined by the **outcome's data type → number of groups → paired vs independent → assumption gate**, in that order, and that ordering is exactly what the decision tree encodes. The agent's discipline (house opinion #1, method before library) is to **traverse the tree before naming a test**, not pattern-match a familiar test name onto keywords in the request. Pattern-matching is how you end up running a t-test because the word "compare" appeared, when the outcome was a proportion.

## How to apply

Walk [`../knowledge/test-selection-decision-tree.md`](../knowledge/test-selection-decision-tree.md) top-to-bottom; resolve the data type first, then group count, then paired-ness, then the assumption gate:

```
QUESTION type → DATA TYPE of outcome → #GROUPS → PAIRED? → ASSUMPTION GATE → test
  e.g. "difference" + continuous + 2 groups + independent + normal+equalvar  -> independent t-test
       "difference" + categorical + 2 groups                                 -> chi-square (Fisher if cells <5)
       "difference" + ordinal                                                -> Mann-Whitney / Kruskal-Wallis on ranks
       "relationship" + both continuous + linear                             -> Pearson  (else Spearman)
       "predict" + binary outcome                                            -> logistic regression
       "predict" + count outcome                                            -> Poisson / NegBin GLM
```

**Do:**
- Identify the outcome's data type (continuous / ordinal / nominal / count / time-to-event) before anything else — it gates the whole branch.
- Use the omnibus test for 3+ groups (ANOVA / Kruskal-Wallis), then a multiplicity-correcting post-hoc.
- State the path you took through the tree on the Output Contract `Method:` line ("continuous / 2 groups / independent → ...").

**Don't:**
- Reach for a t-test by default because two things are being "compared" — check the data type first.
- Run a Pearson correlation on ordinal or outlier-heavy data (use Spearman); or a chi-square on continuous data (bin only as a last resort, with a stated cost).
- Run pairwise t-tests across 3+ groups instead of the omnibus test (inflates Type I error).

## Edge cases / when the rule does NOT apply

- **Mixed / hierarchical / clustered data** (repeated measures within users, students within schools) outgrows the flat tree — escalate to a mixed model / GEE rather than forcing a leaf.
- **Ordinal outcomes** can sometimes justify ordinal logistic regression rather than a rank test when you want covariate adjustment — name the upgrade explicitly.
- **Multivariate outcomes** (several correlated dependent variables) need MANOVA or a multivariate model, which the single-outcome tree doesn't cover — flag and route.

## See also

- [`../knowledge/test-selection-decision-tree.md`](../knowledge/test-selection-decision-tree.md) — the Mermaid decision tree, the parametric↔nonparametric table, and the assumption gate.
- [`../knowledge/stats-test-selection-decision-trees.md`](../knowledge/stats-test-selection-decision-trees.md) — the extended decision-tree bank (parametric-vs-nonparametric, regression family, causal method, time-series).
- [`./check-assumptions-before-the-test.md`](./check-assumptions-before-the-test.md) — the gate that runs once a candidate test is chosen.
- [`./test-use-the-nonparametric-fallback-when-the-gate-fails.md`](./test-use-the-nonparametric-fallback-when-the-gate-fails.md) — the named fallback for each parametric leaf.

## Provenance

Codifies house opinion #1 ("method before library") and the decision-tree-traversal discipline in [`../agents/applied-statistician.md`](../agents/applied-statistician.md) ("traverse the decision tree before naming a test"), grounded in [`../knowledge/test-selection-decision-tree.md`](../knowledge/test-selection-decision-tree.md) (last reviewed 2026-05-26; Tier 1 / consensus).

---

_Last reviewed: 2026-05-30 by `claude`_
