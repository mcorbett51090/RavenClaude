---
description: "Evaluate channels on contribution and marginal ROI under a stated attribution model — not average ROI or lead count. Reach for this on a channel or budget question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Evaluate channel mix

You are running `/marketing-operations:evaluate-channel-mix` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. State the attribution model — First/last/multi-touch named before any number (§3 #2).
2. Compute channel ROI — (Contribution − cost) ÷ cost via `marketingops_calc.py channel-roi`.
3. Read marginal ROI — The next dollar's return, not the blended average (§3 #5).
4. Reallocate — Move budget off saturated channels toward higher marginal ROI.

## Output
A channel read with the attribution model named and marginal-ROI reallocation. See [`../skills/evaluate-channel-mix/SKILL.md`](../skills/evaluate-channel-mix/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer/lead PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
