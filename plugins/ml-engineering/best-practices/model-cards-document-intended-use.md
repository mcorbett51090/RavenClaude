# Write a model card before deploying — document intended use, limits, and risks

**Status:** Pattern
**Domain:** MLOps / model governance
**Applies to:** `ml-engineering`

---

## Why this exists

A model without a model card is a black box deployed on trust. When it produces a surprising prediction, the on-call engineer has no documented baseline for "is this expected behavior?" When a product manager asks "can we use this model for X?", there's no answer without re-running the evaluation. Model cards encode the answers to these questions at deploy time, before they become urgent. They also provide the evidence base for the `ravenclaude-core/security-reviewer` to evaluate risk and the `applied-statistics` team to audit the evaluation methodology.

## How to apply

Write a model card for every model before it enters the registry as a production candidate. The card lives in the repository alongside the model code and is linked from the registry entry.

```markdown
# Model Card: Customer Churn Predictor v3.2

## Model details
- **Type:** Gradient Boosted Trees (XGBoost)
- **Task:** Binary classification — 30-day churn prediction
- **Training data:** 18 months of subscription events, 2024-01 to 2025-06
- **Registry:** ml-registry/churn-predictor@v3.2
- **Owners:** ml-team@example.com

## Intended use
- **Intended users:** CRM system (automated), CS team (decision support)
- **Intended use cases:** Proactive retention campaigns for high-risk accounts
- **Out-of-scope uses:** Legal decisions, employment, credit scoring, healthcare

## Performance
| Metric | Value | Population |
|---|---|---|
| AUC-ROC | 0.87 | Full eval set |
| Precision @ 0.5 threshold | 0.73 | Full eval set |
| AUC-ROC | 0.82 | Enterprise accounts (>$10k ARR) |

## Known limitations and risks
- Degrades on accounts < 30 days old (fewer than 10 events in training)
- Not validated on non-English-language markets — do not deploy in EMEA without re-evaluation
- Sensitive to data drift in billing event schema; monitor `billing.event_type` distribution

## Evaluation methodology
- Time-based train/val/test split; no future leakage
- Hold-out test set evaluated once; val set used for hyperparameter search
- Statistical significance test: see experiment run `mlflow/runs/abc123`
```

**Do:**
- Write the model card before promotion to prod, not after the incident that reveals the limitation.
- Include out-of-scope uses explicitly — these are as important as intended uses for liability and trust.
- Link the model card from the registry entry so it's co-located with the model artifact.
- Update the model card when a new version is deployed; version the card alongside the model.

**Don't:**
- Write a model card that only describes the happy-path performance — the limitations and risks section is the most valuable part.
- Let the model card live only in a wiki separate from the registry — it must be discoverable from the artifact.
- Use model cards as a formality after deployment; they are a pre-deployment requirement.

## Edge cases / when the rule does NOT apply

Prototype models deployed for A/B testing (not production decisions) can use a lightweight card (one-page summary). Full cards are required for any model making decisions with user-visible consequences.

## See also

- [`../agents/ml-platform-architect.md`](../agents/ml-platform-architect.md) — owns the model governance framework and registry requirements.
- [`./registry-is-the-source-of-truth.md`](./registry-is-the-source-of-truth.md) — the model card is a required attribute of any registry entry.

## Provenance

Codifies the Model Cards for Model Reporting paper (Mitchell et al., 2019, Google) and Google's model card toolkit documentation, grounded in the ml-platform-architect's governance mandate.

---

_Last reviewed: 2026-06-05 by `claude`_
