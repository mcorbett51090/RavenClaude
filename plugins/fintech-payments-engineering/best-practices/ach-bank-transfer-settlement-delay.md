# Design for ACH settlement delay: hold fulfillment until funds clear

**Status:** Absolute rule
**Domain:** Payments / ACH and bank transfers
**Applies to:** `fintech-payments-engineering`

---

## Why this exists

ACH (Automated Clearing House) transfers and SEPA bank transfers are not
immediate. ACH debit can take 1–3 business days to settle, and during that
window the transaction is reversible by the bank (NSF, revocation). A product
that fulfills the order or grants subscription access the moment an ACH payment
is "initiated" may fulfil to a customer whose payment will be reversed 72 hours
later. This is a business and fraud risk: the customer has received the value but
the payment was reversed, and recovery requires manual collection effort.

## How to apply

For ACH/bank transfer payments:

1. At initiation, record the payment as `pending` (not `succeeded`) in the
   ledger and the subscription/order state.
2. Gate fulfillment on a confirmed `payment_intent.succeeded` or
   `charge.succeeded` webhook — not on the initiation event.
3. For subscriptions, hold access provisioning in a `pending_payment` state
   until settlement confirms.

```python
# ACH payment intent state machine
ACH_STATES = {
    "requires_confirmation": "Payment initiated — awaiting bank",
    "processing":            "Submitted to ACH — 1-3 business days",
    "succeeded":             "Settled — fulfill now",
    "requires_payment_method": "Failed — request new payment method",
}

def handle_payment_intent_update(pi: dict) -> None:
    if pi["payment_method_types"] != ["us_bank_account"]:
        return  # Not ACH — different flow

    if pi["status"] == "processing":
        # ACH in flight — update status but do NOT fulfill
        db.update_payment(pi["id"], status="processing")
        notify_customer_processing(pi["id"])

    elif pi["status"] == "succeeded":
        # Settlement confirmed — fulfill now
        db.update_payment(pi["id"], status="succeeded")
        ledger.post_payment(pi)
        fulfill_order(pi["metadata"]["order_id"])

    elif pi["status"] == "requires_payment_method":
        # ACH reversed / NSF
        db.update_payment(pi["id"], status="failed")
        handle_ach_failure(pi)
```

**Do:**
- Communicate the settlement delay explicitly to the customer at checkout.
- Gate all fulfillment on the `succeeded` webhook, not on initiation or
  `processing`.
- Monitor for ACH reversal events and trigger recovery workflows immediately.

**Don't:**
- Treat an ACH `processing` status as equivalent to a card `succeeded` status.
- Fulfill physical goods or provision access before ACH settlement.
- Omit the settlement delay disclosure from the checkout flow.

## Edge cases / when the rule does NOT apply

- Real-Time Payments (RTP) or Instant Payments (where supported by the bank):
  settlement is near-immediate; fulfillment can follow the confirmation event
  quickly. Verify real-time settlement is guaranteed before treating it as
  instant `[verify-at-use]`.

## See also

- [`../agents/payments-integration-engineer.md`](../agents/payments-integration-engineer.md) — owns PSP integration and settlement flows
- [`./model-the-charge-as-a-state-machine.md`](./model-the-charge-as-a-state-machine.md) — ACH adds `processing` as an intermediate state
- [`./verify-and-dedupe-webhooks.md`](./verify-and-dedupe-webhooks.md) — settlement confirmation arrives as a verified webhook

## Provenance

Standard ACH and bank-transfer payment engineering practice. ACH settlement
timelines documented by NACHA and Stripe/Adyen ACH documentation
`[verify-at-use]`. The fulfillment-on-settlement-only rule is a standard
fraud-prevention requirement for ACH payments.

---

_Last reviewed: 2026-06-05 by `claude`_
