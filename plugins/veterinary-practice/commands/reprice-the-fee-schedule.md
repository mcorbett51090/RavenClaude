---
description: "Reprice fees from the cost-of-service stack and medical value, not the neighbor's prices, to recover margin without losing position. Reach for this when margin erodes despite volume."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Reprice the fee schedule

You are running `/veterinary-practice:reprice-the-fee-schedule` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Build the cost stack — Cost-of-service per fee: labor, materials, capacity (§3 #6).
2. Set value-based fees — Price to cost plus medical value, not the competitor down the road.
3. Model the impact — Project margin and any volume sensitivity from the repricing.
4. Position it — Separate margin recovery from market positioning in the recommendation.

## Output
A cost-stack-anchored fee schedule, a margin/volume model, and a positioning note. See [`../skills/reprice-the-fee-schedule/SKILL.md`](../skills/reprice-the-fee-schedule/SKILL.md). Traverse the matching tree in [`../knowledge/vet-decision-trees.md`](../knowledge/vet-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
