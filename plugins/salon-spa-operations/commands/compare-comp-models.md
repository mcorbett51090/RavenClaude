---
description: "Compare salon/spa compensation models — commission vs booth/chair rental vs hybrid — with the control, overhead, and tax/risk trade, and the mandatory worker-classification flag."
argument-hint: "[salon type + chairs + current pay model + what you want to control]"
---

You are running `/salon-spa-operations:compare-comp-models`. Use `salon-spa-operations-lead` + the `choose-commission-vs-booth-rental` skill.

## Steps
1. Name what the owner is optimizing for — control of brand/schedule/client-book, or low overhead + predictable income.
2. Traverse the compensation-model tree in `knowledge/salon-spa-operations-decision-trees.md`.
3. Lay the models side-by-side: what the owner controls, what they carry, revenue shape, and who owns the client book.
4. Recommend a model with the trade stated explicitly.
5. **Flag the worker-classification test — never call a model "legal."** Route the verdict to `people-operations-hr` and payroll/tax to `accounting-bookkeeping`.
6. Emit using `templates/compensation-model-comparison.md` + the Structured Output block.
