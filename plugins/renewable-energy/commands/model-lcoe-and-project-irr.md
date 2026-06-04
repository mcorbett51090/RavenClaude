---
description: "Model levelized cost of energy and project IRR together, on net cost after the live incentives, since they answer different questions. Reach for this on any project-economics question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Model LCOE and project IRR

You are running `/renewable-energy:model-lcoe-and-project-irr` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Build LCOE — Lifetime cost ÷ lifetime energy, on net cost after incentives (§3 #1, #4).
2. Build project IRR — Levered and unlevered equity return over the hold (§3 #1).
3. Size on P90 — Use the P90 production estimate for financing, not P50 (§3 #6).
4. Include the life — Add degradation, inverter replacement, and O&M over 25 years (§3 #5).

## Output
An LCOE, a levered/unlevered IRR on net cost, sized to P90, with the 25-year cost profile. See [`../skills/model-lcoe-and-irr/SKILL.md`](../skills/model-lcoe-and-irr/SKILL.md). Traverse the matching tree in [`../knowledge/renewables-decision-trees.md`](../knowledge/renewables-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
