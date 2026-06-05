# Default to batch inference — move to online serving only when latency demands it

**Status:** Pattern
**Domain:** MLOps / model serving
**Applies to:** `ml-engineering`

---

## Why this exists

Online serving (real-time REST endpoint) costs significantly more than batch inference in compute, infrastructure complexity, and operational overhead. It requires always-on instances, autoscaling, SLO monitoring, and low-latency serving optimization. Most ML use cases don't need sub-second predictions for each request — they need predictions available by the time a user or system acts on them. A batch job that scores users overnight and writes results to a database is simpler, cheaper, and more reliable than an online endpoint, and is the right default for any use case where the prediction doesn't need to react to the current request in real time.

## How to apply

Evaluate the latency requirement explicitly before choosing serving mode. If the question "can the prediction be pre-computed before the user needs it?" has a "yes," use batch inference.

| Use case | Latency requirement | Recommended mode |
|---|---|---|
| Fraud detection on a transaction | < 200ms, real-time | Online endpoint |
| Personalized homepage recommendations | Available on page load, pre-computed | Batch — score nightly, serve from cache |
| Churn prediction for CRM campaigns | Ready before campaign send | Batch — score weekly |
| Autocomplete / search ranking | < 50ms per keystroke | Online endpoint |
| Email subject line personalization | Ready before send time | Batch — score at schedule |
| Credit risk assessment | Minutes to hours acceptable | Batch or async online |

```python
# Batch inference job: score all active users and write to a feature/result store
# Run as a scheduled job (Airflow, Vertex Pipelines, SageMaker Processing)
import pandas as pd
import mlflow

def run_batch_inference(data_uri: str, model_uri: str, output_uri: str):
    model = mlflow.pyfunc.load_model(model_uri)
    df = pd.read_parquet(data_uri)

    # Batch predict — much more efficient than per-row online calls
    df["churn_score"] = model.predict(df[FEATURE_COLS])
    df["scored_at"] = pd.Timestamp.now(tz="UTC")

    df[["user_id", "churn_score", "scored_at"]].to_parquet(output_uri, index=False)
```

**Do:**
- Start with batch; move to online only when latency requirements explicitly require it.
- Use a result store (Redis, DynamoDB, BigTable, or a feature store) to make batch predictions low-latency to read, even if they're computed in batch.
- Reuse the same registered model artifact for batch and online serving — don't diverge the model binary.

**Don't:**
- Build an online endpoint "because it's more modern" without a latency requirement that demands it.
- Call an online endpoint inside a batch job — that's neither: it has the cost of online and the latency slack of batch; use the SDK directly instead.
- Accept online serving infrastructure complexity as the default for new models.

## Edge cases / when the rule does NOT apply

Models that must react to data that isn't available until request time (the user's current session, a real-time transaction) cannot be pre-computed and require online or async-online serving.

## See also

- [`../agents/model-serving-engineer.md`](../agents/model-serving-engineer.md) — owns the serving mode selection and the serving infrastructure.
- [`./optimize-serving-to-a-budget.md`](./optimize-serving-to-a-budget.md) — if online serving is required, optimize it to a latency/cost budget.

## Provenance

Codifies the batch vs. online serving trade-offs from Chip Huyen's "Designing Machine Learning Systems" Chapter 7 and Google Cloud's ML serving best practices.

---

_Last reviewed: 2026-06-05 by `claude`_
