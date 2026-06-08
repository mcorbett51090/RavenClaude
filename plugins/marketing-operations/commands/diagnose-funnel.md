---
description: "Diagnose MQL→SQL→opp→win conversion stage-by-stage — find the leaking stage before adding lead volume. Reach for this on a funnel question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Diagnose funnel

You are running `/marketing-operations:diagnose-funnel` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Map the stages — Lead → MQL → SQL → opp → win with conversion + dwell each.
2. Find the leak — Lowest conversion or longest dwell via `marketingops_calc.py funnel` (§3 #1).
3. Localize the cause — Lead quality, routing, qualification, or follow-up behind the leaking stage.
4. Fix the constraint first — Then add volume — not before (§3 #1).

## Output
A stage-by-stage funnel read naming the leaking stage and required-lead volume. Traverse Tree 1 in the decision-trees file. See [`../skills/diagnose-funnel/SKILL.md`](../skills/diagnose-funnel/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer/lead PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
