---
description: "Design an incremental strangler-fig migration off a legacy system, behind an anti-corruption layer. Reach for this instead of planning a big-bang rewrite."
argument-hint: "[the system / capability to migrate]"
---

# Plan strangler migration

You are running `/legacy-modernization:plan-strangler-migration` for `$ARGUMENTS`. Run it the way the `migration-engineer` would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §2.

## Steps (traverse top-to-bottom; do not skip)
1. Place the facade — an interception point routing each capability to old or new.
2. Pick the first capability — high-value or high-learning, with a clean seam.
3. Build behind an anti-corruption layer — translate at the boundary (§2 #5).
4. Route incrementally — shift traffic gradually, old path as the rollback.
5. Repeat, then remove the facade — until the legacy system is dead.

## Output
A strangler-fig migration plan in the [`../templates/strangler-fig-migration-plan.md`](../templates/strangler-fig-migration-plan.md) shape. See [`../skills/strangler-fig-migration/SKILL.md`](../skills/strangler-fig-migration/SKILL.md) and the cutover-strategy tree in [`../knowledge/legacy-modernization-decision-trees.md`](../knowledge/legacy-modernization-decision-trees.md).

## Guardrails
- Strangle, don't stop the world (§2 #4) — value lands continuously, rollback a route-flip away.
- Commit to retiring each migrated legacy path, not just adding the new one alongside.
- Hand DDL mechanics to `database-engineering` and traffic-shift automation to `devops-cicd`.
