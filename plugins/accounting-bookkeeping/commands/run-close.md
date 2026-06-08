---
description: "Run the period-end close on a cadence: critical-path checklist, days-to-close, bottleneck. Reach for this on a close question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Run close

You are running `/accounting-bookkeeping:run-close` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Set the target — Days-to-close goal for the period (§3 #1).
2. Lay out the critical path — Dependency-ordered close tasks; gate on reconciliation (§3 #1 #2).
3. Compute days-to-close — Critical-path days + bottleneck via `acctgops_calc.py close-cycle` (§3 #1).
4. Attack the bottleneck — Parallelize the rest; remove the longest dependent task (§3 #1).

## Output
A critical-path days-to-close read with the bottleneck named. Traverse Tree 1 in the decision-trees file. See [`../skills/run-close/SKILL.md`](../skills/run-close/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client financial PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
