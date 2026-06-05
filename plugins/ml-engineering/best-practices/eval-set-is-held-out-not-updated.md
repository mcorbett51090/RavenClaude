# The evaluation set is held out permanently — updating it invalidates the metric

**Status:** Absolute rule
**Domain:** MLOps / validation
**Applies to:** `ml-engineering`

---

## Why this exists

The test/evaluation set exists to measure model performance on data the model has never seen. Its entire value depends on it being genuinely unseen by the model — and by the engineer making hyperparameter choices. The moment you look at test-set performance and tune something, the test set becomes an implicit part of training. Adding new data to the test set to "improve its representativeness" while iterating on the model compounds this: the new data was selected after seeing what the model got wrong, which is evaluation leakage. A contaminated test set produces an inflated metric that is a production disappointment with a delay.

## How to apply

Split the data once, before any modeling, and treat the test set as immutable. The test set is evaluated once — at the end, on the final model version. Never re-sample, augment, or replace it mid-iteration.

```python
# Correct: split once at the start of the project
from sklearn.model_selection import train_test_split

# Time-ordered data: use temporal split
df_sorted = df.sort_values("event_timestamp")
cutoff = int(len(df_sorted) * 0.8)
train_val = df_sorted.iloc[:cutoff]
test = df_sorted.iloc[cutoff:]   # saved to disk — do not touch until final eval

# Random data: stratified split
train_val, test = train_test_split(df, test_size=0.2, stratify=df["label"], random_state=42)
test.to_parquet("data/test_set_frozen.parquet")  # frozen — DO NOT modify

# All iteration happens on train_val only
# Cross-validate on train_val; final evaluation on test once, at promotion
```

```python
# Final evaluation — called once, at model promotion time
def evaluate_final_model(model, test_path: str) -> dict:
    """Call this exactly once per candidate model version."""
    test = pd.read_parquet(test_path)
    predictions = model.predict(test[FEATURE_COLS])
    return {
        "auc_roc": roc_auc_score(test["label"], predictions),
        "eval_date": str(pd.Timestamp.now(tz="UTC")),
        "test_set_hash": hashlib.md5(open(test_path, "rb").read()).hexdigest(),
    }
```

**Do:**
- Save the test set to immutable storage (S3 with object lock, DVC-pinned) at project start.
- Record the test-set content hash in the model registry entry — it proves which data was used.
- Use cross-validation on train+val for all iteration and hyperparameter search; the test set is the final checkpoint.

**Don't:**
- Look at test set predictions during development to guide design decisions — that's leakage.
- Add data to the test set after seeing model errors on it ("let me add more examples of this failure mode").
- Use the test set for hyperparameter tuning, even indirectly (e.g., grid search with test-set feedback).

## Edge cases / when the rule does NOT apply

When the world changes significantly (a major distribution shift, a product change that makes historical data irrelevant), it may be necessary to construct a new test set. Document the decision with the rationale, date, and the new test set's data range. The old metric and new metric are not directly comparable.

## See also

- [`../agents/training-pipeline-engineer.md`](../agents/training-pipeline-engineer.md) — owns validation methodology and leakage prevention.
- [`./validate-without-leakage.md`](./validate-without-leakage.md) — the held-out eval set is the ultimate leakage protection.

## Provenance

Codifies the "test set is sacred" principle from Andrew Ng's Machine Learning Yearning and the ISLR (Introduction to Statistical Learning) guidance on train/test contamination.

---

_Last reviewed: 2026-06-05 by `claude`_
