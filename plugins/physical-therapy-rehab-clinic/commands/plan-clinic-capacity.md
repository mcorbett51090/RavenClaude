---
description: "Plan outpatient PT/rehab clinic capacity — match provider hours and the schedule template to committed plan-of-care visit cadence, quantify the no-show revenue leak, and size mitigation to the measured rate."
argument-hint: "[clinic profile: disciplines, providers, visit volume, no-show rate, schedule pain]"
---

You are running `/physical-therapy-rehab-clinic:plan-clinic-capacity`. Use `clinic-operations-lead`.

> Advisory only. Cancellation/missed-visit fee rules are `[verify-at-use]` per payor. Use measured clinic baselines, not generic benchmarks. No patient PII.

## Steps
1. Sum **committed demand**: active plans of care × prescribed visit frequency = visits/week to place.
2. Compute **true supply**: provider hours × slots/hour, net of the measured no-show + late-cancel rate.
3. Quantify the **no-show leak**: lost visits × net rate/visit.
4. Recommend a **schedule template** matched to the case mix and a mitigation plan (reminders, enforced cancellation policy, re-book-at-the-desk, data-sized overbooking).
5. Flag the **recert re-book** hand-off to certification timing. Traverse the capacity/no-show priors in [`../knowledge/pt-clinic-decision-trees.md`](../knowledge/pt-clinic-decision-trees.md). Emit the Structured Output block.
