---
description: "Diagnose application-to-funded fall-out stage-by-stage and name the worst fallout stage — fix it before buying more apps. Reach for this on a pull-through question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Diagnose pull-through

You are running `/mortgage-lending:diagnose-pullthrough` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Map the stages — App → approved → clear-to-close → funded, with the rate at each (§3 #1).
2. Find the worst fallout — Lowest stage rate via `mortgage_lending_calc.py pullthrough` (§3 #1).
3. Localize the cause — Cycle bottleneck, documentation, or a compliance step (route the compliance cause out, §3 #6).
4. Fix the leak first — Then buy more apps — not before (§3 #1).

## Output
A stage-by-stage fallout read naming the worst fallout stage and the fix. Traverse Tree 1 in the decision-trees file. See [`../skills/diagnose-pullthrough/SKILL.md`](../skills/diagnose-pullthrough/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No borrower PII / NPI in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
