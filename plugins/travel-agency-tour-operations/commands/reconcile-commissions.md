---
description: "Reconcile booked vs paid commission by supplier, surface the gaps, and produce a recovery chase worklist with owners and cadence — because booked commission is not paid commission (settlement terms verify-at-use)."
argument-hint: "[period + supplier(s) + booked vs paid data if available]"
---

You are running `/travel-agency-tour-operations:reconcile-commissions`. Use `supplier-and-commission-manager` + the `supplier-and-commission-management` skill.

> Advisory, not accounting or legal advice. Rates, splits, and settlement cadence are `[verify-at-use]` per supplier agreement. **No traveler PII** — reference bookings by internal ID, never traveler names or payment data.

## Steps
1. Assemble the **booked-vs-paid ledger** by supplier: commissionable value, rate `[verify-at-use]`, commission earned, statement received?, amount paid, gap.
2. For each gap, traverse the **commission-recovery chase** tree in `knowledge/travel-agency-decision-trees.md` to classify the cause (unbilled / short / past due) and the chase step (match statement → open claim → escalate).
3. Note the **air rail** (BSP/ARC) where relevant — don't chase commission bare air never pays.
4. Assign an **owner + cadence** to each chase, and name the **process fix** that stops the leak recurring (not just this booking).
5. Emit using `templates/supplier-commission-tracker.md` + the Structured Output block, reporting commission capture rate and the biggest leak.
