---
description: "Model sales velocity across its four levers (deals, win-rate, ACV, cycle) and show the trade-offs. Reach for this on a speed question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Model velocity

You are running `/sales-revops:model-velocity` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Establish the baseline — Current deals, win-rate, ACV, cycle-length.
2. Compute velocity — (deals × win-rate × ACV) ÷ cycle via `revops_calc.py velocity`.
3. Test each lever — Which single lever moves the number most, and its side-effect.
4. Pick the realistic lever — Tied to the funnel diagnosis, not a wish.

## Output
A velocity model showing the moving lever and its trade-offs. See [`../skills/model-velocity/SKILL.md`](../skills/model-velocity/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer/rep PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
