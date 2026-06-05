# Log every hyperparameter search run — manual tuning is unreproducible

**Status:** Absolute rule
**Domain:** MLOps / experiment tracking
**Applies to:** `ml-engineering`

---

## Why this exists

Manual hyperparameter tuning — changing a value in a script, running it, writing down the result in a spreadsheet — produces experiments that can't be reproduced because there's no machine-readable record of what was tried. Six weeks later, "why is learning_rate=0.003?" has no answer. Logged hyperparameter searches (MLflow, Weights & Biases, Optuna with a backend) produce an auditable record of every trial: the parameters tried, the metrics achieved, the configuration that was promoted, and the reasoning (or automated criterion) for the choice.

## How to apply

Use an experiment tracker (MLflow, W&B, Comet) for all hyperparameter search. If using an HPO library (Optuna, Ray Tune, Hyperopt), configure it to log to the tracker automatically.

```python
# Optuna with MLflow logging — every trial logged automatically
import optuna
import mlflow

def objective(trial):
    # MLflow autolog captures all parameters and metrics
    with mlflow.start_run(nested=True, run_name=f"trial-{trial.number}"):
        lr = trial.suggest_float("learning_rate", 1e-4, 1e-1, log=True)
        depth = trial.suggest_int("max_depth", 3, 10)
        n_estimators = trial.suggest_int("n_estimators", 50, 500)

        mlflow.log_params({
            "learning_rate": lr,
            "max_depth": depth,
            "n_estimators": n_estimators,
        })

        model = train_model(lr=lr, max_depth=depth, n_estimators=n_estimators)
        val_auc = evaluate(model, val_df)

        mlflow.log_metric("val_auc", val_auc)
        return val_auc

# Parent run captures the best configuration
with mlflow.start_run(run_name="hpo-search-v3"):
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=50)

    best_params = study.best_params
    mlflow.log_params({f"best_{k}": v for k, v in best_params.items()})
    mlflow.log_metric("best_val_auc", study.best_value)
```

**Do:**
- Tag the winning trial in the tracker and link it to the registered model version.
- Log the HPO search space (bounds and distributions) as params on the parent run.
- Use the tracker's comparison view to document the rationale for the chosen hyperparameters in the model card.

**Don't:**
- Run grid search or random search from a notebook without logging each run to the tracker.
- Delete intermediate HPO trials from the tracker to "clean up" — they are the audit trail.
- Use a different seed for the final training run than the winning trial — the trial result won't match.

## Edge cases / when the rule does NOT apply

Foundation model fine-tuning with a fixed pretrained checkpoint and minimal hyperparameters (learning rate, warmup steps) may need only 5–10 logged runs to document the choices, not a full automated HPO sweep.

## See also

- [`../agents/training-pipeline-engineer.md`](../agents/training-pipeline-engineer.md) — owns experiment tracking and the hyperparameter search methodology.
- [`./track-every-experiment.md`](./track-every-experiment.md) — HPO runs are experiments; the same tracking discipline applies.

## Provenance

Codifies MLflow hyperparameter logging documentation and the Optuna-MLflow integration pattern, grounded in the training-pipeline-engineer's experiment-tracking mandate.

---

_Last reviewed: 2026-06-05 by `claude`_
