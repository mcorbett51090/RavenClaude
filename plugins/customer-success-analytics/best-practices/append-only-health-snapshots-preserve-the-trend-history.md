# Append-only health snapshots preserve the trend history

**Status:** Absolute rule
**Domain:** CS data modeling
**Applies to:** `customer-success-analytics`

---

## Why this exists

A health snapshot table that upserts in place — updating today's row with new values — destroys the history. Once the history is gone it cannot be reconstructed: there is no way to answer "was this account declining three months before it churned?" or "did our tuning change in March correlate with better renewal outcomes?", because the data that would answer those questions was overwritten. The append-only pattern (one new row per account per day, never deleted or updated) is the only design that keeps the trend history intact for churn-signal validation, tier-tuning back-tests, and renewal-outcome attribution.

## How to apply

Design `fct_account_health_snapshot` as an append-only fact table with a composite primary key of `(account_key, snapshot_date)`. No UPDATE or DELETE statements run against this table in production.

```sql
-- Correct: append-only snapshot
CREATE TABLE fct_account_health_snapshot (
  account_key       INT        NOT NULL,
  snapshot_date     DATE       NOT NULL,
  csp_health_score  FLOAT,
  usage_trend_30d   FLOAT,
  support_spike_flag BOOLEAN,
  tier              VARCHAR(10),
  tier_drivers      JSON,
  -- ... other signals
  PRIMARY KEY (account_key, snapshot_date)
);

-- Daily load pattern:
INSERT INTO fct_account_health_snapshot
SELECT account_key, CURRENT_DATE, ...
FROM source_signals
WHERE account_key NOT IN (
  SELECT account_key FROM fct_account_health_snapshot WHERE snapshot_date = CURRENT_DATE
);
-- No UPDATE. No DELETE.

-- Wrong: upsert-in-place pattern (destroys history):
-- INSERT ... ON CONFLICT (account_key) DO UPDATE SET ...
```

**Do:**
- Partition or cluster the table by `snapshot_date` for query performance as the table grows.
- Keep at minimum 12 months of history; 24+ months is needed for annual renewal-cycle back-tests.
- Instrument a daily row-count check to detect missed snapshot runs before they create gaps.

**Don't:**
- Allow UPDATE statements on historical snapshot rows — even for retroactive corrections (use a correction row with a flag instead).
- Model the snapshot as a slowly-changing dimension type 1 (latest-only) — that is the upsert anti-pattern.
- Truncate and reload the snapshot table as part of a refresh job.

## Edge cases / when the rule does NOT apply

Storage cost can become a concern for very large account books with high signal cardinality over long windows. The solution is to thin the cadence for accounts that have been Green and stable for a sustained period (e.g., weekly snapshot instead of daily) — not to convert to upsert. Even thinned, never delete historical rows.

## See also

- [`../agents/cs-analytics-architect.md`](../agents/cs-analytics-architect.md) — designs and owns the health snapshot mart schema.
- [`./direction-beats-absolute-level-model-trend-columns-explicitly.md`](./direction-beats-absolute-level-model-trend-columns-explicitly.md) — the companion rule that depends on this history being preserved.

## Provenance

Codifies the plugin's §4 house opinion #8 ("Append-only health snapshots"). The upsert-in-place error is the most common data-modeling mistake in first-generation CS health systems; it typically goes unnoticed until the team tries to back-test a tier-tuning change and discovers the history is gone.

---

_Last reviewed: 2026-06-05 by `claude`_
