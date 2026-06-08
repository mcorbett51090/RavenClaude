---
description: "Run a full inventory plan: days-supply by segment, floor-plan cost, aging analysis with hold-vs-wholesale recommendations, recon SLA status, sourcing gaps, and optionally desk a specific deal."
argument-hint: "[context, e.g. 'used inventory 120 units, 58-day supply overall, 3 units over 90 days, recon avg 9 days' OR 'desk: customer wants $450/month, ACV $14k, asking $18k on trade, vehicle cost $28k']"
---

You are running `/automotive-dealership:plan-inventory-and-desking`. Use the
`inventory-and-desking-analyst` discipline and the `inventory-and-desking` skill.

## Steps

1. **Gather inventory inputs.** Request (or read from context): units on hand by segment,
   prior 30/60-day retail rate by segment, floor-plan balance and rate, recon-in-process
   count and average age. If inputs are partial, state assumptions.

2. **Calculate days-supply by segment.** Apply: `Units on hand ÷ (monthly rate ÷ 30)`.
   Flag segments outside target range (general used target: ~45 days [verify-at-use]).
   Calculate daily floor-plan cost: `(balance × annual rate) ÷ 365`.

3. **Run aging analysis.** Bucket into 0–30 / 31–60 / 61–90 / 91+ days. For each
   over-60-day unit, calculate cumulative holding cost and flag the hold-vs-wholesale
   decision. Traverse the `Hold-vs-wholesale` tree in
   `knowledge/automotive-dealership-decision-trees.md` for any specific unit evaluation.

4. **Assess recon pipeline.** Identify average days acquisition-to-retail-ready vs
   target (≤5 business days [verify-at-use]). Flag units over 7 business days in recon.

5. **Identify sourcing gaps.** Quantify missed gross on under-supplied segments.
   Recommend sourcing channels for each gap (auction, dealer trade, direct conquest buy).

6. **Desk the deal (if provided).** Calculate trade spread, front-end gross, payment
   sensitivity matrix (2–3 rate/term combos), pencil progression. Flag F&I opportunity.
   Fill `templates/desking-worksheet.md`.

7. **Output the plan.** Segment days-supply table, aging action list (hold/reduce/wholesale
   per unit), recon SLA status, sourcing plan, and deal structure (if desking).
   Emit the Structured Output JSON block with handoffs
   (`fixed-ops-analyst` for recon RO issues, `fni-advisor` for F&I on the deal,
   `dealership-ops-lead` for whole-store days-supply context).
