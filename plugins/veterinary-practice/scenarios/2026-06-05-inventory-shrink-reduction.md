---
scenario_id: 2026-06-05-inventory-shrink-reduction
contributed_at: 2026-06-05
plugin: veterinary-practice
product: inventory
product_version: "n/a"
scope: likely-general
tags: [inventory, shrink, turns, cogs, markup]
confidence: medium
reviewed: false
---

## Problem

A 4-DVM practice's cost of goods sold (drugs + medical supplies + diet/retail) was running several points above the segment range, and the owner could not explain the gap. Suspicion was supplier price creep, but the actual driver turned out to be **shrink and slow turns**: expired product written off, items dispensed but never charged, and overstocked SKUs tying up cash.

## Context

- Segment: general-practice, independent, no perpetual-inventory discipline — counts were "when we remember," reorder was by eyeball.
- Constraint: the PIMS (a mainstream system) *could* track on-hand and link dispensing to invoices, but the feature was unused — so dispensed-not-charged leakage was invisible.
- The owner conflated "COGS is high" (a P&L symptom) with "suppliers raised prices" (one of several possible causes). Classic single-cause story the decision trees warn against.

## Attempts

- Tried: decomposed the COGS variance before accepting the price-creep story. Sources of the gap, in order found: (1) **dispensed-not-charged** (missed charges at point of dispensing), (2) **expiry write-offs** from overstock, (3) genuine **supplier price** movement (smallest contributor). Outcome: reframed the problem from "negotiate with suppliers" to "fix the dispensing-to-invoice link and the reorder discipline."
- Tried: turned on the PIMS dispensing-to-invoice link and a missed-charge report; instituted reorder points + a perpetual count on the top-20 SKUs by spend (the items that drive most of the cash). Outcome: closed most of the dispensed-not-charged leak; reduced overstock.
- Tried: set a markup/pricing review on the highest-volume items so margin wasn't silently eroding on the SKUs that matter most (the §3 #6 reprice-from-cost discipline). Outcome: recovered margin on fast movers.

## Resolution

High COGS was mostly **shrink (missed charges + expiry) and weak turns**, not supplier pricing. The fix was operational discipline — dispensing-to-invoice link, missed-charge report, reorder points, and a top-SKU perpetual count — plus a markup review on fast movers. Improving inventory **turns** also freed cash that overstock had been tying up.

**Action for the next consultant hitting this pattern:** when COGS runs high, **decompose before negotiating** — separate dispensed-not-charged, expiry write-off, and true price movement; the first two are usually the bigger and the cheaper to fix. Track **inventory turns** (COGS ÷ average inventory) as the cash-efficiency metric, and reconcile dispensing to invoices in the PIMS. Reprice fast movers from the cost stack, not the neighbor's shelf (§3 #6).

**Sources (retrieved 2026-06-05):** veterinary pricing & markup discipline — https://digitail.com/blog/mastering-product-pricing-and-markup-in-veterinary-practices/ ; in-house diagnostics/inventory cost framing — https://vet-advantage.com/vet-advantage/the-economics-of-the-in-house-lab/ . COGS-range figures are segment-dependent; treat any specific number as `[ESTIMATE]` and validate against the practice's actual P&L (§3 #8).
