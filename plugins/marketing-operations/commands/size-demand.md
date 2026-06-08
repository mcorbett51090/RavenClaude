---
description: "Back-solve the lead volume a win target requires through each stage conversion. Reach for this on a 'how many leads' question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Size demand

You are running `/marketing-operations:size-demand` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Set the win target — Target closed-won deals for the period and segment.
2. Pull stage conversion — Lead→MQL→SQL→opp→win rates from clean trailing data (§3 #7).
3. Back-solve volume — Required leads = target wins ÷ product of stage rates via `marketingops_calc.py funnel`.
4. Check the leak first — If a stage leaks, fix it before scaling volume (§3 #1).

## Output
A required-lead model with the leaking stage flagged. See [`../skills/size-demand/SKILL.md`](../skills/size-demand/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer/lead PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
