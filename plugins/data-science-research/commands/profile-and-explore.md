---
description: "Profile and explore a dataset before anyone models it: shape/types/missingness/cardinality/distributions, documented cleaning, leakage candidates, and hypotheses with uncertainty."
argument-hint: "[the dataset + the prediction goal or question + any known caveats]"
---

You are running `/data-science-research:profile-and-explore`. Use `exploratory-data-scientist` + the `eda-workflow` skill.

## Steps
1. Confirm the target is clearly and correctly defined and available at prediction time; if it's fuzzy or leaking, stop and fix it first.
2. Profile the data — shape, dtypes, missingness pattern (and *why* it's missing), cardinality, duplicates, and the distribution of every column. Plot distributions; don't trust summary stats.
3. Make and document cleaning decisions (missingness, outliers, type coercions, dedup) with the rationale and the risk of each.
4. Read relationships adversarially for confounders / Simpson's-paradox reversals; flag leakage candidates (cols absent at prediction time, target-derived fields, IDs encoding the answer).
5. Generate 2-3 hypotheses worth testing, each with its uncertainty (sample size, confounders, the caveat); route any significance question to `applied-statistics`.
6. Emit the EDA report + the Structured Output block (with `Uncertainty + caveats:` and `Leakage check:`). Hand features to `feature-and-modeling-engineer`.
