# Model the subscription as a state machine, not a boolean active/inactive

**Status:** Absolute rule
**Domain:** Subscription billing / state management
**Applies to:** `fintech-payments-engineering`

---

## Why this exists

A subscription has more than two states, and treating it as a boolean (active/
not-active) produces billing bugs at every boundary. A subscriber whose card
failed is not the same as a subscriber who cancelled intentionally: one needs a
dunning retry cycle and access preservation during the grace period; the other
needs immediate access revocation and offboarding. A subscriber in a trial is
not the same as a subscriber in an active paid plan. Collapsing these into a
boolean makes every edge case a special case — which means each one gets
discovered in production.

## How to apply

Model the subscription lifecycle as an explicit finite state machine with
defined transitions:

| State | Entry condition | Exit conditions |
|---|---|---|
| `trialing` | New subscriber, trial flag enabled | Trial ends → `active`; cancelled during trial → `canceled` |
| `active` | First successful payment; trial ends | Payment fails → `past_due`; cancel → `pending_cancel` |
| `past_due` | Payment fails during active | Payment recovered → `active`; dunning exhausted → `canceled` |
| `pending_cancel` | Customer cancels; period not yet ended | Period ends → `canceled` |
| `canceled` | Dunning exhausted; period ends after cancel | Re-subscribe → new subscription |
| `paused` | Customer-initiated pause (where supported) | Resume date → `active` |

Drive the state exclusively from verified webhook events (not PSP sync calls):

```python
VALID_TRANSITIONS = {
    "trialing":       {"trial_end": "active", "cancel": "canceled"},
    "active":         {"payment_failed": "past_due", "cancel": "pending_cancel"},
    "past_due":       {"payment_recovered": "active", "dunning_exhausted": "canceled"},
    "pending_cancel": {"period_ended": "canceled"},
    "canceled":       {},   # terminal — re-subscribe creates a new subscription
}

def transition(subscription, event_type: str) -> None:
    current = subscription.status
    next_state = VALID_TRANSITIONS.get(current, {}).get(event_type)
    if next_state is None:
        raise InvalidTransition(f"{current} --[{event_type}]--> ? (no valid transition)")
    subscription.status = next_state
    ledger.post_state_change(subscription, event_type, next_state)
```

**Do:**
- Define all states and transitions before writing any billing code.
- Drive transitions from verified webhook events only.
- Post a ledger entry and an audit log on every state transition.

**Don't:**
- Use a boolean `is_active` field — it collapses states that require different
  treatment.
- Allow code paths that set `status` directly without going through the
  transition function (bypasses validation and logging).
- Derive subscription access from anything other than the current state.

## Edge cases / when the rule does NOT apply

- One-time purchases (no recurring billing): no subscription state machine needed.

## See also

- [`../agents/billing-subscriptions-engineer.md`](../agents/billing-subscriptions-engineer.md) — owns subscription state management
- [`./model-the-charge-as-a-state-machine.md`](./model-the-charge-as-a-state-machine.md) — the charge-level state machine this builds on
- [`./double-entry-ledger-is-source-of-truth.md`](./double-entry-ledger-is-source-of-truth.md) — every state transition posts to the ledger

## Provenance

Codifies the subscription billing state machine discipline. Standard practice
in subscription billing engineering (Stripe Billing documentation `[verify-at-use]`,
recurly/chargebee equivalent patterns). Extends the charge-state-machine house
opinion to the subscription level.

---

_Last reviewed: 2026-06-05 by `claude`_
