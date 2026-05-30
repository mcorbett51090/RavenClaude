# Handle missing data by its mechanism — don't drop rows or mean-fill on reflex

**Status:** Primary diagnostic (when a result depends on which rows survived, check how missingness was handled)
**Domain:** Data preparation / missing data
**Applies to:** `applied-statistics`

---

## Why this exists

The two reflex moves for missing data — **listwise deletion** (drop any row with a gap) and **mean/mode imputation** (fill the gap with the column average) — are the two most common ways to silently bias a result. Dropping rows is unbiased *only* when data is missing completely at random; otherwise it shrinks the sample toward whoever happened to answer, which is a selection bias. Mean-filling is worse: it fabricates certainty, distorts variances and correlations downward, and makes the standard errors lie. Which method is defensible depends on **why** the data is missing — the missingness mechanism — and that is a judgment about the data-generating process, not a default. The discipline: classify the mechanism, pick the method it licenses, and report the assumption.

## How to apply

Classify the mechanism, then pick the method it permits:

```
WHY is it missing?  (mechanism — an assumption about the DGP, often untestable)
  MCAR  missingness unrelated to anything       -> listwise deletion is unbiased (just less power)
  MAR   missingness depends on OBSERVED vars     -> multiple imputation (MICE) or model-based (FIML)
  MNAR  missingness depends on the UNOBSERVED    -> no clean fix; sensitivity analysis + caveat;
        value itself (e.g. high earners hide income)  consider selection / pattern-mixture models

Default for MAR (the common real case): MULTIPLE imputation, not single
  - single imputation (mean/regression) understates uncertainty -> SEs too small
  - multiple imputation creates several completed datasets, pools (Rubin's rules) -> honest SEs
# Tooling: statsmodels MICE; sklearn IterativeImputer for the predictive-prep case
```

**Do:**
- Quantify and *describe* the missingness (how much, in which columns, correlated with what) before choosing a method.
- Prefer multiple imputation (MICE) under MAR so the uncertainty from imputation propagates into the standard errors.
- For MNAR, run a sensitivity analysis across plausible assumptions and state the residual risk plainly — there is no method that makes MNAR go away.

**Don't:**
- Mean/mode-fill on reflex — it fabricates certainty, biases variances/correlations, and makes the inference overconfident.
- Listwise-delete without arguing MCAR — otherwise you've introduced selection bias and don't know its direction.
- Fit the imputation model on the full dataset and then evaluate on a held-out split — that leaks (pitfall #9); fit imputation within the training fold.

## Edge cases / when the rule does NOT apply

- **Trivial missingness** (a fraction of a percent, plausibly MCAR) — listwise deletion is fine and not worth the imputation machinery; say it's negligible and move on.
- **Missingness is itself the signal** — sometimes "not answered" is informative (a missingness indicator predicts the outcome); model the indicator rather than imputing it away.
- **Structural / "not applicable" missing** (a question only some respondents see) isn't really missing data — it's a different population; don't impute across the structural boundary.

## See also

- [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) — pitfall #9 (leakage: fit transforms/imputers on train only) and #4 (Simpson's, a cousin of selection bias).
- [`./causal-watch-confounders-and-colliders.md`](./causal-watch-confounders-and-colliders.md) — selection bias as a causal-graph phenomenon; conditioning on a collider via missingness.
- [`./regression-run-the-diagnostics-before-trusting-coefficients.md`](./regression-run-the-diagnostics-before-trusting-coefficients.md) — the model whose inputs the imputation feeds.
- [`../knowledge/statistics-tooling-2026.md`](../knowledge/statistics-tooling-2026.md) — `statsmodels` MICE for multiple imputation.

## Provenance

Extends pitfall #9 (leakage, "fit scalers/encoders on train only") in [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) (last reviewed 2026-05-26; Tier 1 / consensus) with the standard MCAR/MAR/MNAR taxonomy and the multiple-imputation-over-single guidance (Rubin, *Multiple Imputation for Nonresponse in Surveys*; Little & Rubin, *Statistical Analysis with Missing Data*; van Buuren, *Flexible Imputation of Missing Data* — the MICE reference). Tier 1 on the taxonomy; the MNAR handling is genuinely hard and is flagged as such (sensitivity analysis, not a fix). `statsmodels` MICE per [`../knowledge/statistics-tooling-2026.md`](../knowledge/statistics-tooling-2026.md).

---

_Last reviewed: 2026-05-30 by `claude`_
