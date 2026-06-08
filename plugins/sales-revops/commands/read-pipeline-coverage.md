---
description: "Read coverage as a ratio against quota by segment and close-date, not a total pipeline number. Reach for this on a coverage question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Read pipeline coverage

You are running `/sales-revops:read-pipeline-coverage` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Set the quota baseline — Remaining quota by segment and period.
2. Compute coverage — Open pipeline ÷ remaining quota via `revops_calc.py coverage`.
3. Segment it — Coverage by segment and close-date; a healthy aggregate can hide a short segment (§3 #1).
4. Compare to target ratio — Against the segment's historical win-rate-implied coverage need.

## Output
A segmented coverage read vs target ratio, naming the short segments. See [`../skills/read-pipeline-coverage/SKILL.md`](../skills/read-pipeline-coverage/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer/rep PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
