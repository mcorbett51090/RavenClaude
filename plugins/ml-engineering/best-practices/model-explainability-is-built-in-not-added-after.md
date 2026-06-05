# Build model explainability into the pipeline — retrofitting it is harder and less trusted

**Status:** Pattern
**Domain:** MLOps / model governance
**Applies to:** `ml-engineering`

---

## Why this exists

Explainability is often treated as an add-on requested after a model has been deployed and someone asks "why did it predict X for user Y?" Retrofitting SHAP or LIME after the fact is possible but produces explanations that are slower to compute (no precomputation), harder to trust (the explanation model may not reflect the original training distribution), and not integrated into the monitoring or drift pipeline. Building explainability into the training pipeline — computing feature importances and example explanations at training time, logging them to the registry — makes them immediately available for debugging, auditing, and stakeholder communication.

## How to apply

Compute global feature importances and a sample of per-prediction explanations as part of the model training and registration step.

```python
# Training pipeline: compute and log SHAP values at training time
import shap, mlflow

# After training the model
explainer = shap.TreeExplainer(model)          # or shap.Explainer(model) for any model type
shap_values = explainer.shap_values(val_df[FEATURE_COLS])

# Global feature importance
feature_importance = pd.DataFrame({
    "feature": FEATURE_COLS,
    "mean_abs_shap": np.abs(shap_values).mean(axis=0),
}).sort_values("mean_abs_shap", ascending=False)

with mlflow.start_run(run_id=current_run_id):
    mlflow.log_dict(feature_importance.to_dict(orient="records"), "feature_importance.json")

    # Save a SHAP summary plot as an artifact
    shap.summary_plot(shap_values, val_df[FEATURE_COLS], show=False)
    plt.savefig("shap_summary.png", bbox_inches="tight")
    mlflow.log_artifact("shap_summary.png")

    # Save the explainer for serving-time use
    mlflow.pyfunc.log_model(
        artifact_path="model_with_explainer",
        python_model=ModelWithExplainer(model, explainer),
    )
```

```python
# At inference time: generate an explanation for a specific prediction
def predict_with_explanation(features: dict) -> dict:
    shap_values = explainer.shap_values(pd.DataFrame([features]))
    return {
        "prediction": model.predict(pd.DataFrame([features]))[0],
        "top_factors": get_top_shap_features(shap_values, features, n=3),
    }
```

**Do:**
- Compute global feature importances for every registered model version — the registry entry is incomplete without them.
- Log per-prediction SHAP explanations for a sample of the validation set to the experiment tracker.
- Store the explainer object alongside the model so serving-time explanations use the same object as training-time.

**Don't:**
- Run SHAP post-hoc against a stale copy of the validation data — use the same validation set used to evaluate the model.
- Present SHAP values as causal explanations — they explain the model's prediction, not the world.
- Skip explainability for "simple" models — a logistic regression's coefficients still need to be logged and interpreted correctly.

## Edge cases / when the rule does NOT apply

Deep learning models (transformers, large CNNs) have high SHAP computation cost. Use gradient-based attribution (Integrated Gradients, GradCAM) or a surrogate explainer, and compute on a sample. The principle stands — compute and log at training time, not on demand.

## See also

- [`../agents/ml-platform-architect.md`](../agents/ml-platform-architect.md) — owns the model governance framework including explainability requirements.
- [`./model-cards-document-intended-use.md`](./model-cards-document-intended-use.md) — the model card's performance section is enriched by the feature importance logged here.

## Provenance

Codifies SHAP (Lundberg & Lee, 2017) and the ML explainability best practices from Responsible AI practices (Google AI), grounded in the ml-platform-architect's governance and the EU AI Act Article 13 transparency requirements for high-risk AI systems.

---

_Last reviewed: 2026-06-05 by `claude`_
