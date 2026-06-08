---
description: "Quantify lost rent during unit turns and frame the work-order backlog as a retention risk. Reach for this on a turn or maintenance question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Quantify turn loss

You are running `/property-management:quantify-turn-loss` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Count vacant units and turn days — Vacant units awaiting turn and average turn days.
2. Compute lost rent — Vacant units × turn days × daily rent via `property_management_calc.py turn-time` (§3 #3).
3. Annualize the drag — Scale the per-turn loss to an annual run-rate.
4. Frame the backlog risk — Read the work-order backlog age as a renewal risk (§3 #6).

## Output
A lost-rent read annualized with the backlog framed as retention risk. See [`../skills/quantify-turn-loss/SKILL.md`](../skills/quantify-turn-loss/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No tenant PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
