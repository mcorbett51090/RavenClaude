---
scenario_id: 2026-06-08-over-capacity-drove-attrition
contributed_at: 2026-06-08
plugin: wealth-management-ria
product: advisor-capacity
product_version: "n/a"
scope: likely-general
tags: [capacity, households-per-advisor, retention, compliance-cadence]
confidence: medium
reviewed: false
---

## Problem

A growing firm kept adding households to existing advisors and saw attrition tick up a year later. The risk: advisor capacity is finite in households, and pushing past it degrades service and review cadence — which surfaces later as attrition and a slipping compliance cadence, not as an immediate alarm (§3 #4 #5 #6).

## Context

- Model: AUM-fee RIA scaling its book without adding advisors.
- Constraint: households per advisor has a defensible band; over it, service and cadence slip and retention follows (§3 #4 #5).
- Leadership reasoned from AUM growth, not capacity.

## Attempts

- Tried: **measured households per advisor vs a target band** (`riaops_calc.py advisor-capacity`). Outcome: several advisors were well over the band.
- Tried: **tied capacity to the review cadence** (§3 #6). Outcome: periodic reviews were slipping for over-capacity advisors — a compliance-cadence exposure as well as a service one.
- Tried: **read attrition against capacity** (§3 #5). Outcome: the over-capacity books showed the rising attrition — a leading indicator the AUM growth had masked.

## Resolution

The response was to **add advisor capacity (or re-tier service) and protect the review cadence before attrition compounded** — not keep loading existing advisors. The output was the capacity read, the cadence risk, and a retention-protection plan; any compliance-calendar question routed to counsel (§2).

**Action for the next consultant hitting this pattern:** **treat households per advisor as a leading retention and compliance-cadence indicator.** Over-capacity degrades service and review cadence quietly, and attrition compounds; size capacity before chasing more AUM. See Tree 3 and the `riaops_calc.py` `advisor-capacity` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
