# Data Science Research — Decision Trees

_Decision trees + a dated tooling map. Tooling rows are `[verify-at-build]` — re-check against the library/project before quoting. Last reviewed: 2026-06-08._

Traverse before modeling, before choosing an evaluation scheme, and before declaring a result reproducible.

## Decision Tree: EDA before modeling — what to check first

A model on un-profiled data is a guess with a confidence interval. Profile first.

```mermaid
graph TD
  A[New dataset, prediction goal] --> B{Is the target clearly and correctly defined?}
  B -- No --> C[Stop - fix the target definition; a fuzzy/leaking target makes every number meaningless]
  B -- Yes --> D{Profiled shape, types, missingness, cardinality, distributions?}
  D -- No --> E[Profile first - plot distributions, not just summary stats the bimodal mean lies]
  D -- Yes --> F{Any leakage candidates? cols absent at prediction time / target-derived / ID encoding the answer}
  F -- Yes --> G[Flag them - exclude or defer to inside-the-fold; a suspiciously good signal is a leakage alarm]
  F -- No --> H{Is the pattern exploratory or a confirmatory claim?}
  H -- Confirmatory --> I[Route the significance question to applied-statistics - do not p-hack]
  H -- Exploratory --> J[Generate hypotheses with uncertainty, hand features to feature-and-modeling-engineer]
```

_If you can't define the target or name the missingness pattern, you're not ready to model._

## Decision Tree: Which classical model — and how to evaluate it honestly

Baseline first, classical before deep, and never let a transform see the test fold.

```mermaid
graph TD
  A[Tabular prediction problem] --> B{Established a dumb baseline? mean / majority / linear}
  B -- No --> C[Set the baseline first - it's the bar every model must clear]
  B -- Yes --> D{Need interpretability or a fast, strong default?}
  D -- Interpretability --> E[Regularized linear / a shallow tree - explainable, honest]
  D -- Strong default --> F[Gradient boosting: XGBoost / LightGBM - the tabular workhorse]
  A --> G{Evaluation: is every transform fit INSIDE the CV fold, split before any fit?}
  G -- No --> H[Fix it - scaling/imputing/encoding before the split leaks the test set the score is fiction]
  G -- Yes --> I{Folds respect structure? grouped / time-series when data demands}
  I -- No --> J[Use GroupKFold / TimeSeriesSplit - random folds leak across groups/time]
  I -- Yes --> K{Metric chosen from the decision, not habit?}
  K -- No --> L[Pick the metric from the cost: PR-AUC for imbalance, asymmetric loss for asymmetric cost]
  K -- Yes --> M[Report the CV spread + the leakage check - never a single-split point estimate]
```

_Tuning hyperparameters? Use nested CV and report the nested estimate; the test set is touched once._

---

## Tooling map (2026, `[verify-at-build]`)

| Layer | Options | Notes |
|---|---|---|
| Data profiling / wrangling | pandas, polars, `ydata-profiling`, Great Expectations | Plot distributions; profile missingness/cardinality before modeling `[verify-at-build]` |
| Visualization | matplotlib, seaborn, plotly, Altair | Read plots adversarially — outliers, bimodality, Simpson's-paradox confounders `[verify-at-build]` |
| Classical modeling | scikit-learn (linear, trees, RF), XGBoost, LightGBM, CatBoost | Baseline first; gradient boosting is the tabular workhorse `[verify-at-build]` |
| Cross-validation | scikit-learn `KFold` / `StratifiedKFold` / `GroupKFold` / `TimeSeriesSplit`, nested CV | Transforms inside the fold; grouped/time-aware when structure demands `[verify-at-build]` |
| Metrics | scikit-learn `metrics` (RMSE/MAE, ROC-AUC/PR-AUC, F-beta), calibration curves | Choose from the decision/cost; accuracy lies on imbalanced classes `[verify-at-build]` |
| Pipelines (leakage-safe) | scikit-learn `Pipeline` / `ColumnTransformer` | Bundles fit-transforms so they stay inside the fold by construction `[verify-at-build]` |
| Experiment tracking | MLflow, Weights & Biases, DVC experiments | Log params + metrics + artifacts + code/data version per run `[verify-at-build]` |
| Data/version control | DVC, content hashes, immutable snapshots | Version the exact input — never "the latest table" `[verify-at-build]` |
| Environment pinning | `pip` lockfile, Poetry (`poetry.lock`), conda env, containers | Pin Python + every dependency; floating `>=` is a future irreproducibility `[verify-at-build]` |

_Seams: the significance call (p-values, confidence intervals, power) → `applied-statistics`; serving/monitoring/retraining → `ml-engineering`; the pipeline/warehouse that produces the table → `data-platform`. Re-verify any library version/behavior before quoting it to a consumer._
