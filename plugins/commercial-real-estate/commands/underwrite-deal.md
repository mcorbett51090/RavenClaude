---
description: "Underwrite a CRE deal in the order that prevents overpaying — in-place NOI first, separate going-in cap from IRR, price the spread, stress the debt and refi, and only then weigh the pro-forma upside."
argument-hint: "[the deal, e.g. 'a 120k sf suburban office at a 7.5 going-in cap']"
---

# Underwrite a CRE deal

You are running `/commercial-real-estate:underwrite-deal` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Re-underwrite to in-place NOI; layer each step-up as a sourced assumption (§3 #1).
2. Separate the going-in cap rate from the levered IRR — show both (§3 #2).
3. Price the cap-rate-vs-Treasury spread and place it historically (§3 #3).
4. Stress the debt: DSCR path, refi year, break rate, equity at risk (§3 #6).
5. Build the down case (step-ups removed, exit cap widened); state if it only works on the pro-forma.

## Output
An IC-ready read: in-place base case, the spread, the debt/refi stress, and the two triggers that change the answer. Use the [`../templates/ic-memo.md`](../templates/ic-memo.md).

## Guardrails
- Resist the seller's pro-forma as a base case.
- Don't quote a cap rate without its date and Treasury context.
