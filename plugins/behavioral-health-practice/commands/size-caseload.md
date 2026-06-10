---
description: "Size clinician caseload capacity against measured demand and the no-show-adjusted fill rate, not a guessed ratio. Reach for this on a staffing or utilization question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Size caseload to demand

You are running `/behavioral-health-practice:size-caseload` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Measure demand — Visit demand and the no-show-adjusted fill rate by program.
2. Compute capacity — FTEs × target weekly billable hours ÷ avg session length via `behavioral_health_practice_calc.py caseload` (§3 #4).
3. Read the gap — Capacity in sessions vs demand → utilization and the staffing gap (§3 #4).
4. Tie to margin — Connect filled capacity to reimbursement per visit (§3 #5).

## Output
A caseload-capacity read vs demand with utilization and the staffing gap named. See [`../skills/size-caseload/SKILL.md`](../skills/size-caseload/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No patient PHI in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
