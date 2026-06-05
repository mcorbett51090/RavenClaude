---
name: ml-experiment-tracking
description: "Playbook for setting up and operating an experiment tracking system (MLflow or Weights and Biases) — what to log, run comparison workflow, promotion to the model registry, and avoiding the common leakage and cherry-picking pitfalls."
---

# ML Experiment Tracking

## When to invoke

Use when instrumenting a training script for the first time, standardizing experiment tracking across a team, or deciding when a candidate model is genuinely better than the current production version.

## Why tracking matters (in two sentences)

An experiment you can't reproduce is a result you can't trust. Tracking creates the immutable record — code version, data version, hyperparameters, environment, metrics — that makes "we improved accuracy by 4%" a verifiable claim rather than a notebook screenshot.

## Step 1 — What to log (minimum set)

| Category | Examples | Why |
|---|---|---|
| Git commit SHA | `mlflow.log_param("git_sha", get_git_sha())` | Pin the code version to the run |
| Dataset version | S3 URI + ETag, DVC hash, or dataset fingerprint | Pin the data; different data = different experiment |
| Hyperparameters | All of them — not just the ones you varied | Future you needs to reproduce the run |
| Environment | Python version, key package versions | Dependency drift changes results |
| Metrics (per epoch) | Train loss, val loss, val metric | Enables learning curve comparison, not just final score |
| Artifacts | Model checkpoint, confusion matrix, feature importances | Complete provenance |

**MLflow instrumentation template:**
```python
import mlflow

mlflow.set_experiment("churn-prediction-v2")

with mlflow.start_run(run_name=f"lgbm-{trial.number}"):
    mlflow.log_params({
        "git_sha": get_git_sha(),
        "dataset_version": dataset.version,
        "model_type": "lightgbm",
        "n_estimators": params["n_estimators"],
        "learning_rate": params["learning_rate"],
    })

    model = train(params, X_train, y_train)

    mlflow.log_metrics({
        "val_auc": val_auc,
        "val_pr_auc": val_pr_auc,
        "train_auc": train_auc,
    })

    mlflow.sklearn.log_model(model, "model",
        signature=mlflow.models.infer_signature(X_val, model.predict(X_val)),
        input_example=X_val.iloc[:3])
```

## Step 2 — Run comparison workflow

When comparing two runs, follow this order to avoid cherry-picking:

1. **Define the evaluation metric before comparing** — choose the primary metric (e.g., val AUC) and the threshold (e.g., 0.5% improvement = meaningful) before looking at results.
2. **Compare on the held-out test set only once** — use val for tuning; the test set is touched once per candidate, not once per run.
3. **Check for overfitting**: `train_metric >> val_metric` is a warning sign even if val_metric is good.
4. **Compare learning curves**: a model that converges earlier with the same final val metric is strictly better.
5. **Run the `applied-statistics` significance check** (bootstrap or paired t-test) before declaring the new model "better."

## Step 3 — Model registry promotion workflow

```
[Experiment runs] → [Staging registry] → [Champion vs Challenger test] → [Production registry]
```

**MLflow model lifecycle:**

```python
client = mlflow.tracking.MlflowClient()

# Register from a run
result = mlflow.register_model(
    model_uri=f"runs:/{run_id}/model",
    name="churn-prediction"
)

# Promote to staging after validation
client.transition_model_version_stage(
    name="churn-prediction",
    version=result.version,
    stage="Staging",
    archive_existing_versions=False
)

# Promote to production only after:
# 1. Shadow/canary traffic test passes
# 2. Statistical significance check passes
client.transition_model_version_stage(
    name="churn-prediction",
    version=result.version,
    stage="Production",
    archive_existing_versions=True  # demote old version to Archived
)
```

## Step 4 — Team conventions to standardize

| Convention | Recommendation |
|---|---|
| Experiment naming | `{team}-{problem}-v{n}` e.g. `risk-churn-v3` |
| Run naming | Descriptive: `lgbm-lr0.01-depth6` not `run_42` |
| Tags | Always tag `env` (dev/ci/prod) and `triggered_by` (manual/ci) |
| Test-set evaluation | One function, called once per candidate; no loops over test set |
| Model signature | Always log an `input_example` — serves as the schema contract for the serving endpoint |

## Step 5 — CI integration

On every PR that touches `training/` or `features/`:

```yaml
- name: Run training smoke test
  run: |
    python train.py \
      --dataset tests/fixtures/sample_dataset.parquet \
      --max-rows 1000 \
      --experiment ci-smoke \
      --run-name "pr-${{ github.sha }}"

- name: Assert min metric threshold
  run: |
    python scripts/assert_min_metric.py \
      --experiment ci-smoke \
      --metric val_auc \
      --min-value 0.70
```

The CI run uses a sample dataset; the full training run is triggered separately (not on every PR).

## Pitfalls

- **Logging only the final metric, not per-epoch metrics** — you can't diagnose overfitting or compare convergence speed without the training curve.
- **Sharing one experiment across all team members' runs** — use per-developer experiment namespaces; shared experiments become a wall of unattributed runs.
- **Not logging the dataset version** — changing a feature, fixing a bug in preprocessing, and retraining without bumping the dataset version makes runs incomparable.
- **Evaluating on the test set repeatedly** — each evaluation on the test set is an implicit optimization step; the test set is a one-shot oracle, not a validation loop.
- **Skipping the model signature** — a model without a signature has no enforced input schema; a serving endpoint receiving mismatched features fails silently or produces garbage predictions.
