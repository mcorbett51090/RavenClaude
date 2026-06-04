---
description: "Split the combined ratio into loss and expense, then attritional and catastrophe, so a deteriorating result is diagnosed correctly. Reach for this on any result question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Decompose the combined ratio

You are running `/insurance-pc:decompose-the-combined-ratio` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Split loss vs expense — Loss ratio and expense ratio separately; under 100 combined is underwriting profit (§3 #1).
2. Strip catastrophe — Separate cat load (~7.6 pts in 2025) from the attritional loss ratio (§3 #4).
3. Attribute to line of business — Decompose by line — the mix, not the average, tells the story (§3 #6).
4. Locate the driver — Name whether the move is expense, attritional loss, cat, or mix before prescribing.

## Output
A loss/expense, attritional/cat, by-line decomposition with the driver located. See [`../skills/decompose-the-combined-ratio/SKILL.md`](../skills/decompose-the-combined-ratio/SKILL.md). Traverse the matching tree in [`../knowledge/pc-decision-trees.md`](../knowledge/pc-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
