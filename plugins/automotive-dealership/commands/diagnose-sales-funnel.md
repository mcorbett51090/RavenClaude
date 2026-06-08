---
description: "Diagnose the lead-to-sold funnel by conversion step — a volume gap is usually a conversion gap. Reach for this on a sales-volume question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Diagnose sales funnel

You are running `/automotive-dealership:diagnose-sales-funnel` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Map the funnel — Ups (walk-in + digital) → write-ups → sold, with a ratio each.
2. Find the leaking step — The lowest-conversion step before buying traffic (§3 #6).
3. Localize the cause — Lead handling, desking, or close discipline behind the step.
4. Fix conversion first — Then add traffic — not before (§3 #6).

## Output
A funnel read naming the leaking conversion step and the fix. See [`../skills/diagnose-sales-funnel/SKILL.md`](../skills/diagnose-sales-funnel/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
