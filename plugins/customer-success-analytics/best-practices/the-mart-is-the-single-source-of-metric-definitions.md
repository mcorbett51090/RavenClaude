# The mart is the single source of metric definitions

**Status:** Absolute rule
**Domain:** CS data architecture
**Applies to:** `customer-success-analytics`

---

## Why this exists

When a CS analyst writes a custom SQL query in the BI tool to compute "monthly active accounts," and the data engineer has a different definition in the pipeline, and the CSP dashboard has its own definition — three different numbers surface in three different systems. The first time the CS leader asks "which number is right?" the team loses a week reconciling definitions instead of acting on the data. The only sustainable fix is one definition per metric, owned by the mart layer, served by every downstream surface. No raw SQL in the BI tool. No per-source live API calls at query time. Every published metric reads the mart.

## How to apply

Define every CS metric as a mart-layer column or view with a documented formula, data source, and grain. BI surfaces consume mart views; they never re-derive metrics using raw source tables.

```sql
-- Correct pattern: metric defined once in mart view
CREATE VIEW v_account_health_kpis AS
SELECT
  account_key,
  snapshot_date,
  usage_trend_30d,               -- definition: see docs/metrics/usage_trend_30d.md
  days_to_renewal,
  renewal_risk_tier,
  csp_health_score,
  composite_tier
FROM fct_account_health_snapshot
WHERE snapshot_date = CURRENT_DATE - 1;

-- BI tool consumes: SELECT * FROM v_account_health_kpis WHERE composite_tier = 'RED'

-- Wrong pattern: BI tool re-derives usage trend from raw source tables:
-- SELECT account_id,
--   (SELECT AVG(logins) FROM raw.logins WHERE ... ) AS usage_today,
--   ...
-- This is a second definition — a metric conflict waiting to happen.
```

**Do:**
- Create a documented metric catalog (even a simple markdown file) that maps each metric name to its mart column, formula, grain, and refresh cadence.
- Add each new metric to the mart schema as an explicit column before adding it to a dashboard.
- Gate new dashboard requests: the BI author must identify the mart column before building.

**Don't:**
- Allow BI-layer computed columns that re-derive metrics from raw source tables.
- Let different dashboards use different SQL to compute the "same" metric.
- Leave metric definitions only in BI tool expressions that are invisible to the data team.

## Edge cases / when the rule does NOT apply

Exploratory analysis (ad-hoc queries during an investigation) may reasonably query raw tables — the rule applies to published, production metrics that CS leaders act on. For very early-stage implementations where the mart schema is not yet stable, document the interim definitions explicitly and flag them as "pre-mart — definition subject to change."

## See also

- [`../agents/cs-analytics-architect.md`](../agents/cs-analytics-architect.md) — owns the mart schema and metric definitions.
- [`./append-only-health-snapshots-preserve-the-trend-history.md`](./append-only-health-snapshots-preserve-the-trend-history.md) — the companion rule on the snapshot foundation the mart depends on.

## Provenance

Codifies the plugin's §4 house opinion #12 ("The mart is the single source of metric definitions"). The multiple-definition anti-pattern is the leading cause of CS-leader distrust in analytics systems; the mart-first discipline is the standard prevention.

---

_Last reviewed: 2026-06-05 by `claude`_
