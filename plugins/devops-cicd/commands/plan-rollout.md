---
description: "Plan a safe production rollout: pick the strategy by blast radius, wire a health-gated promotion, and define the automated rollback."
argument-hint: "[service + risk profile, e.g. 'highest-traffic API, stateless, has SLOs']"
---

You are running `/devops-cicd:plan-rollout`. Use `release-engineer` + the `progressive-delivery` skill.

## Steps
1. Traverse the deploy-strategy decision tree (reversibility, statefulness, signal availability).
2. Choose canary / blue-green / flagged / rolling and name the trade.
3. Define the health signal (route to observability-sre), the abort condition, and the rollback action.
4. If a schema change is involved, sequence expand/contract first (route to database-engineering).
5. Emit the rollout plan (from `templates/canary-rollout-plan.md`) + the Structured Output block.
