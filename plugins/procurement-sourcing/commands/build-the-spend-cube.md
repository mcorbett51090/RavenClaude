---
description: "Build and classify the spend cube by category, supplier, and business unit, surfacing tail spend, so strategy rests on visibility. Reach for this when spend is opaque."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Build the spend cube

You are running `/procurement-sourcing:build-the-spend-cube` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Aggregate the spend — Pull and unify spend across systems and units (§3 #5).
2. Classify it — Map spend to a clean category taxonomy and normalize suppliers.
3. Surface tail spend — Isolate the fragmented tail where savings hide.
4. Prioritize — Rank categories by addressable savings.

## Output
A classified spend cube, surfaced tail spend, and a savings-prioritized category list. See [`../skills/build-the-spend-cube/SKILL.md`](../skills/build-the-spend-cube/SKILL.md). Traverse the matching tree in [`../knowledge/procurement-decision-trees.md`](../knowledge/procurement-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
