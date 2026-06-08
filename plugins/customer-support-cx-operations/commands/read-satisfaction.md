---
description: "Read CSAT/NPS segmented by channel/tier/issue-type and tie it to FCR — never a blended score. Reach for this on a satisfaction question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Read satisfaction

You are running `/customer-support-cx-operations:read-satisfaction` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Segment the score — CSAT/NPS by channel, tier, and issue-type (§3 #3).
2. Find where it breaks — The segment dragging the blended number down.
3. Tie to FCR — Falling FCR / rising reopens usually drive the drop (§3 #4).
4. Date the benchmark — Any CSAT/FCR benchmark carries a source + date or unverified mark (§3 #8).

## Output
A segmented CSAT read localizing the break, with the FCR link. Traverse Tree 3 in the decision-trees file. See [`../skills/read-satisfaction/SKILL.md`](../skills/read-satisfaction/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
