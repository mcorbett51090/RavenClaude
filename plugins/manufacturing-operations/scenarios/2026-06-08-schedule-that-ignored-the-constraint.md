---
scenario_id: 2026-06-08-schedule-that-ignored-the-constraint
contributed_at: 2026-06-08
plugin: manufacturing-operations
product: mrp
product_version: "unknown"
scope: likely-general
tags: [mrp, mps, capacity, bottleneck, toc, infinite-capacity, s-and-op, lot-sizing]
confidence: high
reviewed: false
---

## Problem

A make-to-order job shop kept publishing a weekly master schedule that the floor could never hit. Sales promised dates straight off the MRP run; the plant missed roughly 40% of them and expedited the rest at a premium. The schedule looked rigorous — it was netted through the BOM and time-phased — but it was built on the planning system's default *infinite-capacity* assumption: every work center was treated as able to absorb whatever the netting dumped on it. The heat-treat oven, one shared resource, was quietly the constraint for 70% of the routings.

## Constraints context

- One heat-treat oven fed three downstream cells; its finite throughput was never represented in the MPS — the planning run had no finite-capacity profile loaded for it.
- Lot sizing was lot-for-lot everywhere "to minimize inventory," which meant many small heat-treat batches, each costing a long fixed ramp/soak setup at the exact resource that could least afford it.
- S&OP existed as a sales-forecast meeting, but the forecast was never reconciled against what the oven could actually clear in a week.

## Attempts

- Tried: pushing harder on expediting and overtime to recover the dates. Failed — expediting at the constraint just reshuffled the same finite oven-hours; total throughput didn't move, and premium freight ate the margin.
- Tried: adding a second shift on the downstream assembly cells (the visible busy work). Held — assembly was never the bottleneck; the extra labor produced more WIP queued in front of the oven, not more shipments.
- Tried: loading the oven's finite weekly capacity into the plan, re-lotting heat-treat into fewer larger batches to recover setup time at the constraint, and reconciling the sales forecast against that finite oven rate in S&OP before promising dates. This worked.

## Resolution

Once the oven's finite rate was the spine of the MPS, the schedule became buildable: promised dates were set against oven-hours, not against an infinite-capacity fiction. Re-lotting heat-treat to protect constraint time (and routing the long-ramp setup-reduction to `process-improvement` as a SMED candidate) recovered enough oven throughput that on-time delivery climbed past 90% without new capital. The S&OP meeting started reconciling the forecast against the constraint, so sales stopped promising what the oven couldn't clear.

## Lesson

A master schedule that ignores the bottleneck's finite rate is a wish, not a plan — infinite-capacity planning publishes dates the floor can't hit. Find the constraint (one shared resource gated most routings), plan the MPS to its finite rate, protect its time when you lot-size, and reconcile the forecast against it in S&OP. Plan to the constraint, never to infinite capacity.
