---
description: "Diagnose why delivery is unpredictable using flow + DORA as system signals, find the constraint, and fix it — never by velocity-quota'ing people."
argument-hint: "[the delivery problem, e.g. missed dates / slow lead time / the data you have]"
---

# Improve team flow

You are running `/engineering-management:improve-team-flow` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Measure, don't guess — lead time, WIP, change-fail, MTTR as **system** signals with a baseline (§3 #3).
2. Find where time goes — high WIP / rework / blocked dependencies / estimation churn; traverse Tree 2.
3. Fix the constraint — limit WIP, shrink batch size, make dependencies visible (Little's Law).
4. Check the people cost — if the fix is "push harder," STOP; that's a velocity crackdown, not a system fix (§3 #3).

## Output
A flow diagnosis with the constraint named and a sustainable fix. See [`../skills/improve-team-flow/SKILL.md`](../skills/improve-team-flow/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; never rank a person by velocity/lines/commits.
- DORA bands are date-dependent — cite report year + retrieval date, or mark `[unverified]` (§3 #8).
- End with owner / date / expected change on each recommendation.
