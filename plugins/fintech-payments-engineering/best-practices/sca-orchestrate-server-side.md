# Orchestrate SCA/3DS server-side; never assume the client handles it

**Status:** Absolute rule
**Domain:** Payments / 3DS and SCA
**Applies to:** `fintech-payments-engineering`

---

## Why this exists

Strong Customer Authentication (SCA) under PSD2 (EU/UK) requires additional
cardholder verification for many online transactions. Issuers signal the need
for SCA with a `requires_action` status on the payment intent. A server that
ignores this status and marks the payment as failed — or that delegates the
action step entirely to the client without a fallback — causes unnecessary
decline rates on European cards and failed subscription renewals. The server
must orchestrate the 3DS flow, handle `requires_action` explicitly, and detect
the result from a server-side webhook, not just from a client-side callback.

## How to apply

In the payment flow:

1. **Initiate server-side:** create the payment intent server-side and return the
   `client_secret` to the frontend.
2. **Client handles the action:** the frontend uses the PSP's JS SDK to trigger
   the 3DS challenge if `requires_action`.
3. **Server confirms from webhook:** do NOT rely solely on the client's callback
   to confirm payment — confirm from `payment_intent.succeeded` webhook.

For **subscription renewals** (off-session charges): handle `requires_action`
by sending a re-authentication link to the customer's email:

```python
def handle_payment_intent_requires_action(pi: dict) -> None:
    if pi["next_action"]["type"] == "redirect_to_url":
        # On-session: return the redirect URL to the client
        return {"action_required": True, "url": pi["next_action"]["redirect_to_url"]["url"]}

    elif pi["last_payment_error"] and "authentication_required" in pi["last_payment_error"].get("code", ""):
        # Off-session (subscription renewal): send re-auth email
        customer = db.get_customer(pi["customer"])
        email.send_reauth_required(customer.email, pi["id"])
        # Update subscription to pending_reauth state — do not cancel yet
        subscription = db.get_subscription_by_payment(pi["id"])
        db.update_subscription(subscription.id, status="pending_reauth")
```

**Do:**
- Handle `requires_action` as a normal, expected response, not an error.
- For off-session (subscription renewal) failures with `authentication_required`:
  notify the customer and provide a re-authentication link before dunning.
- Confirm the final payment state from a webhook, not only from the client
  callback.

**Don't:**
- Treat `requires_action` as a final failure — it is an intermediate state.
- Skip the server-side webhook confirmation for SCA-completed payments.
- Attempt to re-charge an off-session card that returned
  `authentication_required` without a new cardholder authentication step.

## Edge cases / when the rule does NOT apply

- US-only card payments: SCA is not mandated by US regulation; 3DS is optional
  but still supported. The flow is identical; it just triggers less often.

## See also

- [`../agents/payments-integration-engineer.md`](../agents/payments-integration-engineer.md) — owns 3DS/SCA integration
- [`./handle-3ds-sca-and-declines.md`](./handle-3ds-sca-and-declines.md) — the upstream rule on handling 3DS in the charge flow
- [`./dunning-without-churning.md`](./dunning-without-churning.md) — `authentication_required` off-session is a specific dunning path

## Provenance

Codifies the SCA/3DS orchestration requirements from PSD2 (EU/UK) and PSP
documentation. Stripe 3D Secure 2 documentation + payment intent lifecycle
`[verify-at-use]`. The off-session re-authentication flow is the PSP-recommended
approach for subscription SCA failures.

---

_Last reviewed: 2026-06-05 by `claude`_
