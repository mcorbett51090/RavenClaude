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


## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| MLflow / experiment tracking | GA | Params/metrics/artifacts/registry |
| Model registry | GA (MLflow/SageMaker/Vertex) | Source of truth for promotion |
| Feature stores (Feast/managed) | GA | Train-serve consistency |
| Drift detection (Evidently/managed) | GA | Data + prediction drift |
| Serving (KServe/Seldon/managed) | GA | Online + batch; canary |
| Managed platforms (SageMaker/Vertex/Databricks) | GA | Build-vs-buy by maturity |
