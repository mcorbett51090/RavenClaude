# Run new models in shadow mode before serving live traffic — validate before impact

**Status:** Pattern
**Domain:** MLOps / model deployment
**Applies to:** `ml-engineering`

---

## Why this exists

Offline evaluation metrics (AUC, F1, RMSE) measure model quality on historical data. They do not measure whether the model behaves correctly in the production serving path — with production features, production latency, and production input distributions. Shadow mode (running the new model in parallel with the current model, without affecting user experience) is the bridge: it validates that the model scores correctly at production scale, that its outputs are well-formed, and that its latency is acceptable, before a single user sees a prediction from it.

## How to apply

Deploy the candidate model as a shadow endpoint alongside the production model. Route a copy of every incoming request to the shadow endpoint. Log both sets of predictions for comparison. Do not serve the shadow predictions to users.

```python
# Shadow mode prediction service
import asyncio
from typing import Optional

async def score_request(features: dict, request_id: str) -> dict:
    """Score with production model; fire-and-forget shadow request."""
    # Production model scores synchronously — users see this
    prod_prediction = await prod_model.predict_async(features)

    # Shadow model scores asynchronously — does not block the response
    asyncio.create_task(
        shadow_score_and_log(features, prod_prediction, request_id)
    )

    return prod_prediction   # only the prod prediction is returned to the user

async def shadow_score_and_log(features, prod_pred, request_id):
    try:
        shadow_pred = await shadow_model.predict_async(features)
        # Log both for comparison — does not affect the user
        log_shadow_comparison(request_id, prod_pred, shadow_pred)
    except Exception as e:
        log_shadow_error(request_id, str(e))  # shadow errors are silent to the user
```

Shadow mode validation checklist:
- [ ] Output format is correct (expected schema, no nulls in required fields)
- [ ] Latency is within budget (P95 under the defined serving SLA)
- [ ] Prediction distribution is plausible (not all-zeros, not out-of-range)
- [ ] Error rate is acceptable (no unexpected exceptions)
- [ ] Agreement rate with the production model (regression guard)

**Do:**
- Run shadow mode for at least 24 hours of production traffic to cover diurnal patterns.
- Alert on shadow model errors or out-of-range predictions — but silently (don't affect the user).
- Compare shadow and production prediction distributions before promoting.

**Don't:**
- Skip shadow mode when you're "confident" in the offline metrics — offline confidence is exactly when shadow mode is most valuable.
- Run shadow mode with the same compute budget as production (it doesn't need to be cheap, but don't double the cost for a long-running shadow).
- Log user-identifiable data from shadow predictions beyond what's already logged for the production model.

## Edge cases / when the rule does NOT apply

Models where the prediction changes the input (reinforcement learning, bandit policies) cannot be shadow-tested in the same way — the shadow prediction would need to act to be meaningful. Use a dedicated replay environment or simulation instead.

## See also

- [`../agents/model-serving-engineer.md`](../agents/model-serving-engineer.md) — owns the shadow serving infrastructure and the rollout sequence.
- [`./roll-out-with-shadow-then-canary.md`](./roll-out-with-shadow-then-canary.md) — shadow mode is the first phase of the shadow→canary→full rollout.

## Provenance

Codifies the shadow mode deployment pattern from Martin Fowler's "Dark Launching" article and the model rollout safety recommendations from Google's MLOps practitioners guide.

---

_Last reviewed: 2026-06-05 by `claude`_
