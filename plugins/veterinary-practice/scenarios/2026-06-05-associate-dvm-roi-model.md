---
scenario_id: 2026-06-05-associate-dvm-roi-model
contributed_at: 2026-06-05
plugin: veterinary-practice
product: finance
product_version: "n/a"
scope: likely-general
tags: [associate-dvm, hiring, production, roi, capacity]
confidence: medium
reviewed: false
---

## Problem

An owner-DVM wanted to hire a new-graduate associate "to grow," but had no model for whether the practice could *feed* a new doctor or what the hire would do to net income during ramp. The risk: hiring into insufficient demand, where the associate cannibalizes the owner's appointments instead of adding net production, and net income falls for 12+ months.

## Context

- Segment: general-practice, independent, 2 DVMs, growing new-client count, owner at capacity.
- Constraint: a new-grad associate ramps slowly — production builds over 12–24 months, while salary (often salary-or-production-floor) is paid from day one. The decision needs a **demand check** before a cost model.
- The owner was reasoning from "more doctors = more revenue" without checking whether the production thresholds and new-client flow justified the seat.

## Attempts

- Tried: ran the **demand/capacity check first**, using public production benchmarks as the gate. Rules of thumb from the literature: a full-time small-animal practitioner is often cited at **~3,000 invoices/year** and a practice at **~5,000 invoices per FTE doctor**; a sustainable load is **~20 patients/day** (more trends toward burnout); a full-time DVM should draw **~25 new clients/month**. When the existing doctors are consistently *above* these and new-client flow is healthy, demand supports a hire. Outcome: confirmed the practice was over the thresholds → demand exists.
- Tried: built a simple ROI model — incremental production (ramped over months), minus associate compensation (salary or production %, whichever floor applies), minus the support/COGS load that scales with the added production — to project the net-income trough and breakeven month. Outcome: quantified the J-curve so the owner could fund the trough deliberately rather than be surprised by it.
- Tried: checked the alternative (extend hours / add a tech / template fix) before committing to headcount, per the in-house-lever order. Outcome: confirmed the practice had already exhausted the cheaper capacity levers — so the associate was the right next move, not the first reflex.

## Resolution

The hire was justified **because the demand check passed first** (production thresholds exceeded, healthy new-client flow, cheaper capacity levers already used), and the ROI model made the ramp-period net-income trough explicit and fundable. The output was a dated model with a breakeven month and a compensation structure, not a gut call.

**Action for the next consultant hitting this pattern:** **demand check before cost model.** Gate the hire on production thresholds and new-client flow; only then model the ramp J-curve (incremental production minus comp minus scaling support/COGS) to find the net-income trough and breakeven. Always confirm the cheaper capacity levers (template, support ratio, hours) are exhausted first — see [`../knowledge/vet-add-associate-vs-extend-capacity-decision-tree.md`](../knowledge/vet-add-associate-vs-extend-capacity-decision-tree.md). The [`../scripts/vet_calc.py`](../scripts/vet_calc.py) `associate-roi` mode does the J-curve arithmetic.

**Sources (retrieved 2026-06-05):**
- dvm360 — when to add an associate (production thresholds, new-client signal): https://www.dvm360.com/view/qa-when-add-associate-your-team
- AAHA — associate compensation formula: https://www.aaha.org/newstat/publications/following-a-formula-for-fair-associate-veterinarian-compensation/
- Today's Veterinary Business — structuring associate pay: https://todaysveterinarybusiness.com/associate-dvm-pay-take-charge-0223/

Thresholds are rules-of-thumb from the trade literature, not hard rules — treat as `[verify-at-use]` and calibrate to the practice's case mix and segment (§3 #8).
