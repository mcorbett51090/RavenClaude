---
description: "Build cost and margin per acre by field so the money-losing acres are visible. Reach for this on any margin question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Build per-acre economics

You are running `/precision-agriculture:build-per-acre-economics` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Cost per acre by field — Inputs, operations, land, and overhead per acre (§3 #4).
2. Margin per acre by field — Revenue (yield × price) minus cost, by field.
3. Rank the fields — Identify the profitable and the loss-making acres.
4. Act — Map input/rotation/marketing changes to the laggard fields.

## Output
A per-acre cost-and-margin read by field with the laggards identified. See [`../skills/build-per-acre-economics/SKILL.md`](../skills/build-per-acre-economics/SKILL.md). Traverse the matching tree in [`../knowledge/ag-decision-trees.md`](../knowledge/ag-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
