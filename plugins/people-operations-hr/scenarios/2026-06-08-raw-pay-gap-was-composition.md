---
scenario_id: 2026-06-08-raw-pay-gap-was-composition
contributed_at: 2026-06-08
plugin: people-operations-hr
product: pay-equity
product_version: "n/a"
scope: likely-general
tags: [pay-equity, residual-gap, controls, legal-handoff, compensation]
confidence: medium
reviewed: false
---

## Problem

A board member read a headline that women at the company were paid materially less than men and demanded an immediate across-the-board adjustment. The risk runs both ways: ignoring a real pay-equity problem is a legal and retention risk, but acting on a *raw* gap — which is mostly composition, not discrimination — spends budget on the wrong fix and can itself create new inequities (§3 #5).

## Context

- Scope: company-wide, all levels and functions blended into one raw mean.
- Constraint: the raw gap conflates *who holds which roles/levels* with *whether like-for-like work is paid unequally*. The actionable number is the residual after controlling for level/role/tenure/location/performance — and even that is a *signal to investigate*, not a legal conclusion (§3 #5, §2).
- The board reasoned from a single uncontrolled mean.

## Attempts

- Tried: **separated raw from residual** (`people_calc.py pay-equity` for the illustrative split; flagged that a defensible audit uses a regression). Outcome: most of the raw gap was explained by composition — fewer women in the most senior, highest-paid band — a representation problem, not a like-for-like pay problem.
- Tried: **classified the residual.** Outcome: a small but non-negligible residual remained in one job family — a signal to investigate, not proof.
- Tried: **routed the material residual to qualified counsel under privilege** before any remediation, and framed the representation finding as a separate talent-pipeline workstream (§2).

## Resolution

The response split into two correct workstreams: a **privileged legal review** of the residual gap in the one job family (counsel's determination, not the team's), and a **representation/pipeline** initiative for the senior-band composition gap — *not* an across-the-board raw-gap adjustment. The output was a raw gap, an illustrative residual with its method explicitly stated, a classification, and the counsel handoff.

**Action for the next consultant hitting this pattern:** **never act on a raw gap; compute the residual, and route a material residual to counsel — don't conclude.** The raw gap is mostly composition; the residual is the signal; the legal determination is counsel's. See [`../knowledge/people-ops-decision-trees.md`](../knowledge/people-ops-decision-trees.md) Tree 3 and the [`../scripts/people_calc.py`](../scripts/people_calc.py) `pay-equity` mode (which is illustrative, not a regression or a legal conclusion).

Pay-equity thresholds and reporting duties are jurisdiction-/date-dependent — treat as `[unverified — training knowledge]` and route every legal determination to qualified counsel (§2, §3 #8).
