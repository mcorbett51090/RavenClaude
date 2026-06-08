---
description: "Diagnose win-rate and sales-cycle stage-by-stage — find the leaking stage before adding leads. Reach for this on a conversion question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Diagnose funnel

You are running `/sales-revops:diagnose-funnel` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Map the stages — Lead → qual → demo → proposal → close with conversion + dwell each.
2. Find the leak — Lowest conversion or longest dwell via `revops_calc.py funnel` (§3 #3).
3. Localize the cause — Qualification, process, or comp behind the leaking stage.
4. Fix the constraint first — Then add volume — not before (§3 #3).

## Output
A stage-by-stage funnel read naming the leaking stage and the fix. Traverse Tree 2 in the decision-trees file. See [`../skills/diagnose-funnel/SKILL.md`](../skills/diagnose-funnel/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer/rep PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
