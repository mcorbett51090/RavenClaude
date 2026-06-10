---
scenario_id: 2026-06-09-velocity-metric-got-gamed
contributed_at: 2026-06-09
plugin: engineering-management
product: delivery-metrics
product_version: "n/a"
scope: likely-general
tags: [dora, velocity, goodhart, metrics, stack-rank]
confidence: medium
reviewed: false
---

## Problem

A director asked an EM to rank individuals by story points and commit counts to feed calibration. The risk: the moment a system signal becomes an individual stack-rank input it gets gamed and the signal dies (Goodhart) — flow and DORA measure the *system*, never the person (§3 #3).

## Context

- The team had just adopted DORA and throughput dashboards as a delivery-health signal.
- Constraint: measure flow and outcomes, never lines or commits; never rank a person by a velocity metric (§3 #3).
- Within a sprint of the ranking request, point inflation and trivial-commit splitting appeared.

## Attempts

- Tried: **separated system signals from individual evaluation** — kept DORA/throughput as a team health read with baselines (§3 #3). Outcome: the bottleneck (a slow review queue) became visible once nobody was gaming the number.
- Tried: **reframed the director's ask** around the actual goal (predictability) and offered a system-improvement plan instead of a ranking (§3 #3). Outcome: the calibration input reverted to dated behavioral evidence (§3 #4), not point counts.
- Tried: **fixed the review-queue constraint** (WIP limit + reviewer rotation) rather than pushing people harder. Outcome: lead time dropped without a velocity crackdown.

## Resolution

The fix was to **keep the metric a system signal and fix the constraint**, not to rank people by it. The output was a team-health read with the bottleneck named and a behavioral-evidence calibration path.

**Action for the next manager hitting this pattern:** **never let a flow/DORA metric become an individual stack-rank input — it will be gamed and the signal will die.** Use the metric to improve the system; evaluate people on dated behavior and impact (§3 #3 #4). DORA bands are date-dependent — cite the report year (§3 #8). See Tree 2 and the `improve-team-flow` skill.
