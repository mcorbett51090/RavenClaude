---
scenario_id: 2026-06-08-adherence-gap-was-a-star-and-revenue-problem
contributed_at: 2026-06-08
plugin: pharmacy-operations
product: adherence
product_version: "n/a"
scope: likely-general
tags: [adherence, pdc, star-ratings, targeting]
confidence: medium
reviewed: false
---

## Problem

A pharmacy saw a PDC dip and treated it as a purely clinical follow-up item. The risk: adherence (PDC) is simultaneously an outcome lever and a direct star-rating/value-based-reimbursement input — treating an adherence gap as only clinical misses that it's also a quality-rating and revenue problem, and untargeted effort wastes scarce intervention time (§3 #4).

## Context

- Setting: pharmacy participating in a plan with adherence star measures.
- Constraint: PDC over the measurement period sets the star band; patients near a threshold move the measure most (§3 #4).
- The pharmacy reasoned about adherence without the star/revenue tie or targeting.

## Attempts

- Tried: **measured PDC over the defined period** (`pharmacy_operations_calc.py adherence`) and placed each cohort against the band. Outcome: the dip was concentrated near the threshold — where intervention has the most leverage.
- Tried: **translated the band into the star-rating and reimbursement implication** (§3 #4). Outcome: the gap was reframed as quality + revenue, not just clinical.
- Tried: **targeted refill-sync/reminder operational fixes**, routing any drug-therapy question to the pharmacist (§3 #8 §2). Outcome: an operational plan with the clinical judgment routed out.

## Resolution

The response was to **target intervention at the near-threshold patients and translate the gap into its star/revenue impact** — not a blanket clinical follow-up. The output was the PDC band read, the star/reimbursement implication, and the targeted operational plan, with no patient PHI in the deliverable.

**Action for the next consultant hitting this pattern:** **read adherence as stars and revenue, and target patients near the band threshold.** An adherence gap is a quality and revenue problem at once; near-threshold patients give the most leverage, and drug-therapy questions route to the pharmacist. See Tree 3 and the `adherence` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
