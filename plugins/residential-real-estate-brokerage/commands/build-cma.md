---
description: "Build a defensible comparative market analysis and a supported list-price range from adjusted comparable sales, with a seller-conversation script that prices to the comps, not the target (local figures verify-at-use)."
argument-hint: "[subject property + seller goal/timeline + a few candidate comps or the market]"
---

You are running `/residential-real-estate-brokerage:build-cma`. Use `listing-and-transaction-coordinator` + the `cma-and-pricing-strategy` skill.

> Advisory, not appraisal advice. A CMA is not an appraisal. Every price/DOM figure is `[verify-at-use]`. No client PII — work in the property and the comps, never a personal record.

## Steps
1. Capture the subject property (location, size, condition, style) and the seller's goal and timeline.
2. Select **3-6 genuinely comparable closed sales** and adjust each toward the subject explicitly. Traverse the **price a listing (CMA)** tree in `knowledge/residential-brokerage-decision-trees.md`.
3. Produce a **supported price range**, then position the list price within it on the seller's timeline and market direction — never on the seller's target. Flag local list-to-sale / DOM figures `[verify-at-use]`.
4. Draft the seller-conversation script that lets the comps carry the price and names the cost of overpricing.
5. Emit using `templates/listing-launch-plan.md` (Price section) + the Structured Output block.
