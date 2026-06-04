---
name: progressive-delivery
description: "Choose and wire a progressive-delivery strategy — blue-green, canary, rolling, or feature-flagged — by blast radius and reversibility, with a health-gated promotion and an automated, rehearsed rollback."
---

# Progressive Delivery

**Purpose:** ship to production safely by matching the rollout to the risk.

## Strategy by blast radius
| Situation | Strategy |
|---|---|
| Stateless, fast rollback | **Canary** (1% -> 10% -> 100% on signal) |
| Need instant cutover/rollback | **Blue-green** |
| Risky/irreversible behaviour change | **Feature flag** (deploy dark, release later) |
| Schema change | **Expand/contract** migration *before* the deploy |

## The health gate
A canary promotes on an **SLO / error-budget burn-rate** signal from `observability-sre`, not a timer. Define the **abort condition** and the **rollback action** before you ship, and rehearse the rollback.

## Deploy != release
Separate them: deploy the bytes dark, flip the flag to release. A bad release becomes a flag flip.
