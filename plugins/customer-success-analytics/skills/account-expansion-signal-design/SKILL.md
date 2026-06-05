---
name: account-expansion-signal-design
description: "Design the signal set and mart model for an account expansion-readiness view alongside the churn-risk tier — identifying which signals predict expansion, how to surface them without confusing the CS team, and what mart additions are needed. Reach for this skill when a CS team wants both a churn-risk view and an expansion-opportunity view from the same health mart."
---

# Skill: Account Expansion Signal Design

A health tier focused only on churn risk surfaces who is in trouble. A complete CS analytics build also surfaces who is primed for a grow motion — expansion-ready accounts with high usage momentum, champion depth, and positive sentiment. This skill designs the expansion signal layer alongside the existing risk tier without conflating the two.

## The core rule: separate expansion from churn mitigation

Expansion signals and churn-risk signals are **different animals**:

| Signal type | Churn risk | Expansion readiness |
|---|---|---|
| Usage trend | Down trend = risk | Up trend = expansion candidate |
| Health score | Declining = risk | High + stable = expansion candidate |
| Champion depth | Single champion = risk | Multiple active champions = expansion ready |
| Support load | High escalations = risk | Low support + resolved backlog = expansion ready |
| NPS | Low + declining = risk | High + recent = expansion ready |

Do not fold expansion signals into the churn-risk tier or use a single "health score" that conflates the two. A "healthy" account in the churn-risk tier is not necessarily expansion-ready. Keep the tiers and the views separate.

## Step 1 — Define the expansion outcome

Pick the one outcome the expansion signal predicts:

- **Upsell** — account upgrades to a higher plan tier
- **Cross-sell** — account adds a new product line
- **Seat expansion** — account grows user count within the current plan
- **Composite expansion** — any revenue-expansion event (fallback when the above are not distinguishable in source data)

## Step 2 — Select the expansion signals (4-6 max)

Domain-neutral expansion signal categories:

| Category | Example signals | Grain + window |
|---|---|---|
| Usage momentum | Active-user count trending up 30-day rolling; feature adoption rate above baseline | Account, 30-day |
| Champion depth | Count of named active users; count of departments with active usage | Account, rolling 90-day |
| Engagement quality | QBR attended; product-feedback submitted; champion-to-new-stakeholder introductions | Account, event-based |
| Sentiment | NPS >= 8 in last 180 days; last CSAT > 4/5 | Account, last response |
| Renewal runway | Days since last renewal > 180 (enough runway to execute a grow motion) | Account, point-in-time |
| Feature depth | Count of distinct features used in last 30 days above adoption baseline | Account, 30-day |

All six signals are **leading for expansion** — they fire before the expansion event. Verify each against historical upsell/cross-sell outcomes the same way churn signals are validated.

## Step 3 — Define the expansion tier rule

```
Expansion Ready := usage_trend_30d = up
                   AND champion_depth >= 2
                   AND (nps_last_180d >= 8 OR csat_last_90d >= 4)
                   AND renewal_runway_days > 180

Expansion Watch := one or two signals above threshold but not all three
                   (monitor — not yet ready for a grow motion)

Neutral         := everything else
```

The expansion tier runs **alongside** the churn-risk tier. An account can be Red (churn risk) and Neutral (no expansion signal) at the same time. Render them as two separate columns or two separate views — not a single composite.

## Step 4 — Mart additions required

This skill produces a domain-layer contract for `data-platform`:

```sql
-- New mart table: fct_account_expansion_signal (daily, append-only like the risk snapshot)
-- Columns:
--   account_id, snapshot_date, expansion_tier (ready|watch|neutral),
--   usage_trend_30d, champion_depth, nps_last_180d, csat_last_90d,
--   renewal_runway_days, feature_depth_30d,
--   expansion_tier_driver_1, expansion_tier_driver_2   -- explainability columns
```

Hand the build to `data-platform/etl-pipeline-engineer` and `database-setup-guide`. This plugin specifies the contract; data-platform builds it.

## Step 5 — Explainability for expansion-ready accounts

Apply the same explainability contract as the churn-risk tier: every Expansion-Ready account shows its 2-3 driving signals in the CS surface. The CS rep opening an account marked Expansion-Ready must be able to see *why* in under 30 seconds.

## Pitfalls

- Folding expansion signals into the churn-risk tier — a single composite obscures both signals and produces a tier the CS team can't explain.
- Using lagging signals (signed contract expansion, invoice uplift) as expansion *predictors* — they confirm an expansion that already happened.
- Building the expansion view before the churn-risk tier is validated — fix the baseline view before adding growth complexity.
- Missing the renewal-runway signal: an expansion motion requires enough contract runway to execute; a renewal that is 30 days out is not expansion-ready regardless of usage.

## See also

- [`../../knowledge/cs-health-metrics-and-churn-indicators.md`](../../knowledge/cs-health-metrics-and-churn-indicators.md) — signal classification and leading vs. lagging taxonomy
- [`../../agents/cs-analytics-architect.md`](../../agents/cs-analytics-architect.md) — the agent that designs this into the mart
- [`../../agents/churn-signal-analyst.md`](../../agents/churn-signal-analyst.md) — validates expansion signals the same way churn signals are validated
