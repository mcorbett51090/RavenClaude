# Expansion Signal Design Brief

> **Use for:** documenting the expansion-readiness signal set and mart additions when a CS team wants a grow-motion view alongside the churn-risk tier. Produced by the `account-expansion-signal-design` skill; handed to `data-platform` to build the `fct_account_expansion_signal` mart table.

---

**Date:** [YYYY-MM-DD]
**Produced by:** [cs-analytics-architect or analyst]
**CS team:** [team / company name]
**Expansion outcome targeted:** [upsell / cross-sell / seat expansion / composite]

---

## 1. Expansion tier definition

| Tier | Rule expression | CS action |
|---|---|---|
| Expansion Ready | [usage_trend_30d = up AND champion_depth >= 2 AND nps_last_180d >= 8 AND renewal_runway_days > 180] | Start grow-motion; book expansion QBR |
| Expansion Watch | [1-2 signals above threshold] | Monitor; qualify in next QBR |
| Neutral | [all else] | No expansion motion; maintain current cadence |

> Adjust signal names and thresholds to the engagement's actual columns. All thresholds are provisional until validated against historical expansion outcomes.

---

## 2. Signal inventory

| Signal | Source table | Column | Window | Threshold | Validated? |
|---|---|---|---|---|---|
| Usage momentum | [source] | [column] | 30-day rolling | [value] | [yes / provisional] |
| Champion depth | [source] | [column] | Rolling 90-day | [count >= N] | [yes / provisional] |
| Engagement quality | [source] | [column] | Event-based | [e.g. QBR attended last 180d] | [yes / provisional] |
| NPS / CSAT | [source] | [column] | Last response 180d | [>= 8 / >= 4] | [yes / provisional] |
| Renewal runway | dim_account | days_to_renewal | Point-in-time | [> 180 days] | [yes / provisional] |
| Feature depth | [source] | [column] | 30-day | [>= N features] | [yes / provisional] |

---

## 3. Mart additions (data-platform contract)

### New table: `fct_account_expansion_signal`

```sql
-- Grain: one row per account per snapshot_date (append-only)
CREATE TABLE fct_account_expansion_signal (
    account_id              TEXT        NOT NULL,
    snapshot_date           DATE        NOT NULL,
    expansion_tier          TEXT        NOT NULL,  -- 'ready' | 'watch' | 'neutral'
    usage_trend_30d         TEXT,                  -- 'up' | 'flat' | 'down' | NULL
    champion_depth          INT,                   -- count of active named champions | NULL
    nps_last_180d           FLOAT,                 -- last NPS score in window | NULL
    csat_last_90d           FLOAT,                 -- last CSAT in window | NULL
    renewal_runway_days     INT,                   -- days to next renewal | NULL
    feature_depth_30d       INT,                   -- count distinct features used | NULL
    expansion_tier_driver_1 TEXT,                  -- top driver for Ready or Watch
    expansion_tier_driver_2 TEXT                   -- second driver or NULL
);
```

**Append-only:** same as `fct_account_health_snapshot` — no deletes, no upserts.

### Dashboard additions

- [ ] New column: `expansion_tier` alongside `risk_tier` in the main accounts view
- [ ] Expansion-Ready filter: quick filter to show only Ready accounts sorted by ACV
- [ ] Expansion drivers panel: same explainability design as the churn-risk tier

---

## 4. Rendering rule — keep the tiers visually separate

Do NOT combine `expansion_tier` and `risk_tier` into a single composite score. Render them as two independent columns. A CS rep must be able to answer both:
- "Who is at risk of churning?" (risk_tier = Red)
- "Who is ready to grow?" (expansion_tier = Expansion Ready)

...without one answer obscuring the other.

---

## 5. Validation plan

Back-test the expansion signals against historical expansion outcomes (same methodology as `churn-signal-backtest` skill) after the first full quarter of data is available. Until validated, mark all thresholds `[provisional]`.

**Target validation date:** [YYYY-MM-DD]
**Outcome data needed:** [upsell / cross-sell / seat-expansion events from CRM — table: [table name]]

---

## 6. Handoff checklist

- [ ] Signal table shared with data-platform/etl-pipeline-engineer
- [ ] `fct_account_expansion_signal` schema approved by cs-analytics-architect
- [ ] Dashboard additions spec shared with data-platform/dashboard-builder
- [ ] Validation date agreed with CS team lead
