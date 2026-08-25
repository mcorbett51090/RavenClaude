---
name: screening-vendor-invoices
description: Screens a supplier invoice against the purchase order and the approval matrix, flagging quantity, price and duplicate-payment discrepancies before the invoice reaches the approver. Use when an invoice arrives for a purchase order, when a payment run is being prepared, or when an approver asks why an invoice was held.
---

# screening-vendor-invoices

Turns an invoice into a short list of discrepancies an approver can act on, so the
approval decision is about judgement rather than arithmetic.

## Not for

- Deciding whether to pay — this screens; a person approves.
- Tax determination or filing — route to the tax owner.
- Supplier onboarding and bank-detail changes, which are a fraud surface with their own
  control and must never be handled here.

## Procedure

1. Match the invoice to its purchase order by number, then by supplier and amount.
2. Compare line by line against [the tolerance table](reference/tolerances.md).
3. Check for a duplicate: same supplier, same amount, within the lookback window.
4. Resolve the approver from the approval matrix by amount and cost centre.
5. Emit the discrepancy list. An empty list is a result — say so explicitly.

## Escalation

A bank-detail change on the invoice, a supplier not in the master record, or a duplicate
already paid goes to the controller before anything else happens.
