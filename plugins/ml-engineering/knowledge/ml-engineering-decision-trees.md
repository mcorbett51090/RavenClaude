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

## Decision Tree: Model rollout — shadow, canary, or full deploy?

**When this applies:** a new model version has passed offline evaluation and is ready for production deployment. The rollout strategy depends on the risk of the model and the availability of a live signal.

**Last verified:** 2026-06-05 against model-serving-engineer mandate and ML deployment best practices.

```mermaid
flowchart TD
    START[New model version ready to deploy] --> Q1{Is the model a breaking change - new output schema, changed semantics?}
    Q1 -->|yes| SHADOW[Shadow mode first - validate output format and distribution]
    Q1 -->|no, same output schema| Q2{Is there a live user-facing metric to measure the new model?}
    Q2 -->|yes| Q3{Does the current model have a known performance baseline?}
    Q3 -->|yes| CANARY[Canary - 1% to 10% to 100% gated on live metric]
    Q3 -->|no baseline| SHADOW
    Q2 -->|no, batch or internal| Q4{Is the model significantly different from the previous version?}
    Q4 -->|yes, major retrain or algorithm change| SHADOW
    Q4 -->|no, incremental update| DIRECT[Deploy directly with monitoring - low-risk increment]
    SHADOW --> CANARY
```

**Rationale per leaf:**
- *Shadow first* — a breaking output schema must be validated before any user sees the prediction; shadow mode has zero user impact.
- *Canary* — when a live metric exists and a baseline is known, canary delivers statistical evidence of improvement or regression before full rollout.
- *Shadow then canary* — when the baseline is unknown, establish it via shadow observation, then canary for the promotion gate.
- *Direct deploy* — incremental retrains of the same architecture with no schema change have low enough risk for a direct deploy with monitoring.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Shadow mode | Doubled serving cost | Zero user impact | Metric review | Breaking changes, no baseline |
| Canary | Partial traffic cost | Small - 1-10% users | Live metric gate | Live metric available |
| Direct deploy | No extra cost | Full - all users | Monitoring alert | Low-risk incremental update |

## Decision Tree: Retraining — automated trigger or human decision?

**When this applies:** the ML monitoring system has detected drift, performance decay, or a scheduled retrain cadence is due. The team must decide whether to trigger retraining automatically or require human sign-off.

**Last verified:** 2026-06-05 against ml-monitoring-engineer and training-pipeline-engineer mandates.

```mermaid
flowchart TD
    START[A retrain trigger fires] --> Q1{Is this a scheduled cadence retrain with no drift signal?}
    Q1 -->|yes| Q2{Has the pipeline been tested and run successfully before?}
    Q2 -->|yes| AUTO_SCHED[Automated retrain - pipeline runs, new model goes to registry]
    Q2 -->|no, first or untested run| HUMAN[Human review before triggering]
    Q1 -->|no, drift or performance signal| Q3{Is the drift severe - PSI greater than 0.2 or performance drop more than 5 pct?}
    Q3 -->|yes| Q4{Is the training pipeline reliable - recent successful run?}
    Q4 -->|yes| AUTO_DRIFT[Automated retrain - alert on result for human review]
    Q4 -->|no| HUMAN
    Q3 -->|no, mild drift| Q5{Is the retraining cost high - days of compute?}
    Q5 -->|yes| HUMAN
    Q5 -->|no, cheap run| AUTO_DRIFT
```

**Rationale per leaf:**
- *Automated scheduled* — a tested pipeline on a known cadence has low risk; automation reduces toil.
- *Human review* — untested pipelines, unreliable infra, or expensive runs warrant human sign-off before committing compute.
- *Automated on drift* — severe drift is an urgency signal; automated trigger keeps response time short with human review of the output.
- *Human on mild drift + high cost* — mild drift may not justify expensive recomputation; a human can weigh the cost vs. the expected lift.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Automated scheduled | Low - routine | Low | Monitoring alert on result | Tested pipeline, regular cadence |
| Automated on drift | Medium - triggered | Low | Human reviews output | Severe drift, reliable pipeline |
| Human decision | High - latency | Lowest | Human required | Untested pipeline, expensive run, mild drift |

## Decision Tree: Which drift metric to monitor for this model?

**When this applies:** deploying a new model and designing the monitoring strategy. Choosing the wrong drift metric produces noisy false alarms (alert fatigue) or silent degradation (missed decay).

**Last verified:** 2026-06-05 against ml-monitoring-engineer mandate and Evidently/Seldon drift detection documentation.

```mermaid
flowchart TD
    START[Choosing drift monitoring metrics] --> Q1{Are ground-truth labels available within a reasonable delay?}
    Q1 -->|yes, days to weeks| PERF[Monitor performance decay - AUC drop, F1 drop, or MSE rise]
    Q1 -->|no, months or never| Q2{Is the input distribution expected to be stable?}
    Q2 -->|yes, stable domain| Q3{Numerical or categorical features?}
    Q3 -->|numerical| PSI[PSI or KS-test on numerical feature distributions]
    Q3 -->|categorical| CHI2[Chi-squared or TVD on categorical feature distributions]
    Q2 -->|no, known seasonal or trend changes| PRED[Monitor prediction distribution shift - proxy for concept drift]
    PERF --> BOTH[Also monitor input drift as early warning before labels arrive]
    PSI --> PRED
    CHI2 --> PRED
```

**Rationale per leaf:**
- *Performance decay* — when labels are available, this is the ground truth; a drop in AUC/F1/RMSE is the most direct signal.
- *PSI/KS-test* — Population Stability Index and Kolmogorov-Smirnov tests are standard for numerical feature drift detection with no labels needed.
- *Chi-squared/TVD* — Total Variation Distance and chi-squared test for categorical distribution shifts.
- *Prediction distribution shift* — a shift in the model's output distribution is a proxy for concept drift when labels are unavailable; easier to monitor than input drift.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Performance decay | Requires labels | Direct signal | Retrain trigger | Labels available within weeks |
| Input drift - PSI/KS | No labels needed | Early warning | Alert for review | Numerical features, no labels |
| Prediction drift | No labels needed | Proxy signal | Alert for review | Output distribution monitorable |
