---
scenario_id: 2026-06-05-driver-turnover-bleed
contributed_at: 2026-06-05
plugin: fleet-logistics
product: driver-retention
product_version: "n/a"
scope: likely-general
tags: [driver-turnover, retention, unseated-truck, recruiting, unit-economics]
confidence: medium
---

## Problem

A truckload carrier treated driver turnover as an unavoidable HR cost of doing business — "everybody in trucking churns drivers" — and budgeted recruiting as a fixed line, never quantifying what a single separation actually cost or what the unseated trucks did to revenue. The carrier was spending heavily on a perpetual recruiting machine to backfill a leak it had never measured, while seated-truck count (the real revenue constraint) silently dropped every time a driver walked.

## Context

- Segment: for-hire truckload, ~50 trucks, long-haul, high-churn driver pool.
- Constraint: turnover was tracked as a single rate but **never converted to dollars**, and the **unseated-truck** cost (a parked truck earns nothing) was completely absent from the model. Recruiting spend and revenue loss lived in different mental buckets.
- The carrier conflated "turnover is industry-normal" (true — large TL carriers regularly run **90–95%**) with "turnover is unmanageable," skipping the unit-economics step entirely (§3 #4).

## Attempts

- Tried: **quantified turnover as unit economics** — annual separations = seats × turnover rate, × cost-per-replacement, **plus** the revenue lost while each seat sat empty. Public benchmarks anchored the inputs: average replacement cost commonly cited around **$8,000–$15,000** per driver (one widely-cited 2024 snapshot put it at **$12,799**), and a parked truck loses roughly **$800–$1,200/day** of revenue during the vacancy. [`../scripts/fleet_calc.py`](../scripts/fleet_calc.py) `turnover` did the arithmetic, including the unseated-truck term. Outcome: the all-in annual cost was far larger than the recruiting budget alone had suggested — because the unseated-truck revenue loss dwarfed the direct replacement cost.
- Tried: **modelled the retention prize** — what a 15–20-point cut in turnover would save annually. Because ~35% of new hires quit within 90 days and ~55% within 6 months, the highest-leverage intervention was the **first-90-day experience** (onboarding, realistic-route expectations, pay-structure clarity), not a blanket pay raise. Outcome: a targeted retention spend with a quantified payback, instead of an open-ended recruiting spend.
- Tried: **reframed retention as an operations metric, not HR overhead** — tied seated-truck count to revenue-per-truck-per-day so leadership saw turnover as a utilization leak (§3 #3, §3 #4). Outcome: retention got an owner and a target.

## Resolution

Turnover was a **quantified margin and utilization leak**, not an unavoidable HR cost: the unseated-truck revenue loss was the bigger half of the bill, and a modest reduction in turnover paid back a targeted retention investment many times over. The fix was to model turnover in dollars (incl. unseated trucks), target the first-90-day churn, and give retention an owner and a metric.

**Action for the next consultant hitting this pattern:** **convert turnover to dollars before accepting it as a cost of doing business** — and include the unseated-truck revenue loss, which usually exceeds the direct replacement cost. Driver turnover is a unit-economics problem, not HR overhead (§3 #4). Target the first-90-day quit cliff, not a blanket raise. Use [`../scripts/fleet_calc.py`](../scripts/fleet_calc.py) `turnover` for the annual cost and the retention prize.

**Sources (retrieved 2026-06-05):**
- TheTrucker — *2024 Snapshot shows estimated cost of losing one driver reaching $12,799*: https://www.thetrucker.com/trucking-news/business/2024-snapshot-shows-estimated-cost-of-losing-one-driver-reaching-12799
- Centerline Drivers — *How much does truck driver turnover cost?* (replacement range; unseated-truck revenue loss): https://www.centerlinedrivers.com/resources/how-much-does-truck-driver-turnover-cost/
- UGPTI — *The Costs of Truckload Driver Turnover* (per-replacement range $2,243–$20,729): https://www.ugpti.org/resources/reports/downloads/sp-146.pdf

Turnover rates and per-replacement costs vary widely by segment and carrier size — treat any specific number as `[verify-at-use]`/`[ESTIMATE]` and validate against the carrier's actual recruiting and revenue data (§3 #8). The team stores no driver PII (§2).
