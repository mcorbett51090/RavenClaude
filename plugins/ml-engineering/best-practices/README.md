# ml-engineering — best-practice docs

Named, citable rules for the `ml-engineering` plugin's specialists. Each file is **one rule**.

---

## Index

_25 rules._

| Doc | Status | Use when |
|---|---|---|
| [`a-notebook-is-not-production.md`](./a-notebook-is-not-production.md) | Absolute rule | Moving any model beyond the prototype stage |
| [`validate-without-leakage.md`](./validate-without-leakage.md) | Absolute rule | Designing any train/val/test split |
| [`route-significance-to-the-statistician.md`](./route-significance-to-the-statistician.md) | Absolute rule | Deciding whether a new model's improvement is real |
| [`roll-out-with-shadow-then-canary.md`](./roll-out-with-shadow-then-canary.md) | Pattern | Planning any model deployment to production |
| [`reproducibility-is-the-floor.md`](./reproducibility-is-the-floor.md) | Absolute rule | Starting any ML project or platform design |
| [`gate-promotion-on-a-defined-metric.md`](./gate-promotion-on-a-defined-metric.md) | Absolute rule | Promoting a model version to production |
| [`monitor-drift-and-define-the-trigger.md`](./monitor-drift-and-define-the-trigger.md) | Absolute rule | Deploying any model to production |
| [`optimize-serving-to-a-budget.md`](./optimize-serving-to-a-budget.md) | Pattern | Designing or reviewing an online serving endpoint |
| [`registry-is-the-source-of-truth.md`](./registry-is-the-source-of-truth.md) | Absolute rule | Deploying or promoting any model |
| [`track-every-experiment.md`](./track-every-experiment.md) | Absolute rule | Running any model training experiment |
| [`eliminate-training-serving-skew.md`](./eliminate-training-serving-skew.md) | Absolute rule | Designing the feature computation pipeline |
| [`feature-store-is-the-consistency-contract.md`](./feature-store-is-the-consistency-contract.md) | Pattern | Designing a multi-model or shared-feature ML system |
| [`data-versioning-is-part-of-reproducibility.md`](./data-versioning-is-part-of-reproducibility.md) | Absolute rule | Running any training experiment with external data |
| [`model-cards-document-intended-use.md`](./model-cards-document-intended-use.md) | Pattern | Registering any model version for production |
| [`online-feature-freshness-has-a-sla.md`](./online-feature-freshness-has-a-sla.md) | Absolute rule | Deploying any model that reads from an online feature store |
| [`batch-inference-is-cheaper-than-online.md`](./batch-inference-is-cheaper-than-online.md) | Pattern | Choosing a serving mode for a new model |
| [`eval-set-is-held-out-not-updated.md`](./eval-set-is-held-out-not-updated.md) | Absolute rule | Designing the train/val/test split at project start |
| [`serving-latency-profiled-before-production.md`](./serving-latency-profiled-before-production.md) | Absolute rule | Promoting a model from staging to production serving |
| [`retraining-pipeline-is-tested-like-code.md`](./retraining-pipeline-is-tested-like-code.md) | Absolute rule | Adding CI for any ML training pipeline |
| [`shadow-mode-before-live-traffic.md`](./shadow-mode-before-live-traffic.md) | Pattern | Deploying a model with a breaking output change or no baseline |
| [`hyperparameter-search-is-logged-not-manual.md`](./hyperparameter-search-is-logged-not-manual.md) | Absolute rule | Running any hyperparameter search or tuning |
| [`model-explainability-is-built-in-not-added-after.md`](./model-explainability-is-built-in-not-added-after.md) | Pattern | Registering any model that will face auditing or stakeholder scrutiny |
| [`split-cv-data-by-scene-not-random-frame.md`](./split-cv-data-by-scene-not-random-frame.md) | Absolute rule | Splitting any computer-vision dataset (frames, multi-shot, tiled images) |
| [`watch-augmentation-and-label-leakage.md`](./watch-augmentation-and-label-leakage.md) | Absolute rule | Adding image augmentation to a CV training pipeline |
| [`right-size-the-vision-model-for-the-inference-target.md`](./right-size-the-vision-model-for-the-inference-target.md) | Pattern | Choosing or compressing a vision model for edge/cloud inference |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
