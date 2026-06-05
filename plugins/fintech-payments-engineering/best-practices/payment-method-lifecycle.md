# Manage payment method lifecycle: create, update-on-expiry, and retire

**Status:** Pattern
**Domain:** Payments / payment method management
**Applies to:** `fintech-payments-engineering`

---

## Why this exists

A stored payment method (a card, a bank account token) has a lifecycle: it is
created, it may be updated (card expiry, account change), and it eventually
becomes unusable. Teams that don't manage this lifecycle discover it at
subscription renewal: a declined charge on an expired card that the customer
updated months ago, where the update was never applied to the stored token. Card
networks provide "card updater" services and the PSP exposes lifecycle webhooks
precisely to prevent this failure class. Not handling them means avoidable
involuntary churn.

## How to apply

**On creation:** store the payment method token (not the raw card number — house
opinion #5), along with `expiry_month`, `expiry_year`, and the `fingerprint`
(for deduplication).

**On `customer.updated` / `payment_method.updated` webhooks:** update the stored
card metadata (expiry, last-four) and re-assign as the default payment method
if it replaces an existing one.

**Network card updater:** enable the PSP's automatic card updater service (Stripe
Account Updater, Visa/Mastercard network updates `[verify-at-use]`); this silently
refreshes tokens when a card is reissued without requiring customer action.

**Proactive expiry handling:** 60 days before expiry, trigger a "please update
your card" communication workflow so the customer acts before the renewal charge.

```python
def handle_payment_method_updated(pm: dict) -> None:
    stored = db.get_payment_method(pm["id"])
    if not stored:
        return  # Not ours — ignore

    db.update_payment_method(pm["id"], {
        "exp_month": pm["card"]["exp_month"],
        "exp_year": pm["card"]["exp_year"],
        "last4": pm["card"]["last4"],
        "updated_at": datetime.utcnow(),
    })
    # If this is the customer's default, re-evaluate subscription
    if stored.is_default:
        billing.refresh_default_payment_method(stored.customer_id)
```

**Do:**
- Handle `payment_method.updated` and `customer.updated` webhooks to keep
  stored metadata current.
- Enable the PSP's network card updater to handle reissued cards automatically.
- Proactively communicate pending expiries before they cause a failed renewal.

**Don't:**
- Store card numbers or CVVs — store only PSP-issued tokens (house opinion #5).
- Let a payment method persist in `active` status after `payment_method.detached`
  events.
- Use expiry date alone as a decline predictor — card updater may have already
  refreshed the token.

## Edge cases / when the rule does NOT apply

- Single-use payment (guest checkout with no stored method): no lifecycle
  management needed; the PSP token is used once and discarded.

## See also

- [`../agents/payments-integration-engineer.md`](../agents/payments-integration-engineer.md) — owns PSP integration and webhook handling
- [`./minimize-pci-scope-with-tokenization.md`](./minimize-pci-scope-with-tokenization.md) — only PSP tokens are stored; lifecycle management operates on tokens
- [`./dunning-without-churning.md`](./dunning-without-churning.md) — expired/updated payment methods are the first dunning intervention point

## Provenance

Standard payment method lifecycle management practice. Stripe customer.updated,
payment_method.updated, and card-updater documentation `[verify-at-use]`.
The proactive-expiry communication pattern is a documented best practice in
subscription billing engineering.

---

_Last reviewed: 2026-06-05 by `claude`_
