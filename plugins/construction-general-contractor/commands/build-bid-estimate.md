---
description: "Run a complete GC bid estimate: read the bid package, perform a quantity takeoff by CSI division, price with sourced unit rates, apply markup vs. margin correctly, add general conditions/overhead/profit/bond, and produce a bid letter with exclusions and qualifications."
argument-hint: "[project name or bid package summary, e.g. 'Office TI, 22,000 SF, Division 3-10 self-perform, sub quotes for MEP']"
---

You are running `/construction-general-contractor:build-bid-estimate`. Use the
`estimating-and-takeoff-analyst` discipline and the `estimating-and-bidding` skill.

## Steps

1. **Read the bid package.** Identify the drawings, specifications (all divisions), addenda,
   bid form, and contract form. Note the bid due date and any owner-required bid format.

2. **Identify scope inclusions and exclusions.** List every CSI division in scope. Assign
   each division to self-perform or subcontractor. Write the exclusion list before starting
   the takeoff.

3. **Perform quantity takeoff.** Measure each scope division from the drawings, working
   systematically by CSI division. Document the drawing sheet and detail for each quantity.
   Flag ambiguous scope as an assumption or pending RFI.

4. **Price the takeoff.**
   - Labor: crew composition + hours from productivity data + unit rate (with source and date).
   - Material: quoted prices or price-book reference (with edition, date, and location factor).
   - Equipment: owned (owning/operating cost) or rented (current market quote with date).
   - Sub quotes: review each for scope completeness before including.

5. **Convert markup to margin (or confirm the basis).** Traverse the `Markup-vs-margin`
   tree in `knowledge/construction-gc-decision-trees.md`. State explicitly: "Applying X%
   markup on cost" OR "Pricing to Y% gross margin." Show the conversion formula.

6. **Assemble the complete bid.** Direct cost by trade → general conditions → overhead →
   profit → named contingency → bond → total bid price.

7. **Write the bid letter.** Include: bid basis, addenda acknowledged, exclusions, allowances,
   qualifications, bid validity period, bond status.

8. **Emit the Structured Output block** with: total bid price, margin %, top-3 scope risks,
   open items before bid day, and handoffs (gc-project-lead for SOV if awarded;
   scheduling-engineer for schedule support if time-limited).
