---
scenario_id: 2026-06-05-interconnection-queue-upgrade-shock
contributed_at: 2026-06-05
plugin: renewable-energy
product: interconnection
product_version: "n/a"
scope: likely-general
tags: [interconnection, queue, network-upgrade, resize, irr]
confidence: medium
reviewed: false
---

## Problem

A mid-size solar project cleared its feasibility screen and the developer modeled an attractive IRR on a placeholder interconnection-upgrade assumption. The system-impact study then came back with a **network-upgrade allocation several multiples** of the placeholder — large enough to push the project below the equity hurdle. The risk: treating the queue and the upgrade cost as a late-stage line item rather than the schedule-and-cost driver it actually is (CLAUDE.md §3 #2 — interconnection is the schedule, and the schedule is the risk).

## Context

- Segment: utility-scale / large C&I, single point of interconnection (POI) at a constrained substation.
- Constraint: the upgrade allocation is **not knowable to the dollar before the study** — pre-study estimates are placeholders, and the developer had committed site-control and study-deposit cost against the optimistic one. Network upgrades can be a **first-loss exposure** (the developer fronts cost that may not be refunded if earlier-queue projects drop and re-trigger restudies).
- The developer was reasoning "the study is a formality" instead of "the study can move the IRR by more than the module price ever will."

## Attempts

- Tried: re-ran the IRR with the **final** upgrade allocation instead of the placeholder, and confirmed the gap was upgrade-driven, not revenue-driven. Outcome: isolated the single variable that broke the model — the upgrade cost, not the PPA price or the resource.
- Tried: tested **resize / reconfigure** — reducing the MW load on the constrained POI to shrink the upgrade allocation, which often falls roughly with the injection the upgrade has to accommodate. Outcome: a smaller project at the same POI cleared the hurdle because its upgrade share dropped more than its revenue did.
- Tried: priced the **alternative POI** option (a different substation with queue headroom) against the resize, and the cost/time of re-queuing. Outcome: resize won on time-to-NTP; the alternate POI was kept as the fallback if a later restudy re-inflated the allocation.

## Resolution

The project was rescued by **resizing to the constrained POI's real headroom** rather than abandoning, because the upgrade allocation — not the resource or the offtake — was the binding constraint, and upgrade cost scales with injected MW. The output was a dated, study-grounded pro-forma with the upgrade allocation as a modeled (not placeholder) input and a sensitivity band around a possible restudy.

**Action for the next consultant hitting this pattern:** **model the interconnection upgrade as a first-loss exposure early, with a sensitivity band — never a placeholder line item.** When a study breaks the IRR, sequence the cheap levers first: confirm the allocation is final (not pre-study), then resize/reconfigure to shed upgrade load on the constrained POI **before** renegotiating offtake or abandoning — see [`../knowledge/renewables-decision-trees.md`](../knowledge/renewables-decision-trees.md) "Project IRR Below Hurdle Rate". The interconnection lane is owned by [`grid-interconnection-specialist`](../agents/grid-interconnection-specialist.md).

**Sources (retrieved 2026-06-05):**
- LBNL / Berkeley Lab — *Queued Up: Interconnection queue characteristics & costs* (network-upgrade cost variability, withdrawal/restudy dynamics): https://emp.lbl.gov/queues
- FERC — Order No. 2023 (interconnection process reform, cluster studies): https://www.ferc.gov/explainer-interconnection-final-rule

Upgrade-allocation magnitudes and queue timelines are ISO/RTO- and POI-specific and move with each study cycle — treat as `[verify-at-use]` and ground in the project's actual study results (§3 #2, #8).
