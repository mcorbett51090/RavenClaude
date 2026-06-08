---
description: "Run a hotel revenue-management and pricing analysis: build the demand calendar, set or validate BAR strategy, design length-of-stay controls, model an overbooking policy, and calculate the RevPAR impact of pricing decisions."
---

# Revenue Management and Pricing

**Purpose:** translate demand signals into a pricing and inventory strategy that maximizes RevPAR
— the right room, to the right guest, at the right price, through the right channel.

## The operating loop

1. **Read the demand signal.** Establish on-the-books (OTB) pace vs. prior-year-same-time and
   vs. forecast. Identify compression nights (high pick-up, OTB > forecast), soft nights (slow
   pace, OTB < forecast), and shoulder transitions. Check local event calendar (citywide, sports,
   concerts, holidays) for demand-catalyst or demand-depressor dates.

2. **Position rate vs. comp set.** Pull (or input) competitive-set rate data (rate-shopping
   snapshot). Determine whether the property is at rate premium, parity, or discount vs. comp.
   For compression nights, rate premium is the default; justify any exception.

3. **Traverse the raise-or-hold-rate decision tree.** See
   [`../../knowledge/hospitality-hotels-decision-trees.md`](../../knowledge/hospitality-hotels-decision-trees.md).
   The tree requires: OTB pace, comp-set position, days-to-arrival window, and demand-calendar
   context. Land on a leaf (raise / hold / lower) with the basis stated.

4. **Set or validate BAR strategy.** Best Available Rate (BAR) is the publicly-posted, fully-
   flexible rack rate for each day and room type. BAR should be:
   - Compression: at or above comp-set average rate
   - Shoulder: at or near comp-set average
   - Soft: below comp-set average only with a RevPAR-positive discount math

5. **Design length-of-stay controls (if needed).** For compression nights, calculate whether
   a minimum-stay restriction (MinLOS) improves RevPAR by protecting shoulder revenue from
   displacement by single-night arrivals. Use the displacement formula:
   > MinLOS benefit = (shoulder-night RevPAR × protected nights) − (single-night RevPAR × unrestricted fills)

6. **Model overbooking (if needed).** Traverse the overbook-or-not tree. Inputs required:
   12-month no-show rate, cancellation rate by booking window, expected same-day rebookings,
   walk cost (relocation rate + compensation + loyalty impact). Calculate expected RevPAR uplift
   and walk risk before recommending an overbook level.

7. **Calculate RevPAR impact.** Use `scripts/hotel_calc.py` (or manual formula) to compute:
   - Current RevPAR = ADR × occupancy %
   - Revised RevPAR = revised ADR × revised occupancy %
   - RevPAR delta = what the pricing move is worth in $/available room

8. **Output the recommendation.** Use the structure in step output below.

## Anti-patterns

- Setting a rate without citing OTB pace or comp-set position.
- Optimizing occupancy without checking ADR impact (may lower RevPAR).
- Applying MinLOS on soft dates (restricts demand without protecting shoulder revenue).
- Overbooking without a no-show/cancel rate basis and a walk-cost model.

## Output

A RevPAR-anchored pricing recommendation: date range, demand basis (OTB + comp-set), BAR
recommendation, LOS control (if any) with displacement math, overbooking level (if any) with
walk-risk math, and the RevPAR impact estimate. Reference
[`../../templates/rate-plan.md`](../../templates/rate-plan.md) for the artifact structure.
