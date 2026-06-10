---
scenario_id: 2026-06-08-hired-before-deflecting
contributed_at: 2026-06-08
plugin: customer-support-cx-operations
product: deflection
product_version: "n/a"
scope: likely-general
tags: [deflection, cost-to-serve, headcount, contact-drivers]
confidence: medium
reviewed: false
---

## Problem

A head of support saw a backlog and proposed hiring a batch of agents. The risk: headcount adds recurring cost forever, while a large share of the volume was repetitive, deflectable contacts that self-service could remove — modeling deflection first changes the answer (§3 #1).

## Context

- Channel: mixed email + chat, high-volume consumer support.
- Constraint: the cheapest contact never reaches an agent; deflection is recurring savings vs a recurring hire (§3 #1).
- Leadership reasoned from the backlog snapshot.

## Attempts

- Tried: **clustered contact drivers before sizing hires.** Outcome: a handful of drivers (password resets, order status) made up a large share of volume — all deflectable.
- Tried: **modeled deflection savings** (`supportops_calc.py deflection`). Outcome: deflecting the top drivers removed enough recurring volume to shrink the staffing gap sharply.
- Tried: **compared deflection savings to the hire cost** (§3 #1). Outcome: KB + self-service investment paid back faster than the headcount and lowered cost-to-serve permanently.

## Resolution

The response was a **self-service/KB build on the top drivers, then staff the residual volume** — not a hiring wave. The output was the contact-driver ranking, the deflection model, and a smaller, justified staffing number.

**Action for the next consultant hitting this pattern:** **model deflection before sizing headcount.** A hire is recurring cost; a deflected contact is recurring savings. Cluster the contact drivers and deflect the repetitive volume first. See Tree 1 and the `supportops_calc.py` `deflection` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
