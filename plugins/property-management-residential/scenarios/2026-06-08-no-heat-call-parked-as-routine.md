---
scenario_id: 2026-06-08-no-heat-call-parked-as-routine
contributed_at: 2026-06-08
plugin: property-management-residential
product: generic
product_version: "unknown"
scope: likely-general
tags: [habitability, triage, emergency, work-order, after-hours]
confidence: high
reviewed: false
---

## Problem

A "no heat" call came in on a Friday afternoon in January and landed in the general work-order queue tagged "routine — HVAC." It sat over the weekend because the queue was sorted by submission order and cost, not by habitability. The tenant was without heat in freezing weather for two days, escalated angrily on Monday, and the situation became both a habitability problem and a trust problem that a 30-minute Friday dispatch would have avoided.

## Constraints context

- The work-order system sorted by age and estimated cost, with no safety/habitability priority field.
- After-hours calls routed to the same queue as cosmetic requests.
- Staff weren't sure whether "no heat" was technically an emergency, so it defaulted to routine — the wrong default.

## Attempts

- Tried: adding more weekend staff to drain the queue faster. Failed — a faster FIFO queue still buries the one ticket that was actually an emergency.
- Tried: a cost-based priority. Failed — it deprioritized a cheap-but-critical no-heat fix behind expensive cosmetic work.
- Tried: a triage rubric that classifies by risk to person and habitability FIRST — no heat in winter, no water, no power, sewage, gas, and no lock are emergencies dispatched now, with "when in doubt, treat as emergency." This worked.

## Resolution

The habitability-first rubric pulled no-heat (and the rest of the list) out of the routine queue automatically and dispatched it the same hour. The legal warranty-of-habitability question was flagged to counsel separately; the operational duty to act fast did not wait on it. Time-to-dispatch on habitability events dropped from "next business day" to within the hour.

## Lesson

Triage by safety and habitability first, cost second. No heat in winter (and no water/power/gas/sewage/lock) is an emergency with a duty to act fast — it never sits in the routine queue, and "when in doubt, treat as emergency" is the correct default. Warranty-of-habitability *legality* is a counsel flag; the operational urgency is immediate.
