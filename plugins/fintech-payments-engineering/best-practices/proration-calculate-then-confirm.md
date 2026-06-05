# Calculate proration, preview it to the customer, then confirm

**Status:** Pattern
**Domain:** Subscription billing / proration
**Applies to:** `fintech-payments-engineering`

---

## Why this exists

A mid-cycle plan change (upgrade, downgrade, seat addition) creates a proration:
a credit for unused time on the old plan and a charge for the remaining time on
the new plan. Getting the math wrong — especially with multi-currency, annual
plans, or partial-day granularity — produces an incorrect invoice that may
overcharge or undercharge the customer. The correct workflow is: (1) calculate
the proration preview, (2) show it to the customer before applying it, (3)
confirm and apply only after acknowledgment. This matches how Stripe and Paddle
model it, and it is the only flow that prevents surprise charges.

## How to apply

```python
import stripe

# Step 1: Calculate proration preview (dry run — no charge yet)
proration_date = int(time.time())  # timestamp of the change

preview = stripe.Invoice.upcoming(
    customer=customer_id,
    subscription=subscription_id,
    subscription_items=[{"id": item_id, "price": new_price_id}],
    subscription_proration_date=proration_date,
)

# Step 2: Surface the preview to the customer
proration_amount = sum(
    item.amount for item in preview.lines.data
    if item.period.start == proration_date
)
# Display proration_amount (in minor units) to the customer for confirmation

# Step 3: Apply only on confirmation (idempotent — include an idempotency key)
stripe.Subscription.modify(
    subscription_id,
    items=[{"id": item_id, "price": new_price_id}],
    proration_behavior="create_prorations",
    proration_date=proration_date,
    idempotency_key=f"proration:{subscription_id}:{proration_date}",
)
```

Post the proration entries to the double-entry ledger: debit the revenue account
for the unused time credit; credit it for the new period charge.

**Do:**
- Always preview first; never apply a proration silently.
- Use the same `proration_date` in the preview and the apply call to get
  consistent amounts.
- Store the preview amount shown to the customer for dispute resolution.

**Don't:**
- Apply a proration in the same API call as the plan change without a preview step.
- Calculate proration manually in floating-point arithmetic — use the PSP's
  proration endpoint (house opinion #1: money is integers in minor units).
- Prorate on a timezone-naive timestamp; always work in UTC.

## Edge cases / when the rule does NOT apply

- Annual plans with a fixed renewal date: proration may be waived by policy
  ("changes take effect at renewal, no proration") — that is a billing policy
  decision, document it explicitly.
- Immediate cancellation with no credit owed: no proration calculation, just
  a cancellation event.

## See also

- [`../agents/billing-subscriptions-engineer.md`](../agents/billing-subscriptions-engineer.md) — owns proration logic
- [`./money-is-integers.md`](./money-is-integers.md) — proration amounts are minor-unit integers
- [`./every-money-operation-is-idempotent.md`](./every-money-operation-is-idempotent.md) — the apply call carries an idempotency key

## Provenance

Codifies the proration workflow from Stripe Billing documentation (preview →
confirm pattern `[verify-at-use]`). Standard subscription billing engineering
practice. Proration math at minor-unit integer precision is implied by house
opinion #1 from `CLAUDE.md` §2.

---

_Last reviewed: 2026-06-05 by `claude`_
