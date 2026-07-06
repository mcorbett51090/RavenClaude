---
name: tuition-and-subsidy-billing
description: "Route and collect childcare tuition on the right rail: private-pay vs CCDF/state subsidy vs blended, the parent-fee/co-pay split, authorization and attendance rules that drive subsidy payment, and reconciliation as receivables. State-specific subsidy rules are verify-at-use."
---

# Tuition & Subsidy Billing

A childcare seat can be billed on more than one rail, and the rail changes what actually gets collected. Everything about subsidy programs (CCDF and state-specific variants) is **jurisdiction-specific and `[verify-at-use]`** — confirm against the current state/agency rule before it drives a bill.

## The loop

1. **Determine the billing route.** Private-pay, subsidy-funded (CCDF / state program), or a blend of subsidy plus a parent co-pay. The route decides the collection mechanics — see the tuition-vs-subsidy billing-route tree in [`../../knowledge/childcare-decision-trees.md`](../../knowledge/childcare-decision-trees.md).
2. **Split subsidy from parent fee explicitly.** A subsidized seat almost always still has a parent portion (co-pay / parent fee). Collect it as deliberately as the private-pay tuition — an uncollected co-pay is uncollected revenue `[verify-at-use, state-specific]`.
3. **Track the authorization.** Subsidy is paid against an authorization with a start, an end, and usually attendance. Authorizations lapse; a lapsed authorization is an unfunded seat. Treat the authorization as a live, expiring asset.
4. **Bill against the payment driver.** Many subsidy programs pay on attendance (or enrolled days) with their own reporting cadence — bill and report on that driver, not on a generic invoice, or the payment is delayed or denied.
5. **Reconcile subsidy as accounts-receivable.** Subsidy money is receivables to be chased, matched, and reconciled — not money that simply arrives. Age it, match it to authorizations, and follow up on shortfalls.

## Metrics

| Metric | Reads | Note |
|---|---|---|
| Collection rate by rail | collected / billed, private vs subsidy | Isolates where the leak is |
| Parent-fee / co-pay collection | co-pays collected / due | Often the quietest revenue leak |
| Authorization lapse rate | seats with expired auth | Each lapse = an unfunded seat |
| Subsidy A/R aging | days subsidy outstanding | Subsidy is receivables, manage it |

## Anti-patterns

- Treating a subsidized seat as "free to the family" and skipping the co-pay.
- Letting authorizations expire unnoticed.
- Invoicing subsidy without the attendance/reporting the program pays on.
- Booking subsidy as received instead of reconciling it as A/R.

## See also

- [`../enrollment-and-waitlist-management/SKILL.md`](../enrollment-and-waitlist-management/SKILL.md) — the route is decided when the family commits.
- Reference: [`../../knowledge/childcare-reference-2026.md`](../../knowledge/childcare-reference-2026.md) (CCDF/subsidy basics — verify-at-use, state-specific).
- Best practices: [`../../best-practices/enroll-the-waitlist-before-you-discount.md`](../../best-practices/enroll-the-waitlist-before-you-discount.md), [`../../best-practices/staff-to-ratio-is-the-cost-model.md`](../../best-practices/staff-to-ratio-is-the-cost-model.md).
