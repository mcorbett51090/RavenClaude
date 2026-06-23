---
name: strangler-fig-migration
description: "Plan an incremental strangler-fig migration off a legacy system — a facade routing one capability at a time to a new implementation behind an anti-corruption layer. Reach for this instead of a big-bang rewrite."
---

# Skill: Strangler-fig migration

Replace the old system one capability at a time, value landing continuously, rollback always a route-flip away (§2 #4).

## Step 1 — Place the facade
Put an interception point (gateway / facade / abstraction) in front of the legacy system so requests can be routed to old *or* new per capability.

## Step 2 — Pick the first capability
Choose a slice that is high-value or high-risk-to-learn and has a clean seam (from `codebase-archaeologist`). Small enough to ship; meaningful enough to prove the pattern.

## Step 3 — Build behind an anti-corruption layer
Implement the new version with an ACL translating between the legacy model and the new model (§2 #5), so the old quirks don't leak into the new design.

## Step 4 — Route incrementally
Shift traffic for that capability gradually (canary / cohort), watching SLOs and reconciliation. Keep the old path live as the rollback.

## Step 5 — Repeat, then remove the facade
Migrate capabilities one by one until the legacy system is dead, then retire the facade. Branch-by-abstraction is the in-process variant of the same idea.

> Decision support: the cutover-strategy tree in [`../../knowledge/legacy-modernization-decision-trees.md`](../../knowledge/legacy-modernization-decision-trees.md) and the pattern catalog in [`../../knowledge/modernization-patterns-reference.md`](../../knowledge/modernization-patterns-reference.md).
