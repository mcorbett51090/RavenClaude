# Direction beats absolute level — model trend columns explicitly

**Status:** Absolute rule
**Domain:** CS churn signal design
**Applies to:** `customer-success-analytics`

---

## Why this exists

A usage score of 65 on a given day is context-free. A usage score of 65 trending down from 85 three months ago is a churn signal. The absolute level tells you where the account is; the direction tells you where it is going. Churn is a trajectory problem, not a snapshot problem. Health models built on point-in-time absolute values miss the account that has been declining for 90 days but hasn't crossed a threshold yet, and reward an account that jumped to a high value recently but is already reverting. Trend columns must be first-class citizens in the mart schema, not derived at BI query time.

## How to apply

Materialize trend columns in the `fct_account_health_snapshot` table at the mart layer — do not compute slopes in the BI tool at query time. Include both the slope (direction and magnitude) and the delta from a reference window.

```sql
-- Trend columns to materialize in the health snapshot:
fct_account_health_snapshot (
  ...
  usage_score_current   FLOAT,          -- absolute level today
  usage_trend_30d       FLOAT,          -- slope or % change over 30 days
  usage_trend_90d       FLOAT,          -- slope over 90 days (longer view)
  usage_delta_vs_avg    FLOAT,          -- current vs account's own historical avg
  health_score_delta_30d FLOAT,         -- CSP health score direction last 30 days
  ...
)

-- Trend slope computation (SQL example):
usage_trend_30d = (usage_score_current - usage_score_30d_prior) / NULLIF(usage_score_30d_prior, 0)

-- Tier rule: weight trend direction, not absolute:
RED includes: usage_trend_30d < -0.30  -- account declining 30%+ in 30 days
```

**Do:**
- Materialize all trend columns in the mart; do not delegate to BI computed columns.
- Use both short-window (30d) and long-window (90d) trends to distinguish noise from signal.
- Use the account's own historical average as a baseline for delta, not a fixed population benchmark.

**Don't:**
- Build a health tier using only the current absolute value of each signal.
- Compute trends in the BI tool — this creates inconsistency and is not reusable by alert logic.
- Use a single trend window — a 30d spike and a 90d decline are different risk profiles.

## Edge cases / when the rule does NOT apply

For signals that are inherently binary or event-based (champion departure: yes/no; contract signed: yes/no), trend direction is not meaningful — use recency and frequency instead. For accounts in their first 60 days, a trend baseline doesn't exist; flag these as "new — trend pending" rather than computing a noisy trend from insufficient history.

## See also

- [`../agents/churn-signal-analyst.md`](../agents/churn-signal-analyst.md) — designs and validates the churn-leading signals and trend thresholds.
- [`./append-only-health-snapshots-preserve-the-trend-history.md`](./append-only-health-snapshots-preserve-the-trend-history.md) — the companion rule on why the snapshot must be append-only to support trend computation.

## Provenance

Codifies the plugin's §4 house opinion #3 ("Direction beats absolute level"). The absolute-value-only health model is the predominant design error in first-generation CS health scores; the fix is materializing the trend as a first-class column.

---

_Last reviewed: 2026-06-05 by `claude`_
