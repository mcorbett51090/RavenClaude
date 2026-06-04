---
name: slo-and-error-budgets
description: "Design SLIs/SLOs and an error-budget policy: pick user-centric indicators, set targets by user need (not 100%), define the ship-vs-freeze budget rule, and enforce with multi-window multi-burn-rate alerts."
---

# SLOs & Error Budgets

**Purpose:** decide how reliable a service must be and enforce it.

## SLIs
Measure user happiness at the boundary: availability, latency (p99), correctness. `good events / valid events`.

## SLO target
Set by user need. 99.9% = ~43 min/month budget. 100% is a cost, not a goal.

## Error-budget policy
- Budget remaining -> ship features, take risk.
- Budget exhausted -> freeze features, do reliability work.

## Burn-rate alerting (multi-window)
Page when burning fast **and** confirmed: e.g. 2% budget in 1h (fast) AND sustained over 5m. Multi-window suppresses blips, catches real fast-burns.
