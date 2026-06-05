---
name: slo-definition-workshop
description: "Guided workshop playbook for defining SLIs and SLOs with engineering and product — produces a complete SLO document with error budget, burn-rate alert thresholds, and a budget policy."
---

# SLO Definition Workshop

## When to Use This

A service has no SLOs, or its existing ones are arbitrary ("five nines because it sounds good"). Run this workshop with the service owners and product stakeholders to produce SLOs that reflect user pain and that the team will actually act on.

## Pre-Work (Before the Session)

1. Pull 90 days of request/error/latency data from your monitoring backend.
2. Identify the user-visible entry points — not internal hops, but the calls a user or downstream consumer can actually feel.
3. Invite: the on-call engineer, the product owner, and one customer-facing person (support, CSM, or PM with user data).

## Step 1 — Define the SLI (What to Measure)

Good SLIs are ratio metrics of **good events / valid events**. Use the request-based form:

| Dimension | SLI formula example |
|---|---|
| Availability | `HTTP 5xx` / total requests (exclude health-check and client 4xx) |
| Latency | requests completing in < X ms / total requests |
| Freshness (data) | data_age < threshold / all data reads |
| Durability | successfully retrieved writes / all writes (storage) |

**One or two SLIs per service, maximum.** More than two and the team loses focus; pick the dimension that causes the most user pain when it degrades.

## Step 2 — Set the SLO Target

1. Look at your 90-day percentile distribution. Note the actual reliability (p50/p99 of your latency SLI, or your error rate).
2. Ask: "If we held this level for a year, would product and customers be satisfied?" If yes, that's your starting target.
3. Apply a "tight but achievable" rule: start 0.5–1% below your best recent 30-day window. You can always tighten later.
4. Avoid five nines (99.999%) unless you have the operational capability to defend it — the error budget is only 5 minutes/year.

| SLO target | Annual error budget | Weekly budget |
|---|---|---|
| 99.9% | 8.7 hours | 10 minutes |
| 99.5% | 43.8 hours | 50 minutes |
| 99.0% | 87.6 hours | 100 minutes |

## Step 3 — Agree the Budget Policy

The error budget is useless without a policy that governs what happens when it runs low. Write down:

- **Green (> 50% remaining):** normal velocity, experiments allowed.
- **Yellow (10–50% remaining):** new features reviewed; reliability work prioritized.
- **Red (< 10% remaining):** feature freeze; all hands on reliability until budget recovers.
- **Exhausted:** incident post-mortem required before re-opening the budget.

## Step 4 — Set Burn-Rate Alerts

Use the multi-window multi-burn-rate pattern (Google SRE Workbook Ch. 5):

| Severity | Burn rate | Short window | Long window | Budget consumed |
|---|---|---|---|---|
| Page (P1) | 14× | 1 hour | 5 minutes | ~2% in 1 h |
| Page (P2) | 6× | 6 hours | 30 minutes | ~5% in 6 h |
| Ticket | 3× | 3 days | 6 hours | ~10% in 3 d |

Alert fires when BOTH windows exceed the burn rate — reduces false positives from transient spikes.

## Step 5 — Document the SLO

```
Service: <name>
SLI: <formula — numerator / denominator, data source>
SLO target: <X>% over a rolling 28-day window
Error budget: <minutes or requests per 28 days>
Budget policy: <green/yellow/red thresholds and actions>
Alert thresholds: <burn rates and windows from Step 4>
Exclusions: <planned maintenance windows, dependency outages?>
Review cadence: <monthly at reliability review>
Owner: <team>
Last reviewed: <date>
```

## Pitfalls

- Setting the SLO target before defining the SLI — teams anchor on "99.9%" without knowing what they're measuring.
- Including internal health-check traffic in the denominator — inflates availability and hides real user-facing errors.
- No budget policy — an SLO without a policy is a number on a dashboard nobody acts on.
- Alerting on burn rate only (no short window) — slow burns trigger too late; alerting only on the long window misses fast burns.
- Setting an SLO tighter than your dependencies' SLOs — you will perpetually blow your budget on factors you can't control.

## See Also

- [`../../agents/sre-reliability-engineer.md`](../../agents/sre-reliability-engineer.md) — SLI/SLO/error-budget ownership
- [`../../agents/incident-commander.md`](../../agents/incident-commander.md) — budget exhaustion triggers incident process
