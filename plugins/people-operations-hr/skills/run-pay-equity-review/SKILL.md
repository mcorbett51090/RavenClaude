---
name: run-pay-equity-review
description: "Run a pay-equity review that controls for legitimate factors — compute the raw gap, then the residual after level/role/tenure/location/performance, and route a material residual to counsel. Reach for this on a pay-equity question."
---

# Skill: Run pay-equity review

The raw gap is not the finding; the residual after controls is — and that residual is a signal, not a legal conclusion (§3 #5, §2).

## Step 1 — Compute the raw gap
Mean/median pay by group, uncontrolled. State explicitly that this is mostly composition.

## Step 2 — Control for legitimate factors
Stratify by level / role / tenure / location / performance. Use [`../../scripts/people_calc.py`](../../scripts/people_calc.py) `pay-equity` for an *illustrative* residual — a defensible audit uses a regression.

## Step 3 — Classify the residual
Negligible → document method + monitor on cadence. Material → signal to investigate.

## Step 4 — Route & remediate
A material residual goes to qualified counsel under privilege (§2); remediation is modeled to the band and budgeted (§3 #2, #6).

## Output
A raw gap, a controlled/residual gap with its method stated, a classification, and the counsel handoff — never a legal conclusion. Traverse Tree 3 in [`../../knowledge/people-ops-decision-trees.md`](../../knowledge/people-ops-decision-trees.md).
