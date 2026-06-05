---
scenario_id: 2026-06-05-job-margin-erosion-change-orders
contributed_at: 2026-06-05
plugin: skilled-trades-contracting
product: job-costing
product_version: "n/a"
scope: likely-general
tags: [job-costing, change-order, margin-erosion, scope-creep, labor-variance]
confidence: medium
reviewed: false
---

## Problem

A residential/light-commercial HVAC-and-plumbing contractor was "busy all year" but the P&L showed gross margin several points below the segment range, and net profit near zero. The owner blamed material price inflation. Job-by-job, the real driver turned out to be **uncaptured change-order scope and unfavorable labor variance** — crews delivering extra work for free and burning hours the estimate never funded.

## Context

- Trade: HVAC + plumbing, residential service + small new-install, ~14 field staff, owner still estimating most jobs from a spreadsheet.
- Constraint: no job-cost reconciliation existed — actuals were never compared to the estimate, so a losing job looked identical to a winning one on the bank balance. Change orders were handled verbally ("we'll take care of you") and rarely written.
- The owner conflated "margin is down" (a P&L symptom) with "material got expensive" (one of several possible causes) — the single-cause story the decision trees warn against.

## Attempts

- Tried: ran a **job-cost reconciliation** on a sample of recent jobs before accepting the inflation story — actual labor hours x loaded rate + material (incl. waste) + sub cost vs the bid. Outcome: on the losing jobs, **labor variance was >15% unfavorable** and a chunk of delivered work had **no corresponding change order**. Material price was a minor contributor.
- Tried: decomposed the variance per the post-completion decision tree — separated rework/callbacks (a quality problem) from genuine efficiency loss (a dispatch problem) from uncaptured scope (a discipline problem). Outcome: uncaptured scope + rework dominated; material drift was last.
- Tried: instituted **written change-order discipline** (any scope beyond the signed estimate stops for a signed change order before work proceeds) and a standing job-cost close-out on every job over a dollar threshold. Modeled the leak with [`../scripts/trades_calc.py`](../scripts/trades_calc.py) `job-margin` (the `--uncaptured-change-order` input shows the margin points handed away). Outcome: the free-work leak closed; the close-out made the next estimate's labor assumptions honest.

## Resolution

The margin gap was mostly **uncaptured change-order scope and labor variance**, not material inflation. The fix was operational discipline — written change orders before out-of-scope work, and a job-cost close-out that feeds actuals back into the next estimate — not a supplier renegotiation. Change-order industry framing: change orders commonly run **~8–14% of total project cost** (commercial), with **~10%** a widely-cited benchmark, and markup on change-order work is frequently **~15%** [verify-at-use] — so capturing them is material, not rounding.

**Action for the next consultant hitting this pattern:** when margin is down on a busy contractor, **reconcile before you renegotiate** — run job costing, then split labor variance into rework vs efficiency vs uncaptured scope; the last is usually the biggest and the cheapest to fix. Enforce written change-order discipline and a close-out loop so the estimate learns. See [`../knowledge/trades-decision-trees.md`](../knowledge/trades-decision-trees.md) (the post-completion losing-money tree) and the [`job-costing-closes-the-loop`](../best-practices/job-costing-closes-the-loop-between-estimate-and-actual.md) / [`change-order-discipline`](../best-practices/change-order-discipline-protects-margin-on-every-construction-job.md) rules.

**Sources (retrieved 2026-06-05):**
- Rhumbix — *How Much Are Change Orders Costing Your Construction Business?* (change-order cost share): https://www.rhumbix.com/blog/how-much-are-change-orders-costing-your-construction-business
- Case Western Facilities — *Pricing of Construction Contract Change Orders* (change-order markup ~15%): https://case.edu/facilities/sites/default/files/2024-10/410%20Pricing%20of%20Construction%20Contract%20Change%20Orders.pdf

Change-order and variance percentages are segment-dependent; treat any specific number as `[verify-at-use]` and validate against the contractor's actual job-cost data (§3 #8).
