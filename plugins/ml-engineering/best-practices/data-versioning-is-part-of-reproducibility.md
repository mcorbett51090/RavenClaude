# Version training data alongside model code — a model is the product of both

**Status:** Absolute rule
**Domain:** MLOps / reproducibility
**Applies to:** `ml-engineering`

---

## Why this exists

"Reproducibility is the floor" means versioning code, config, and environment — but the model is equally a function of the training data. A model experiment that stores the code version but not the data version is only half-reproducible: you cannot rebuild the model six months later if the training dataset has been modified or overwritten. Data versioning is the missing piece that completes the reproducibility contract and enables honest debugging ("did the model change because the code changed or because the data changed?").

## How to apply

Use a data versioning tool (DVC, Delta Lake, LakeFormation versions, or immutable S3 prefixes with date/hash) to create a stable, addressable version of every training dataset. Link each model version in the registry to its training data version.

```python
# DVC: track the training dataset version
# dvc.yaml — pipeline with versioned data input
stages:
  preprocess:
    cmd: python src/preprocess.py
    deps:
      - data/raw/              # DVC-tracked raw data
      - src/preprocess.py
    outs:
      - data/processed/train.parquet
      - data/processed/val.parquet

  train:
    cmd: python src/train.py
    deps:
      - data/processed/train.parquet
      - data/processed/val.parquet
      - src/train.py
      - params.yaml
    outs:
      - models/candidate/      # tracked by DVC + logged to MLflow
```

```python
# MLflow: log the data version alongside the model version
import mlflow

with mlflow.start_run():
    mlflow.log_param("data_version", "v2026-06-05-abc123")     # DVC commit hash
    mlflow.log_param("data_path", "s3://my-bucket/data/v42/")
    mlflow.log_param("training_rows", len(train_df))
    mlflow.log_metric("val_f1", val_f1)
    mlflow.sklearn.log_model(model, "model")
```

**Do:**
- Store training data in immutable, content-addressed storage (S3 with versioning, Delta Lake time travel, or DVC).
- Log the data version hash/URI to the experiment tracker alongside hyperparameters and metrics.
- Tag the data snapshot before training starts — not after; post-hoc tagging is unreliable.

**Don't:**
- Overwrite training data in place; use append-only or versioned writes.
- Track only the data path — track the content hash (DVC `md5`, S3 object version ID) to detect silent modifications.
- Log "latest" as the data version; log the immutable identifier.

## Edge cases / when the rule does NOT apply

Streaming/online-learning models where training data is continuous require a window specification (start time, end time, and any applied filters) as the "version" instead of a static snapshot. Log the window parameters to the experiment tracker.

## See also

- [`../agents/training-pipeline-engineer.md`](../agents/training-pipeline-engineer.md) — owns the training pipeline and reproducibility stack.
- [`./reproducibility-is-the-floor.md`](./reproducibility-is-the-floor.md) — data versioning is a required component of the reproducibility floor.

## Provenance

Codifies DVC (dvc.org) data versioning best practices and MLflow experiment tracking guidance, grounded in the training-pipeline-engineer's reproducibility mandate.

---

_Last reviewed: 2026-06-05 by `claude`_
