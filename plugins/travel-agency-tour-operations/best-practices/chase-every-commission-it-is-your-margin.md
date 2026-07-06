# Chase every commission — it is your margin

**Status:** Absolute rule
**Domain:** Commission management / recovery
**Applies to:** `travel-agency-tour-operations`

> Advisory operations rule. Commission terms, statement cadence, and settlement mechanics are supplier-specific — `[verify-at-use]`. No traveler PII.

---

## Why this exists

Booked commission is not paid commission. Suppliers pay on their own cadence (often post-travel), pay short, or miss bookings entirely — and an agency without a ledger has no idea which. Unchased commission is the quietest leak in the business: it's revenue you **already earned** and simply never collected. Because the work is already done, recovery is the highest-ROI activity in the agency.

## How to apply

- Maintain a **booked-vs-paid ledger** by supplier — you cannot chase what you don't track. Use [`../templates/supplier-commission-tracker.md`](../templates/supplier-commission-tracker.md).
- Reconcile every commission statement; open a claim on shorts and non-payments with the booking evidence — traverse the commission-recovery tree in [`../knowledge/travel-agency-decision-trees.md`](../knowledge/travel-agency-decision-trees.md).
- Chase on a **cadence**, not when you happen to remember; escalate per the supplier agreement or consortia support.
- Fix the **process** that let a commission slip, not just the one booking.

**Do:** ledger every earned commission; reconcile statements; chase shorts with evidence.
**Don't:** trust suppliers to pay what they owe unprompted; let recovery live in someone's memory.

## Edge cases / when the rule does NOT apply

Genuinely uncommissionable product (e.g. bare air the rail never pays commission on) shouldn't be "chased" — expecting commission there is the error. Know which bookings actually earn commission before chasing (`[verify-at-use]`).

## See also

- [`../skills/supplier-and-commission-management/SKILL.md`](../skills/supplier-and-commission-management/SKILL.md)
- Command: [`../commands/reconcile-commissions.md`](../commands/reconcile-commissions.md)

## Provenance

Codifies `supplier-and-commission-manager` house opinion and the commission-recovery decision tree. Terms: [`../knowledge/travel-agency-reference-2026.md`](../knowledge/travel-agency-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
