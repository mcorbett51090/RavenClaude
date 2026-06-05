# Define and monitor the freshness SLA for online features before serving

**Status:** Absolute rule
**Domain:** MLOps / feature stores
**Applies to:** `ml-engineering`

---

## Why this exists

A model served online is only as good as the features it sees at inference time. When the online feature store falls behind — because a pipeline is delayed, a materialization job failed, or a source stream is lagging — the model may receive stale features that no longer reflect the user's current state. Without a defined freshness SLA and monitoring, the model silently degrades: it's predicting on yesterday's user behavior while showing today's pricing. Training-serving skew via stale features is as damaging as skew via different computation.

## How to apply

For each feature set used in online serving, define the maximum acceptable staleness (freshness SLA) and set up a monitor that alerts when the feature store falls behind.

```python
# Feature freshness monitor — runs every 5 minutes
# Checks the `user_recent_activity` feature set
import feast
from datetime import datetime, timezone, timedelta

store = feast.FeatureStore(repo_path=".")

def check_feature_freshness():
    # Get the timestamp of the most recently materialized data
    entity_df = pd.DataFrame({"user_id": ["sentinel_user_1"], "event_timestamp": [datetime.now(timezone.utc)]})
    features = store.get_online_features(
        features=["user_activity_stats:last_session_ts"],
        entity_rows=[{"user_id": "sentinel_user_1"}],
    ).to_dict()

    last_session_ts = features["last_session_ts"][0]
    staleness = datetime.now(timezone.utc) - last_session_ts
    freshness_sla = timedelta(minutes=15)  # defined SLA: features must be < 15 min old

    if staleness > freshness_sla:
        alert(f"Feature staleness {staleness} exceeds SLA {freshness_sla}")
        # Optionally: fall back to a safe default or stale-feature flag for the model
```

```yaml
# Feature freshness SLA document (per feature set)
feature_sets:
  user_activity_stats:
    source: kafka_stream
    materialization_schedule: "every 5 minutes"
    freshness_sla: "15 minutes"
    alert_threshold: "20 minutes"
    fallback_on_stale: "use previous valid value"
    owner: "ml-platform-team"
```

**Do:**
- Define the freshness SLA in the feature store configuration, not just in a wiki.
- Monitor actual feature staleness using a sentinel entity or a watermark check, not just pipeline run time.
- Define a model fallback behavior when features are stale (use cached value, fallback model, or fail-safe default).

**Don't:**
- Assume feature pipelines always run on schedule — network, cluster, and source failures make late materialization common.
- Mix fresh and stale features in the same inference request without flagging the request as stale.
- Set the freshness SLA tighter than the materialization pipeline can reliably achieve.

## Edge cases / when the rule does NOT apply

Batch inference (pre-computed scores) has a different freshness model — the staleness is the time since the last batch run, and the SLA is expressed as "scores recomputed at least every N hours." Apply the same monitoring principle: alert when the last batch run exceeded the SLA.

## See also

- [`../agents/training-pipeline-engineer.md`](../agents/training-pipeline-engineer.md) — owns the feature store and materialization pipelines.
- [`./feature-store-is-the-consistency-contract.md`](./feature-store-is-the-consistency-contract.md) — the feature store is only a consistency contract if freshness is monitored and enforced.

## Provenance

Codifies feature freshness SLA practices from Feast documentation (feast.dev/docs) and the real-time ML serving reliability patterns described in Chip Huyen's "Designing Machine Learning Systems."

---

_Last reviewed: 2026-06-05 by `claude`_
