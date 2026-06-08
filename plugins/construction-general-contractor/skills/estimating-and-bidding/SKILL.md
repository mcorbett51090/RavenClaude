---
name: estimating-and-bidding
description: "Run a complete GC estimate and bid assembly: quantity takeoff from drawings, unit pricing (labor/material/equipment), markup vs. margin conversion, subcontractor scope review, general conditions budget, overhead and profit, contingency, and bid-letter qualification. Covers original bids and change-order re-estimates."
---

# Estimating and Bidding

**Purpose:** produce a bid price that is defensible, wins at the right margin, and has no scope
gaps that will cost money post-award.

---

## Step 1 — Scope the bid before you touch a number

1. Read the full bid package: drawings, specifications (all divisions), addenda, bid form, and
   contract form.
2. Identify scope inclusions and exclusions in the bid documents. Note every ambiguity.
3. List the CSI divisions in scope. Assign each to self-perform or sub.
4. Write the exclusion list before you start the takeoff — it will grow as you read.

## Step 2 — Quantity takeoff

1. Work division-by-division from the drawings. Measure, don't estimate.
2. Use consistent units: concrete in CY, masonry in SF, steel in tons, drywall in SF, etc.
3. Add waste and productivity factors appropriate to the scope and site conditions.
4. Document the drawing sheet and detail for every quantity — you'll need to defend it.
5. For ambiguous scope (scope shown on architectural but not structural, or described in spec
   but not dimensioned), call it out as an assumption or seek an RFI before bid day.

## Step 3 — Price the takeoff

- **Labor:** crew composition (foreman + journeymen + apprentices), hours from productivity
  data, labor rates with a date and source (prevailing wage schedule, open-shop survey, or
  historical actuals). Never use an undated rate.
- **Material:** quoted prices preferred (valid for bid day); RS Means or published price
  books with the edition date and location factor as fallback. Note escalation risk on
  long-lead items.
- **Equipment:** owned (fully-burdened owning/operating cost) vs. rented (current market
  quote with date).
- **Subcontractor quotes:** review each quote for scope. A cheap sub with a narrow scope is
  the same as a scope gap. Note any exclusions in the sub's quote.

## Step 4 — Markup vs. margin conversion

**This is the most common arithmetic error in construction estimating.**

- **Markup** = profit ÷ direct cost. A 20% markup on $100 of cost → bid price of $120.
- **Margin** = profit ÷ revenue. That same $120 bid price carries a 16.7% margin.
- A contractor who targets "20% margin" but applies "20% markup" is giving away 3.3 points.
  On a $5M project, that is $165,000.

Before applying OH&P, state explicitly: "We are applying X% markup on cost" or "We are
pricing to Y% gross margin." Traverse the `Markup-vs-margin` decision tree in the knowledge
bank to confirm the conversion is correct.

## Step 5 — Assemble the complete bid

| Line | What goes here |
|---|---|
| Direct cost (by trade) | Labor + material + equipment per takeoff |
| Subcontractor total | Sum of reviewed sub quotes + applicable GC markup |
| GC general conditions | Superintendent, PM, project engineer, temp facilities, equipment, insurance |
| Overhead allocation | Home-office overhead % (typically 5–10% of revenue, depending on volume) |
| Profit | State as a % of cost (markup) or % of revenue (margin) — not both simultaneously |
| Contingency | Named contingency items only (e.g., "3% concrete coordination allowance") |
| Bond | 1–3% depending on bond rate — verify with surety |
| Total bid price | Sum of above |

## Step 6 — Write the bid letter

The bid letter is a contract document. It must include:

- Bid basis: lump sum, GMP, or unit price
- Addenda acknowledged: list all
- Exclusions: everything not in your price
- Allowances: named items with dollar amounts
- Qualifications: conditions, assumptions, alternates priced
- Bid validity period (typically 30–90 days)
- Bond included/excluded

## Change-order re-estimation

Apply the same discipline with a tighter scope. The contract usually specifies the markup
rate (e.g., "15% OH&P on self-performed work, 10% on sub work"). Apply it consistently.
Always price time impact separately — additional days are a separate line item from the
direct cost, and the contract may cap OH&P on direct cost but allow full time-extension
recovery.

---

## Anti-patterns

- Markup and margin conflated in the same calculation.
- Labor rate without a date or source.
- Sub quote accepted without a scope review.
- Contingency applied as a global unnamed percentage.
- Bid letter with no exclusions section.

## Output

A completed bid workbook (cost by trade, marked-up total, general conditions) plus a bid
letter with inclusions/exclusions/qualifications. Reference template:
[`../../templates/bid-package.md`](../../templates/bid-package.md).
