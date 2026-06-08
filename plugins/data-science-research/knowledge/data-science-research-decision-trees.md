# Data Science Research — Decision Trees

_Decision trees + a dated tooling map. Tooling rows are `[verify-at-build]` — re-check against the library/project before quoting. Last reviewed: 2026-06-08._

Traverse before modeling, before choosing an evaluation scheme, before picking the metric, before imputing a missing value, and before declaring a result reproducible. Five trees: EDA-before-modeling, classical-model-selection-and-honest-evaluation, metric-per-decision, missing-data-diagnosis, and the reproducibility spine.

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

## Decision Tree: Which metric — derive it from the decision, not from habit

The wrong metric makes a bad model look good. Choose from the cost structure, then justify it.

```mermaid
graph TD
  A[Have a model to score] --> B{Regression or classification?}
  B -- Regression --> C{Are large errors disproportionately costly?}
  C -- Yes --> D[RMSE penalizes big misses; or a custom asymmetric loss if over/under differ]
  C -- No --> E[MAE - robust, interpretable in target units; report R2 only as variance-explained context]
  B -- Classification --> F{Classes balanced?}
  F -- No --> G{Do you consume probabilities or a ranking?}
  G -- Ranking/probabilities --> H[PR-AUC for rare positives; calibration curve if probs feed a downstream decision]
  G -- Hard labels --> I[Recall-at-precision or F-beta tuned to the cost of FP vs FN - NOT accuracy]
  F -- Yes --> J{Is one error type costlier than the other?}
  J -- Yes --> K[Cost-weighted loss / choose the operating threshold from the cost ratio]
  J -- No --> L[Accuracy / ROC-AUC are defensible here - still pair with the baseline on the same metric]
```

_Always score the baseline on the *same* metric so "better" is measured against the right bar; report lift, not just the absolute number._

## Decision Tree: Missing data — diagnose before you impute

Imputation is a modeling decision. The *fact* of missingness is often itself a signal.

```mermaid
graph TD
  A[Column has missing values] --> B{Why is it missing - do you know the mechanism?}
  B -- No --> C[Investigate first - is it a sentinel/default masquerading as data? a join failure? a sensor gap?]
  B -- MCAR --> D{Small fraction missing?}
  D -- Yes --> E[Listwise drop is defensible - but confirm it doesn't shrink a rare class]
  D -- No --> F[Impute inside the fold - mean/median or model-based]
  B -- MAR --> G[Impute inside the fold conditioned on observed cols + add a missing-indicator column]
  B -- MNAR --> H[Missingness correlates with the outcome - add the indicator; NEVER silently drop, it biases the result]
  E --> I[Record the decision]
  F --> I
  G --> I
  H --> I
  I[Every dropped row / filled value is an auditable assumption - log it]
```

_Fit every imputer inside the cross-validation fold like any other transform; fitting on the full dataset leaks the test set's distribution._

## Decision Tree: Is this result reproducible — the spine

A result that can't be re-run from a pinned env, versioned data, and a fixed seed is an anecdote.

```mermaid
graph TD
  A[Have a result to defend] --> B{Notebook runs clean restart-and-run-all?}
  B -- No --> C[Fix hidden out-of-order state, or extract to a scripted pipeline - top-to-bottom is the only honest test]
  B -- Yes --> D{Environment pinned - Python + every dep at exact versions?}
  D -- No --> E[Lock it - a floating >= is a future irreproducibility]
  D -- Yes --> F{Exact input data versioned - hash / snapshot, not "the latest table"?}
  F -- No --> G[Version it with a content hash / DVC snapshot]
  F -- Yes --> H{Seed threaded through EVERY stochastic step - split, model, framework?}
  H -- No --> I[Thread the seed everywhere - a single global seed is not enough]
  H -- Yes --> J{Run's params + metrics + code/data version tracked?}
  J -- No --> K[Log the run - MLflow / W&B / DVC - so it's recoverable and comparable]
  J -- Yes --> L[Reproducible - it reproduces byte-for-byte on another machine]
```

_The notebook is a draft, not the deliverable; the reproducible artifact (pinned env + scripted pipeline + tracked run) is what ships._

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
