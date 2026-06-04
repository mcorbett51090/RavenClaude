---
description: "Rank comparable units against each other, normalized for format and daypart, to find where the margin actually is. Reach for this on a portfolio review."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Rank multi-unit variance

You are running `/restaurant-operations:rank-multi-unit-variance` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Normalize the comparison — Group units by format/daypart so the comparison is apples-to-apples (§3 #7).
2. Rank on prime cost and margin — Order units on prime cost and four-wall margin within each group.
3. Isolate the spread — Quantify best-vs-worst and attribute it to operations, not format.
4. Prescribe to the laggards — Map the top quartile's practices to the bottom.

## Output
A normalized store ranking, the best-vs-worst spread, and a laggard improvement plan. See [`../skills/rank-multi-unit/SKILL.md`](../skills/rank-multi-unit/SKILL.md). Traverse the matching tree in [`../knowledge/restaurant-decision-trees.md`](../knowledge/restaurant-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
