---
description: "Compute cost-to-originate (fixed + variable per loan) and the breakeven volume that the rate swing must clear. Reach for this on a unit-economics question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Model cost-to-originate

You are running `/mortgage-lending:model-cost-to-originate` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Split the cost — Fixed cost and variable cost per loan.
2. Compute cost-to-originate — (fixed + variable × loans) ÷ loans via `mortgage_lending_calc.py cost-to-originate` (§3 #5).
3. Find the breakeven — Fixed cost ÷ margin-per-loan = breakeven volume (§3 #5).
4. Stress the rate swing — Compare breakeven to a downturn volume projection (§3 #7).

## Output
A cost-to-originate and breakeven read stressed against the rate-cycle volume swing. See [`../skills/model-cost-to-originate/SKILL.md`](../skills/model-cost-to-originate/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No borrower PII / NPI in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
