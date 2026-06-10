---
description: "Model a student:teacher ratio into FTE and salary cost and check it against the budget envelope. Reach for this on a staffing question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Fit staffing to budget

You are running `/k12-school-administration:fit-staffing-to-budget` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Set the target ratio — The student:teacher ratio and current FTE.
2. Compute teachers and cost — Enrollment ÷ ratio × avg teacher cost via `k12_school_administration_calc.py staffing-ratio` (§3 #3).
3. Check the variance — FTE and dollar variance vs current and vs the budget envelope (§3 #3).
4. Tie to retention — Turnover cost that the ratio decision interacts with (§3 #7).

## Output
A staffing-to-budget read with the FTE and dollar variance vs the envelope. Traverse Tree 2 in the decision-trees file. See [`../skills/fit-staffing-to-budget/SKILL.md`](../skills/fit-staffing-to-budget/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No student PII (FERPA) in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
