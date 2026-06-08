# Model Experiment Record

> Output of `feature-and-modeling-engineer` + `research-reproducibility-engineer` / the
> `feature-engineering-and-modeling` + `reproducible-research` skills. A record with no leakage check,
> no CV spread, or no seed/env is not a result you can trust or re-run.

## 1. Problem + baseline

- **Prediction goal:** <regression / classification / ranking>
- **Cost structure:** <symmetric? asymmetric? class imbalance?>
- **Baseline (the bar to clear):** <mean / majority / linear> → <baseline metric>

## 2. Features

| Feature | Transform | Fit inside the fold? |
|---|---|---|
| | <encoding / interaction / scaling> | <must be Yes for fit-based transforms> |

## 3. Model + selection

- **Model:** <regularized regression / tree / RF / XGBoost / LightGBM>
- **Why this one:** <interpretability / strong tabular default — classical before deep>
- **Hyperparameter tuning:** <nested CV? test set touched once?>

## 4. Evaluation (leakage-safe)

| Aspect | Choice |
|---|---|
| CV scheme | <KFold / Stratified / GroupKFold / TimeSeriesSplit> |
| Transforms inside the fold? | <Yes — split before any fit> |
| Metric (from the decision) | <RMSE / PR-AUC / recall@precision / cost-weighted — justified> |
| Score (mean ± spread) | <never a single-split point estimate> |
| Lift over baseline | |

## 5. Leakage check

- <transforms fit inside the fold; no target-derived features; group/time integrity; test set touched once>

## 6. Reproducibility

| Item | Status |
|---|---|
| Environment pinned (lockfile + Python version) | |
| Data versioned (hash / snapshot) | |
| Seed set + threaded (split / model / framework) | |
| Notebook clean top-to-bottom / scripted | |
| Tracked run (params + metrics + code/data version) | |

## 7. Handoff

| What | Routed to |
|---|---|
| Is the difference / effect statistically real | `applied-statistics` |
| Serving / monitoring / retraining | `ml-engineering` |
| The upstream pipeline / table | `data-platform` |

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
