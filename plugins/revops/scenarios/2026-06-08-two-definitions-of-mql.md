---
scenario_id: 2026-06-08-two-definitions-of-mql
contributed_at: 2026-06-08
plugin: revops
product: generic
product_version: "unknown"
scope: likely-general
tags: [funnel, mql, definition, handoff, sla, attribution]
confidence: high
reviewed: false
---

## Problem

Marketing reported hitting its MQL target every month; sales said the leads were garbage and stopped working them. The board saw two dashboards with two different funnel numbers and trusted neither. Pipeline was "growing" on the marketing slide while sales-accepted volume was flat. The root cause wasn't lead quality per se — marketing's MQL was "downloaded a whitepaper + scored 50 points," sales' working definition of a real lead was "fits ICP and shows buying intent," and nobody had reconciled the two. Leads also sat unassigned for hours, so even the good ones went cold.

## Constraints context

- Marketing comp was tied to MQL volume; sales comp to closed-won. The incentives pulled the definition apart.
- No accept/reject loop existed — sales silently ignored bad MQLs instead of rejecting them with a reason, so marketing never got the signal.
- Leadership wanted "one number" but each team defended its own dashboard as the real one.

## Attempts

- Tried: raising the MQL score threshold. Failed — it cut volume but didn't fix the definition mismatch; sales still rejected leads that cleared the higher bar because the *criteria* (not the threshold) were wrong.
- Tried: a weekly marketing-vs-sales reconciliation meeting. Failed — it surfaced the disagreement but didn't resolve it; without a shared written definition every meeting re-litigated the same fight.
- Tried: defining MQL by criteria *sales agreed converts* (ICP fit + a specific intent signal), instrumenting it at one point, adding an SAL stage with an explicit accept/reject loop and a reason code, and putting a speed-to-lead SLA on assignment. This worked.

## Resolution

One written MQL definition, owned by RevOps (not marketing or sales), measured once. The SAL accept/reject loop gave marketing a feedback signal — rejection reasons became the input that improved scoring. The speed-to-lead SLA (assign within 5 minutes, accept/reject within a day) stopped good leads going cold. Within a quarter the two dashboards converged to one number both teams stood behind, and sales-accepted volume — the metric that actually predicts pipeline — became the shared target.

## Lesson

When marketing and sales report different funnel numbers you don't have a funnel, you have two. Fix the *definition* (by criteria the downstream team accepts) before touching thresholds or tooling, wire an accept/reject feedback loop so the definition stays honest, and put a speed-to-lead SLA on routing — an unrouted lead is lost revenue.
