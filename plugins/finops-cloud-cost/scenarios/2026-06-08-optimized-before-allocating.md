---
scenario_id: 2026-06-08-optimized-before-allocating
contributed_at: 2026-06-08
plugin: finops-cloud-cost
product: cost-allocation
product_version: "n/a"
scope: likely-general
tags: [allocation, showback, tagging, governance]
confidence: medium
reviewed: false
---

## Problem

A FinOps lead launched an optimization sprint across teams, but most of the bill was untagged, so no team owned its number. The risk: optimizing un-allocated spend is guessing — you can't hold a team accountable for a bill they can't see, and showback-free allocation is a report nobody reads (§3 #1 #6).

## Context

- Stage: enterprise, partial tagging, no showback.
- Constraint: allocation precedes optimization; showback drives most behavior change (§3 #1 #6).
- The lead jumped straight to optimization targets.

## Attempts

- Tried: **measured allocation coverage** (tagged ÷ total) before targeting anything. Outcome: coverage was well below a usable threshold — the ungoverned pile dominated (§3 #1).
- Tried: **stood up showback to owning teams** rather than a chargeback mandate first. Outcome: teams that could finally see their spend started self-correcting (§3 #6).
- Tried: **sized and prioritized the biggest untagged sources** to close the gap fast. Outcome: a focused tagging push lifted coverage above the threshold.

## Resolution

The fix was to **allocate first — close the tagging gap and stand up showback — then optimize against numbers teams could see** — **not** to push optimization targets onto unattributed spend. The output was the coverage read, the ungoverned-pile size, and the showback design.

**Action for the next consultant hitting this pattern:** **allocate and stand up showback before you optimize.** Un-allocated spend can't be governed, and allocation without showback is a report nobody reads. Get coverage above a usable threshold first. See Tree 1 and the `measure-allocation` skill.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
