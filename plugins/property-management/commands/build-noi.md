---
description: "Build the EGI-to-NOI bridge from gross potential rent and translate to value at a cap rate. Reach for this on an NOI or valuation question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Build NOI

You are running `/property-management:build-noi` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Set gross potential rent — GPR at asking, the starting line for the bridge.
2. Subtract vacancy and loss — Vacancy, loss-to-lease, concessions, bad debt → effective gross income (§3 #5).
3. Add other income, subtract opex — Other income in, operating expense out, capex below the line via `property_management_calc.py noi` (§3 #4 #7).
4. Translate to value — NOI ÷ cap rate, with the cap-rate source + date marked (§3 #8).

## Output
An EGI-to-NOI bridge with optional cap-rate value, each line baselined. Traverse Tree 1 in the decision-trees file. See [`../skills/build-noi/SKILL.md`](../skills/build-noi/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No tenant PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
