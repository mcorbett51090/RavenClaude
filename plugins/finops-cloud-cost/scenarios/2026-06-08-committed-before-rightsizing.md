---
scenario_id: 2026-06-08-committed-before-rightsizing
contributed_at: 2026-06-08
plugin: finops-cloud-cost
product: commitment
product_version: "n/a"
scope: likely-general
tags: [commitment, rightsizing, waste, sequencing]
confidence: medium
reviewed: false
---

## Problem

A team saw a high on-demand bill and bought a large Savings Plan to capture the discount, computing coverage against the current footprint. The risk: committing against an un-rightsized baseline locks in oversized and idle resources for the full term, so the 'savings' subsidize waste (§3 #4 #5).

## Context

- Stage: growing startup, no prior rightsizing pass.
- Constraint: the correct sequence is waste -> rightsize -> commit; committing on the fat baseline reverses it (§3 #4).
- The team reasoned from the gross on-demand bill.

## Attempts

- Tried: **ran a rightsizing read first** (`finops_cloud_cost_calc.py rightsizing`). Outcome: a meaningful share of the baseline was oversized against real utilization — capacity the commitment would have locked in (§3 #4).
- Tried: **inventoried waste** (idle/orphaned/oversized). Outcome: pure-savings wins that should be harvested before any discount (§3 #5).
- Tried: **modeled commitment coverage on the LEAN baseline** (`finops_cloud_cost_calc.py commitment`). Outcome: the right coverage was lower than the gross-baseline plan, with materially less utilization risk (§3 #3).

## Resolution

The fix was to **reverse the sequence** — harvest waste, rightsize to utilization, then buy commitments against the lean baseline at a coverage tier where the marginal discount beat the marginal lock-in risk — **not** to max coverage on the fat baseline. The output was the rightsizing read, the waste inventory, and the lean-baseline coverage model.

**Action for the next consultant hitting this pattern:** **rightsize and kill waste before you commit; never the other way around.** A commitment on a fat baseline locks in waste for the whole term. Model coverage on the lean baseline and stop where marginal discount no longer pays for marginal lock-in risk. See Tree 3 and the `rightsizing`/`commitment` modes.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
