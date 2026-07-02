---
description: "Triage a shop's comebacks by root cause (misdiagnosis, workmanship, part quality, incomplete repair, no-fault), name the process fix per cause, and quantify the labor-GP and car-count tax so the shop fixes the pattern, not one car (benchmarks verify-at-use)."
argument-hint: "[comeback log or a recurring return pattern]"
---

You are running `/auto-repair-shop-operations:diagnose-comebacks`. Use `technician-workflow-manager` + the `ro-lifecycle-and-comeback-control` skill.

> Operations decision-support. Comeback-rate benchmarks are `[verify-at-use]` against the shop's own baseline. No customer PII — reason in RO status and cause, not customer records.

## Steps
1. Gather the comebacks and confirm each is the **same concern** as its original RO (new/unrelated = no-fault, not a quality comeback).
2. Traverse the **comeback root-cause triage** tree in `knowledge/auto-repair-shop-decision-trees.md`.
3. Group the comebacks by cause — misdiagnosis, workmanship, part quality, incomplete repair, no-fault — and name the **process fix** per group (diagnostic process, dispatch/QC, supplier/matrix tier, closeout verification, write-up clarity).
4. Quantify the cost: rework labor billed at zero (effective-labor-rate hit) plus the car-count/trust hit; set a comeback-ownership rule for workmanship returns.
5. Emit using the comeback section of `templates/repair-order-workflow.md` (or `templates/shop-kpi-dashboard.md` for a rate read) + the Structured Output block. Hand pay-plan/effective-rate strategy to `auto-repair-shop-lead` and any counter/write-up fix to `service-advisor-estimator`.
