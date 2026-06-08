---
description: "Quantify manual toil and the automation ROI in engineer-hours per year. Reach for this on an automate-or-not question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Quantify toil

You are running `/platform-engineering-idp:quantify-toil` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Inventory the task — Manual minutes per occurrence, frequency, and engineers affected.
2. Compute hours/yr — minutes × frequency × engineers ÷ 60 via `platform_engineering_idp_calc.py toil` (§3 #4).
3. Compare to build cost — Hours/yr saved vs the build-and-maintain cost of the self-service action.
4. Rank against adoption — Prioritize toil on high-adoption paths, not rare edge cases (§3 #7).

## Output
A toil ROI read in engineer-hours/yr with the build-vs-buy-vs-leave call. See [`../skills/quantify-toil/SKILL.md`](../skills/quantify-toil/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No internal credentials/PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
