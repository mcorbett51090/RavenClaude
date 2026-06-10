---
description: "Run a pay-equity review that controls for legitimate factors — compute the raw gap, then the residual after level/role/tenure/location/performance, and route a material residual to counsel. Reach for this on a pay-equity question."
argument-hint: "[the situation, e.g. the group / population in question]"
---

# Run pay-equity review

You are running `/people-operations-hr:run-pay-equity-review` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Compute the raw gap — uncontrolled; state it is mostly composition (§3 #5).
2. Control for legitimate factors — level/role/tenure/location/performance via `scripts/people_calc.py pay-equity` (illustrative; a real audit uses a regression).
3. Classify the residual — negligible → monitor; material → signal to investigate.
4. Route & remediate — material residual to qualified counsel under privilege (§2); remediation modeled to band (§3 #2).

## Output
A raw gap, a controlled/residual gap with its method stated, a classification, and the counsel handoff — never a legal conclusion. See [`../skills/run-pay-equity-review/SKILL.md`](../skills/run-pay-equity-review/SKILL.md). Traverse Tree 3 in [`../knowledge/people-ops-decision-trees.md`](../knowledge/people-ops-decision-trees.md).

## Guardrails
- The residual is a signal, not a legal conclusion; legal determinations are counsel's (§2).
- No employee PII / protected-class attribution to an individual in the output.
- End with owner / date / expected movement on each recommendation.
