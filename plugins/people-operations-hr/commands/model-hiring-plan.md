---
description: "Model a capacity-tied hiring plan — back-solve the funnel pipeline for target hires, flag the leaking stage, size recruiter capacity, hand off the comp envelope. Reach for this on a hiring-plan or stuck-req question."
argument-hint: "[the situation, e.g. target hires / function / the stuck req]"
---

# Model hiring plan

You are running `/people-operations-hr:model-hiring-plan` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Set the target — hires by level/function, tied to capacity/revenue (§3 #6).
2. Back-solve the funnel — required pipeline per stage via `scripts/people_calc.py hiring-plan`.
3. Find the leaking stage — fix the lowest conversion before adding volume (§3 #3).
4. Size capacity & budget — recruiter load + comp envelope handoff to the comp analyst.

## Output
A hiring-plan model with required pipeline, the leaking stage named, recruiter capacity, and the comp-budget handoff. See [`../skills/model-hiring-plan/SKILL.md`](../skills/model-hiring-plan/SKILL.md). Traverse Tree 2 in [`../knowledge/people-ops-decision-trees.md`](../knowledge/people-ops-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; fix the leak before adding volume.
- No PII in the output; cite a source + date for every external benchmark (or mark it).
- End with owner / date / expected movement on each recommendation.
