---
description: "Locate a conversion problem by funnel stage — traffic, product page, cart, checkout — instead of reading the headline rate. Reach for this when conversion is low."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Diagnose the conversion funnel

You are running `/ecommerce-dtc:diagnose-the-conversion-funnel` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Map the funnel — Sessions → product view → add-to-cart → checkout → purchase (§3 #4).
2. Find the drop-off — Locate the stage with the worst relative conversion.
3. Attribute the cause — Traffic quality, product page, price, or checkout friction.
4. Fix and re-measure — Prescribe the stage fix and track conversion.

## Output
A funnel map, the drop-off stage, the cause, and a measured fix. See [`../skills/diagnose-the-funnel/SKILL.md`](../skills/diagnose-the-funnel/SKILL.md). Traverse the matching tree in [`../knowledge/ecommerce-decision-trees.md`](../knowledge/ecommerce-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
