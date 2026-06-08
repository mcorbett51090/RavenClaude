---
description: "Assemble an AIA G702/G703 pay application from the schedule of values: work completed + stored materials this period, retainage per the contract, prior payments, and current payment due — with the back-up the architect needs to certify."
argument-hint: "[the SOV / contract sum + this period's progress + the contract retainage terms]"
---

You are running `/construction-field-management:assemble-pay-app`. Use `cost-and-change-controls-lead` + the `change-order-and-pay-application` skill.

## Steps
1. Confirm the governing contract form (AIA G702/G703 vs. EJCDC/ConsensusDocs) and the retainage % + stored-materials rules — `[verify-at-build]` against the specific contract.
2. Build/confirm the SOV line items tied to cost codes; carry executed change orders into the SOV.
3. Compute per line: scheduled value, work completed prior + this period, stored materials, total completed-and-stored, % complete, retainage held, prior payments, current payment due.
4. Reconcile the G702 summary to the G703 totals; list the back-up (lien waivers, stored-materials support) the architect needs to certify.
5. Flag any abusive front-loading or unsupported stored materials that will get the draw rejected.
6. Emit the pay-app summary + the Structured Output block (with `Field/cost/schedule impact:` and `Ball-in-court:`). Route any time-impacting change to `project-management`.
