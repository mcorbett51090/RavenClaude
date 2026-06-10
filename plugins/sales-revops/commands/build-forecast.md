---
description: "Build a stage-weighted, aged forecast with coverage — surface the at-risk deals. Reach for this on a forecast question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Build forecast

You are running `/sales-revops:build-forecast` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Pull the pipeline — Open deals by stage, value, close-date, and age.
2. Weight by stage win-rate — Σ(value × historical stage win-rate); a commit is an input, not the model (§3 #2).
3. Age and haircut — Flag deals past expected close or beyond stage-normal dwell; apply a slip haircut (§3 #6).
4. Compare to coverage — Open pipeline ÷ remaining quota vs target ratio via `revops_calc.py coverage` (§3 #1).

## Output
A stage-weighted, aged forecast with the coverage ratio and at-risk deals named. Traverse Tree 1 in the decision-trees file. See [`../skills/build-forecast/SKILL.md`](../skills/build-forecast/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer/rep PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
