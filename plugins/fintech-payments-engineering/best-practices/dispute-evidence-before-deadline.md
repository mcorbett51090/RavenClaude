# Submit dispute evidence before the deadline; never miss it

**Status:** Absolute rule
**Domain:** Payments / disputes and chargebacks
**Applies to:** `fintech-payments-engineering`

---

## Why this exists

A chargeback dispute has a hard deadline — typically 7–21 days from the dispute
creation date depending on the card network and reason code `[verify-at-use]`.
Missing the deadline is an automatic loss: the issuer rules in the cardholder's
favour regardless of the evidence quality. Teams that treat dispute handling as
a manual process or route it through a long ticket queue routinely miss deadlines.
Every dispute must trigger an automated workflow that (a) captures all available
evidence immediately and (b) schedules a deadline reminder.

## How to apply

When a `charge.dispute.created` webhook fires, immediately:

1. Record the dispute in the database with the `evidence_due_by` timestamp from
   the webhook payload.
2. Gather the available evidence automatically (order confirmation, delivery
   proof, terms acceptance, communication history).
3. Schedule a reminder alert at `evidence_due_by - 48h` to the disputes team.
4. Submit evidence via the PSP API before the deadline — even a partial
   submission is better than missing the deadline.

```python
def handle_dispute_created(dispute: dict) -> None:
    due_by = datetime.fromtimestamp(dispute["evidence_due_by"])

    db.insert("disputes", {
        "id": dispute["id"],
        "charge_id": dispute["charge"],
        "amount_cents": dispute["amount"],
        "currency": dispute["currency"],
        "reason": dispute["reason"],
        "evidence_due_by": due_by,
        "status": "needs_response",
    })

    # Auto-gather evidence
    evidence = gather_evidence(dispute["charge"])

    # Schedule 48h-before reminder
    scheduler.schedule(
        at=due_by - timedelta(hours=48),
        task="dispute_deadline_reminder",
        dispute_id=dispute["id"],
    )

    # If evidence is complete, submit immediately
    if evidence.is_complete():
        submit_dispute_evidence(dispute["id"], evidence)
```

**Do:**
- Automate evidence gathering and deadline tracking; manual processes miss deadlines.
- Submit partial evidence before the deadline if the complete dossier isn't ready.
- Log every dispute in the ledger as a contingent liability from creation.

**Don't:**
- Route dispute handling entirely through a human ticket queue without automated
  deadline tracking.
- Wait for complete evidence before submitting — a late perfect submission is
  an automatic loss.
- Ignore disputes because the amounts are small; dispute rates affect merchant
  account standing with the card networks.

## Edge cases / when the rule does NOT apply

- Disputes you choose to accept without contesting (fraud on a clearly fraudulent
  order): post the reversal and dispute fee to the ledger immediately; no
  evidence submission needed.

## See also

- [`../agents/payments-integration-engineer.md`](../agents/payments-integration-engineer.md) — owns webhook handling including disputes
- [`./verify-and-dedupe-webhooks.md`](./verify-and-dedupe-webhooks.md) — the `charge.dispute.created` webhook that triggers this flow
- [`./double-entry-ledger-is-source-of-truth.md`](./double-entry-ledger-is-source-of-truth.md) — dispute liability is a ledger entry

## Provenance

Standard payment dispute management practice. Card network dispute timelines are
documented in Stripe, Adyen, and Braintree dispute documentation `[verify-at-use]`.
Automated deadline tracking is a standard feature of dispute management tooling.

---

_Last reviewed: 2026-06-05 by `claude`_
