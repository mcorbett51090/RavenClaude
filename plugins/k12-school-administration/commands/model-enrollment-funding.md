---
description: "Translate enrollment and ADA into funding and quantify the dollar value of each attendance point. Reach for this on a funding question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Model enrollment funding

You are running `/k12-school-administration:model-enrollment-funding` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Set enrollment and per-pupil — Enrollment count and the per-pupil funding rate (source + date it, §3 #8).
2. Apply the ADA rate — Funding scaled by average daily attendance via `k12_school_administration_calc.py enrollment-funding` (§3 #2).
3. Value an attendance point — The dollar value of each ADA point — the dual lever (§3 #2).
4. Frame the retention flow — Mid-year attrition that erodes the funded base (§3 #1).

## Output
An enrollment-to-funding read with the per-attendance-point dollar value named. Traverse Tree 1 in the decision-trees file. See [`../skills/model-enrollment-funding/SKILL.md`](../skills/model-enrollment-funding/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No student PII (FERPA) in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
