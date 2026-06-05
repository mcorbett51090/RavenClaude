---
scenario_id: 2026-06-05-dispatch-utilization-improvement
contributed_at: 2026-06-05
plugin: skilled-trades-contracting
product: field-operations
product_version: "n/a"
scope: likely-general
tags: [dispatch, billable-efficiency, utilization, scheduling, truck-stocking]
confidence: medium
reviewed: false
---

## Problem

A plumbing service contractor with 8 trucks was turning away calls and the owner's instinct was to hire two more technicians. Revenue was flat despite a full call board. The real constraint turned out to be **low billable-hour efficiency** — techs were spending too much of the paid day on drive time, parts runs, and rework, so the existing fleet's capacity was underused before any hire was justified.

## Context

- Trade: plumbing, residential + light-commercial service, 8 techs / 8 trucks, dispatcher booking by "next available" with no geographic clustering.
- Constraint: billable-hour efficiency sat around the mid-50s percent — well below a healthy service target — meaning nearly half of each paid hour was non-billable (drive, restock, second trips for parts, callbacks).
- The owner read "full call board + flat revenue" as a headcount shortage. The decision tree reads the same signal as a **utilization** problem first: adding a tech to a low-efficiency shop adds overhead without proportional revenue.

## Attempts

- Tried: measured the **billable-hour ratio** before any hire (the §3 #3 master number) and located the non-billable time — drive, parts runs, and callbacks dominated. Outcome: confirmed the leak was utilization, not headcount; the "hire a tech?" decision tree gates the hire on existing efficiency being above ~70% first.
- Tried: fixed dispatch (geographic clustering / zoning of the day's calls to cut drive time) and **truck stocking** (the common-parts kit that turns a second trip into a first-time fix). Outcome: cut drive time and parts-run trips; first-time-fix rose, which removed callbacks (a callback is a free truck roll, §3 #4).
- Tried: only after the utilization lever was pulled did we re-run the headcount question — with efficiency recovered, the call board cleared without two new trucks. Seasonal peak overflow was routed to a subcontractor rather than a permanent hire. Outcome: deferred the fixed-cost hire; recovered capacity the fleet already owned.

## Resolution

The bottleneck was **billable-hour efficiency and dispatch sequencing**, not technician count. Clustering the route, stocking the trucks, and cutting callbacks unlocked the capacity that overhead was already paying for — deferring two hires. The truck is a profit center with a utilization number (§3 #6); fix the number before adding the asset.

**Action for the next consultant hitting this pattern:** when a service contractor with a full board wants to hire, **measure billable-hour efficiency first** (§3 #3). Below ~70%, fix dispatch sequencing and truck stocking before adding headcount — a hire into a low-utilization shop just adds overhead. Handle seasonal peaks with variable-cost labor (sub/temp), not a permanent seat. See [`../knowledge/trades-decision-trees.md`](../knowledge/trades-decision-trees.md) (the "should we hire a technician?" tree) and the [`billable-hour-efficiency`](../best-practices/billable-hour-efficiency-is-the-fields-master-number.md) / [`the-truck-is-a-profit-center`](../best-practices/the-truck-is-a-profit-center-with-a-utilization-number.md) rules.

**Sources (retrieved 2026-06-05):**
- ServiceTitan — *Understanding HVAC Profit Margins & How to Improve Them* (utilization/efficiency as a margin lever in field service): https://www.servicetitan.com/blog/hvac-profit-margins
- Mar-Hy Distributors — *Key Financial Metrics for HVAC Success in 2025* (billable efficiency, first-time-fix): https://www.marhy.com/key-financial-metrics-for-hvac-success-in-2025/

Efficiency and first-time-fix targets vary by trade and call mix; treat any specific threshold as `[verify-at-use]` and validate against the contractor's dispatch data (§3 #8).
