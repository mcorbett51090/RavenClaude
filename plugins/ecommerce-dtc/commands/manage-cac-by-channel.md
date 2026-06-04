---
description: "Read CAC by channel and cohort and allocate budget to efficiency, instead of a blended number. Reach for this when CAC climbs."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Manage CAC by channel

You are running `/ecommerce-dtc:manage-cac-by-channel` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Split CAC by channel — Spend ÷ new customers per channel (§3 #5).
2. Match to cohort LTV — Read each channel's CAC against its cohort's realized LTV (§3 #1).
3. Find the inefficiency — Creative fatigue, auction pressure, or channel saturation.
4. Reallocate — Shift budget to channels holding LTV:CAC above 3:1.

## Output
A by-channel CAC, the LTV match, the inefficiency, and a reallocation. See [`../skills/manage-cac-by-channel/SKILL.md`](../skills/manage-cac-by-channel/SKILL.md). Traverse the matching tree in [`../knowledge/ecommerce-decision-trees.md`](../knowledge/ecommerce-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
