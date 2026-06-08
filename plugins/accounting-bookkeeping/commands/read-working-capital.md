---
description: "Read the cash conversion cycle (DSO + DIO − DPO) and locate trapped or surrendered cash. Reach for this on a cash question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Read working capital

You are running `/accounting-bookkeeping:read-working-capital` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. State the basis — Accrual vs cash before any figure (§3 #6).
2. Compute DSO/DPO/DIO — Days sales/payable/inventory outstanding.
3. Compute the cycle — DSO + DIO − DPO via `acctgops_calc.py working-capital` (§3 #3 #4).
4. Name the lever — Cash trapped in AR (collections) or surrendered in AP timing (§3 #3 #4).

## Output
A cash-conversion read with the basis stated and the cash lever named. Traverse Tree 2 in the decision-trees file. See [`../skills/read-working-capital/SKILL.md`](../skills/read-working-capital/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client financial PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
