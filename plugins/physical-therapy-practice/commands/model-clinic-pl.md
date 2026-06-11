---
description: "Model the PT clinic P&L on reimbursed-visit economics — build it on the real levers (reimbursed visits, units/visit, net collection/visit, cancellation rate, labor), analyze payer mix by net collection and admin burden, and find the binding margin lever."
---

# /model-clinic-pl

Spawn `pt-practice-lead` (with the billing analyst for net collection) to model the clinic P&L.

## What it does

1. Builds the P&L on reimbursed-visit economics via [`../scripts/pt_calc.py`](../scripts/pt_calc.py) (`net_collection_per_visit`, `units_per_visit`, `cancellation_rate`, `clinic_contribution_margin`).
2. Analyzes payer mix by net collection per visit **and** administrative burden.
3. Connects plan-of-care adherence to the multi-visit revenue engine.
4. Identifies the binding margin lever (adherence → cancellations → net collection → units → labor).

## Usage

```
/model-clinic-pl
```

Then share visit volume, payer mix, net collections, and labor cost. The agent applies
[`pt-clinic-pl-and-payer-mix`](../skills/pt-clinic-pl-and-payer-mix/SKILL.md).

## Good inputs

- Delivered/reimbursed visits, units per visit, net collection per visit by payer.
- Cancellation/no-show rate and labor cost.
