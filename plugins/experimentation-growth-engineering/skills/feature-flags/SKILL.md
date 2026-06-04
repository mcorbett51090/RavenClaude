---
name: feature-flags
description: "Use feature flags safely: match the flag type to its purpose (release/experiment/ops/permission), give every risky change a kill switch, roll out progressively gated by a health signal, evaluate deterministically and fail-safe, and manage the flag lifecycle to prevent debt."
---

# Feature Flags

## Type by purpose
| Type | Lifespan |
|---|---|
| Release | temporary (remove after launch) |
| Experiment | until decision |
| Ops (kill switch) | long-lived |
| Permission/entitlement | permanent |

Treating all flags the same grows debt.

## Safe rollout
Kill switch for every risky change (off without a deploy). Progressive 1% -> 10% -> 100% gated by a **health signal** (with devops-cicd/observability-sre).

## Evaluate + lifecycle
Deterministic + sticky; **fail-safe defaults** when the service is unreachable. Every temp flag: **owner + removal date**. Stale flags = combinatorial config debt + incidents.
