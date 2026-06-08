---
description: "Size technician and pharmacist hours against script volume PLUS clinical-service time, holding verification safety as the constraint. Reach for this on a throughput or staffing question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Size throughput and staffing

You are running `/pharmacy-operations:size-throughput-staffing` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Measure the volume — Daily script volume and the clinical-service time load (§3 #5).
2. Compute the hours — Tech and pharmacist hours via `pharmacy_operations_calc.py throughput-staffing` (§3 #5).
3. Hold safety as the constraint — Verification capacity must cover fill volume — never trade it for speed (§3 #1).
4. Name the gap — Hours needed vs current, with the verification-safety gap flagged (§3 #1).

## Output
A staffing read covering volume + clinical time with the verification-safety constraint held. Traverse Tree 1 in the decision-trees file. See [`../skills/size-throughput-staffing/SKILL.md`](../skills/size-throughput-staffing/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No patient PHI in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
