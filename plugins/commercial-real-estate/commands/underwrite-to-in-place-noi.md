---
description: "Build a CRE base case on contractual in-place income before any pro-forma step-up — separating real income from assumed growth so the return rests on something sourced. Reach for this when a deal is being sold on stabilized rents."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Underwrite to in-place NOI

You are running `/commercial-real-estate:underwrite-to-in-place-noi` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Pin in-place NOI — Build NOI from the actual rent roll and trailing opex — contractual rent, current occupancy, real recoveries.
2. Layer step-ups as explicit assumptions — Every mark-to-market, lease-up, and bump becomes a named line with a source and a probability, not baked into a blended growth rate.
3. Separate going-in cap from IRR — Show today's income yield and the hold-period levered IRR side by side — they answer different questions (§3 #2).
4. Stress the down case — Re-run with the step-ups removed and a wider exit cap; if the deal only works on the pro-forma, say so plainly.

## Output
An in-place base case, a sourced step-up bridge to the pro-forma, and the going-in-cap-vs-IRR pair with a down case. See [`../skills/underwrite-to-in-place-noi/SKILL.md`](../skills/underwrite-to-in-place-noi/SKILL.md). Traverse the matching tree in [`../knowledge/cre-decision-trees.md`](../knowledge/cre-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
