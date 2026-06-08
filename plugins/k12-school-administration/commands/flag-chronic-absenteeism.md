---
description: "Compute the chronic-absentee rate, flag it early, and size the attendance-recovery funding upside. Reach for this on an attendance question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Flag chronic absenteeism

You are running `/k12-school-administration:flag-chronic-absenteeism` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Define the threshold — Students at/over the chronic-absence threshold (source + date the definition, §3 #5 #8).
2. Compute the rate — At/over-threshold ÷ enrolled via `k12_school_administration_calc.py absenteeism` (§3 #5).
3. Flag against a trigger — Raise the early-warning flag, not at year-end (§3 #5).
4. Size the recovery upside — The funding recoverable by lifting attendance (§3 #2).

## Output
A chronic-absentee read with the early-warning flag and recovery funding upside. Traverse Tree 3 in the decision-trees file. See [`../skills/flag-chronic-absenteeism/SKILL.md`](../skills/flag-chronic-absenteeism/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No student PII (FERPA) in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
