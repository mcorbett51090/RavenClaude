---
name: cs-metric-audit
description: "Audit the metrics published on a CS-health dashboard against the mart layer to identify inconsistencies, stale definitions, missing signals, and metrics that bypass the mart. Reach for this skill before a CS analytics rebuild, during a QBR preparation review, or when a CS leader reports that the numbers don't match what they expect."
---

# Skill: CS Metric Audit

A CS dashboard accumulates drift: metrics are added directly in the BI tool, signal definitions diverge from what was agreed, NULLs are silently converted to zeros, and trend columns get recomputed at query time instead of materialized. This skill surfaces the drift before it undermines CS team trust or produces a wrong renewal decision.

## When to reach for this skill

- A CS leader reports that numbers on the dashboard "don't look right."
- A rebuild or refresh of the CS health mart is planned.
- A QBR is upcoming and the team wants to verify the numbers are reliable before presenting to accounts.
- A new data source was added and the team needs to confirm it integrated cleanly.

## Step 1 — Inventory every metric on the CS dashboard

List every metric visible on the CS surface (the sort columns, the tier labels, the sub-indicators in the explainability panel). For each metric, record:

| Metric | Where computed | Source signal | Window | NULL handling | Last verified |
|---|---|---|---|---|---|
| [metric name] | [mart / BI-tool SQL / live API] | [source table] | [window] | [NULL → 0? or explicit NULL?] | [date] |

**Red flags to flag immediately:**
- Computed in the BI tool (not the mart) — violates the mart-is-the-single-source rule
- "Live API at query time" — violates the mart-as-single-source rule and adds query latency
- NULL → 0 anywhere — violates the explicit-NULL rule

## Step 2 — Trace each metric to the mart definition

For every metric computed in the mart, find the dbt model (or equivalent) and confirm:
1. The model name and the mart column name match what is displayed on the dashboard
2. The window definition matches what the CS team was told (e.g., "30-day usage trend" is actually 30 days, not 28 or 35)
3. The grain is correct (account-level, not user-level accidentally aggregated)
4. The trend column is materialized, not a `CASE WHEN ... OVER (...)` computed at query time

## Step 3 — Validate the append-only health snapshot

Confirm `fct_account_health_snapshot`:
- Is append-only (no deletes, no upsert-in-place rows)
- Has one row per account per day for the complete history window
- The trend columns (`health_score_delta_7d`, `usage_slope_30d`) are materialized in the model, not derived at query time
- NULL signals are NULL, not zero

```sql
-- Quick check: does the table have rows for every day in the window?
SELECT snapshot_date, COUNT(*) AS account_count
FROM fct_account_health_snapshot
WHERE snapshot_date >= CURRENT_DATE - 90
GROUP BY 1
ORDER BY 1
-- Expected: a row for every date in the window with a stable account count
-- Red flag: missing dates (gap) or count drops that aren't explained by churn
```

## Step 4 — Audit tier rule expression

Find the tier rule expression (in the mart model, a dbt macro, or the tier-definition doc) and verify:
- The rule uses the threshold values documented in the tier-design decision record
- The NULL handling is explicit: a missing signal is treated as NULL (not zero or "OK")
- The drivers columns (`tier_driver_1`, `tier_driver_2`) are populated for every Red account
- The explainability contract is met: every Red has at least one named driver

## Step 5 — Identify identity-resolution anomalies

Check whether any metric is published off a name-match join rather than the resolved `bridge_account_xref` cross-reference. Name-only joins produce artificially inflated or deflated metrics when two accounts share a company name variation.

```sql
-- Check for unresolved accounts in key metrics
SELECT COUNT(*) AS unresolved
FROM fct_account_health_snapshot h
LEFT JOIN dim_account a ON h.account_id = a.account_id
WHERE a.account_id IS NULL
-- Expected: 0. Any non-zero value means metric rows that can't be attributed to a resolved account.
```

## Step 6 — Produce the audit report

```
Audit date: [YYYY-MM-DD]
Dashboard version / last refresh: [date]

Metric count: [total]
Passed: [N]
Flagged: [N]

Flags:
  [metric name]: [flag type] — [brief description] — recommended fix: [action]

Identity-resolution anomalies: [N unresolved]
NULL handling violations: [N fields where NULL → 0]
Mart-bypass violations: [N metrics computed in BI tool or via live API]
Append-only snapshot: [PASS / FAIL — detail if fail]

Handoff to data-platform: [any mart fixes required]
Recommended re-audit date: [YYYY-MM-DD — after fixes are deployed]
```

## Pitfalls

- Auditing only the dashboard layer without tracing to the mart model — a clean dashboard that sits on wrong mart logic passes the surface check and fails in production.
- Treating a BI-tool computed metric as "fine" because it returns the same number as the mart — it will diverge eventually, and the divergence will be invisible.
- Skipping the identity-resolution check when the source systems use different account name formats — name-match joins are almost always subtly wrong.

## See also

- [`../../knowledge/cs-health-metrics-and-churn-indicators.md`](../../knowledge/cs-health-metrics-and-churn-indicators.md) — canonical signal definitions to audit against
- [`../../agents/cs-analytics-architect.md`](../../agents/cs-analytics-architect.md) — the agent that designs and owns the mart layer
- [`../../templates/cs-health-data-model.md`](../../templates/cs-health-data-model.md) — the reference schema to cross-reference
