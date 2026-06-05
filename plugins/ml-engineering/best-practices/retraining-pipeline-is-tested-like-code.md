# Test the retraining pipeline — an untested pipeline fails silently in production

**Status:** Absolute rule
**Domain:** MLOps / training pipelines
**Applies to:** `ml-engineering`

---

## Why this exists

A retraining pipeline that only runs monthly on a schedule is the most under-tested code in the ML stack. It runs rarely, so failures accumulate between runs and surface only when a retrain is urgently needed (after drift is detected). Common failures: the feature store schema changed, a data source moved, a new library version broke a preprocessing step, or the model evaluation metric comparison logic has a bug. Testing the retraining pipeline in CI — on a small synthetic dataset — catches these failures continuously, not at the worst moment.

## How to apply

Structure the training pipeline as testable code units and add a smoke-test run to CI that trains on a tiny synthetic dataset (100–1000 rows) and verifies the pipeline completes and produces a model with the expected shape.

```python
# tests/test_training_pipeline.py
import pytest, pandas as pd, numpy as np
from src.pipeline import run_training_pipeline

@pytest.fixture
def synthetic_training_data(tmp_path):
    """Generate a tiny synthetic dataset for pipeline smoke tests."""
    np.random.seed(42)
    n = 200
    df = pd.DataFrame({
        "user_id": range(n),
        "feature_a": np.random.randn(n),
        "feature_b": np.random.randint(0, 10, n),
        "label": np.random.binomial(1, 0.3, n),
        "event_timestamp": pd.date_range("2026-01-01", periods=n, freq="1h"),
    })
    path = tmp_path / "train.parquet"
    df.to_parquet(path)
    return str(path)

def test_pipeline_completes_and_produces_model(synthetic_training_data, tmp_path):
    """Smoke test: the full pipeline runs end-to-end on synthetic data."""
    result = run_training_pipeline(
        data_path=synthetic_training_data,
        output_path=str(tmp_path / "model"),
        max_rows=200,    # override to prevent accidental full data load
    )

    assert result.status == "success"
    assert result.model_path is not None
    assert result.metrics["val_auc"] > 0.4   # sanity check — better than random
    assert result.metrics["val_auc"] < 1.0   # sanity check — not suspiciously perfect

def test_pipeline_fails_gracefully_on_empty_data(tmp_path):
    """Pipeline should raise a clear error, not a cryptic exception."""
    empty_df = pd.DataFrame(columns=["user_id", "feature_a", "feature_b", "label"])
    path = tmp_path / "empty.parquet"
    empty_df.to_parquet(path)
    with pytest.raises(ValueError, match="Training data is empty"):
        run_training_pipeline(data_path=str(path), output_path=str(tmp_path / "model"))
```

**Do:**
- Add the pipeline smoke test to the CI suite so it runs on every PR touching pipeline code.
- Test error paths explicitly (empty data, missing features, downstream service unavailable).
- Use synthetic data in CI — never pull production data into the CI environment.
- Pin the synthetic dataset in version control so test failures are deterministic.

**Don't:**
- Skip pipeline tests because "it's just scripts, not application code."
- Use the full production dataset in CI tests — use a tiny representative sample.
- Only test the model quality on synthetic data (too small to be meaningful) — test that the pipeline completes and produces a valid artifact.

## Edge cases / when the rule does NOT apply

Computationally expensive pipeline stages (large-scale distributed training) cannot run in CI on full scale. Test them with a tiny-data smoke run in CI and a staging-environment full run before production promotion.

## See also

- [`../agents/training-pipeline-engineer.md`](../agents/training-pipeline-engineer.md) — owns the training pipeline code and its CI integration.
- [`./reproducibility-is-the-floor.md`](./reproducibility-is-the-floor.md) — a tested pipeline is a prerequisite for reliable reproducibility.

## Provenance

Codifies the "test your ML code like application code" principle from Made With ML (madewithml.com) and Google's MLOps maturity model (Level 2: automated training pipelines with CI testing).

---

_Last reviewed: 2026-06-05 by `claude`_
