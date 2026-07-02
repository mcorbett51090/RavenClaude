---
description: "Model a provider's pay across commission tiers vs hourly-plus-commission vs booth rent vs hybrid on their real book, compare shop and provider outcomes, and flag the worker-classification (employee vs 1099) consequence for a professional (economics only, verify-at-use)."
argument-hint: "[provider's service revenue + hours + product cost + who controls the chair]"
---

You are running `/salon-spa-operations:model-compensation`. Use `stylist-chair-economics-advisor` + the `compensation-models-commission-vs-booth-rent` skill.

> Economic decision-support, **not** legal, tax, or employment-classification advice. The employee-vs-1099 determination and any lease/tax question route to a licensed professional. Benchmarks are `[verify-at-use]`. No client PII.

## Steps
1. Capture the provider's real book — service revenue, hours booked/available, product/back-bar cost — and **who controls the chair** (schedule, product, pricing).
2. Traverse the **compensation model** tree in `knowledge/salon-spa-decision-trees.md`.
3. Model each model (commission tiers / hourly + commission / booth rent / hybrid) on that book, showing both the provider take-home and the shop contribution, plus the booth-rent break-even fill.
4. Flag the worker-classification signal from who controls the chair as `[verify-at-use]` and route the determination to a licensed professional — model the money, do not render the legal call.
5. Emit using the provider-economics section of `templates/salon-kpi-dashboard.md` + the Structured Output block; cite `best-practices/choose-the-comp-model-deliberately.md`.
