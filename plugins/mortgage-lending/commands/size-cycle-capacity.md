---
description: "Measure app-to-close cycle, find the bottleneck stage, and size processor/LO capacity as a function of cycle — staff to the cycle, not a ratio. Reach for this on a cycle or staffing question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Size cycle and capacity

You are running `/mortgage-lending:size-cycle-capacity` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Measure the cycle — App-to-close days and dwell by stage.
2. Find the bottleneck — The stage whose dwell dominates the cycle (§3 #2).
3. Compute capacity — Processors × loans-per-processor-at-cycle via `mortgage_lending_calc.py cycle-capacity` (§3 #4).
4. Plan for the swing — Staff to the rate-cycle breakeven, not the peak (§3 #7).

## Output
A cycle/capacity read with the bottleneck stage and staffing gap named. Traverse Tree 2 in the decision-trees file. See [`../skills/size-cycle-capacity/SKILL.md`](../skills/size-cycle-capacity/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No borrower PII / NPI in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
