---
description: "Model tiered-fee revenue and the blended fee, flagging inconsistent application. Reach for this on a fee or revenue question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Model fee revenue

You are running `/wealth-management-ria:model-fee-revenue` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Lay out the schedule — Tiered breakpoints and the fee at each tier.
2. Compute revenue — Σ(tier AUM × tier fee) via `riaops_calc.py aum-revenue` (§3 #3).
3. Compute the blended fee — Revenue ÷ total AUM.
4. Flag exceptions — Inconsistent breakpoints or off-schedule fees route to compliance (§3 #3 #6).

## Output
A tiered-fee revenue model and blended fee with exceptions flagged. See [`../skills/model-fee-revenue/SKILL.md`](../skills/model-fee-revenue/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client financial PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
