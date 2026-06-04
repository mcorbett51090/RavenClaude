# ML Engineering — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before choosing a serving pattern or a retraining trigger.

## Decision Tree: Serving pattern: online or batch?

Match the serving pattern to the latency and request shape.

```mermaid
graph TD
  A[A model to deploy] --> B{Prediction needed per-request in real time?}
  B -- No, score many records periodically --> C[Batch inference job]
  B -- Yes --> D{Strict latency budget?}
  D -- Yes --> E[Online endpoint + latency optimization batching/quantization]
  D -- No, async ok --> F[Online endpoint or async queue]
  C --> G[Deploy registered version; schedule; monitor outputs]
  E --> H[Shadow -> canary -> full rollout]
  F --> H
```

_Deploy a registered version from the registry, never a copied file._

## Decision Tree: When to retrain?

Decide the trigger before launch; drift is the early warning before labels arrive.

```mermaid
graph TD
  A[A deployed model] --> B{Ground-truth labels available soon?}
  B -- Yes --> C{Performance dropped past threshold?}
  C -- Yes --> D[Retrain - verify the drop is real with applied-statistics]
  C -- No --> E[Hold]
  B -- No, labels delayed/absent --> F{Significant input/prediction drift?}
  F -- Yes --> G[Retrain / investigate concept vs data drift]
  F -- No --> H{Scheduled cadence due?}
  H -- Yes --> I[Scheduled retrain]
  H -- No --> E
```


## Decision Tree: Build or buy the ML platform?

Match the platform to ML maturity; don't over-build for one model or hand-run fifty.

```mermaid
graph TD
  A[Need an ML platform] --> B{How many models in production, realistically?}
  B -- Zero / first one --> C[Managed end-to-end SageMaker/Vertex/Databricks - cut undifferentiated ops]
  B -- A handful --> D{Strong existing cloud + small team?}
  D -- Yes --> C
  D -- No, need control/portability --> E[Managed registry+tracking, self-host orchestration as needed]
  B -- Many / scaling --> F{Specialized scale, cost, or control needs?}
  F -- Yes --> G[Self-host MLflow/Kubeflow/Ray - own the control plane]
  F -- No --> E
  C --> H[Reproducibility + registry are non-negotiable in ANY choice]
  E --> H
  G --> H
```

_Managed cuts ops you don't differentiate on; self-host buys control and cost-at-scale. Choose by team size, control needs, and existing cloud — not hype._

## Decision Tree: Data drift or concept drift — what's the response?

The diagnosis selects the fix; they are not interchangeable.

```mermaid
graph TD
  A[Model performance / behavior shifted] --> B{Are ground-truth labels available?}
  B -- Yes --> C{Inputs shifted but input->output mapping stable?}
  C -- Yes --> D[Data drift: retrain on recent data often suffices]
  C -- No, the mapping itself changed --> E[Concept drift: retrain AND likely re-engineer features/target]
  B -- No, labels delayed/absent --> F{Significant input/prediction drift detected?}
  F -- Yes --> G[Investigate: could be data OR concept - escalate label collection]
  F -- No --> H[Hold; confirm the signal is real -> applied-statistics]
  D --> I[Confirm the shift/lift is real, not noise -> applied-statistics]
  E --> I
```

_Data drift = inputs moved; concept drift = the relationship moved. Same symptom, different fix. Whether the change is real routes to applied-statistics._

## Decision Tree: Which validation split for this problem?

Pick the split that prevents leakage for the data's structure, then use the test set once.

```mermaid
graph TD
  A[Setting up validation] --> B{Temporal / time-ordered data?}
  B -- Yes --> C[Time-based split: train on past, validate on future - never shuffle across time]
  B -- No --> D{Grouped/entity-correlated rows e.g. multiple per user?}
  D -- Yes --> E[Grouped split: keep an entity entirely in one fold - no leakage across folds]
  D -- No --> F{Enough data for a held-out test set?}
  F -- Yes --> G[Train/val/test; cross-validate on train+val]
  F -- No --> H[K-fold CV with a small final holdout]
  C --> I[Reserve the test set for ONE final evaluation]
  E --> I
  G --> I
  H --> I
```

_Shuffling time-ordered data or splitting an entity across folds leaks future/correlated information; the inflated metric is a production disappointment with a delay._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| MLflow / experiment tracking | GA | Params/metrics/artifacts/registry |
| Model registry | GA (MLflow/SageMaker/Vertex) | Source of truth for promotion |
| Feature stores (Feast/managed) | GA | Train-serve consistency |
| Drift detection (Evidently/managed) | GA | Data + prediction drift |
| Serving (KServe/Seldon/managed) | GA | Online + batch; canary |
| Managed platforms (SageMaker/Vertex/Databricks) | GA | Build-vs-buy by maturity |
