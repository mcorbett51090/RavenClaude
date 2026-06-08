# EDA Report

> Output of `exploratory-data-scientist` / the `eda-workflow` skill. An empty "Leakage candidates" or
> "Uncertainty" section is a sign the data hasn't actually been looked at yet.

## 1. The question + the target

- **Question / prediction goal:** <what we're trying to learn>
- **Target definition:** <how the target is defined — and is it available at prediction time?>
- **Target leakage risk:** <is the target fuzzy, derived, or contaminated?>

## 2. Data profile

| Aspect | Finding |
|---|---|
| Shape (rows × cols) | |
| Types | |
| Missingness (pattern + *why*) | |
| Cardinality / duplicates | |
| Distributions (plotted?) | <flag bimodality, skew, outliers — not just the mean> |

## 3. Cleaning decisions

| Decision | What we did | Rationale | Risk if wrong |
|---|---|---|---|
| <missingness> | | | |
| <outliers> | | | |
| <type coercion / dedup> | | | |

## 4. Visual findings (read adversarially)

- <relationship / breakdown> — <what it shows, and the confounder / Simpson's-paradox check>

## 5. Leakage candidates (hand to feature-and-modeling-engineer)

- <column absent at prediction time / target-derived / ID encoding the answer>

## 6. Hypotheses generated (route significance to applied-statistics)

| Hypothesis | What suggests it | Uncertainty (sample size / confounders / caveat) |
|---|---|---|
| | | |

---

```
Status: ...
Files changed: ...
Uncertainty + caveats: ...
Leakage check: ...
Reproducibility posture: ...
Handoff: ...
Open questions: ...
Grounding checks performed: ...
```
