---
name: design-dunning-and-recovery
description: "Design and automate failed-payment recovery (dunning) — retry schedule, smart/adaptive retries, grace period, customer comms sequence, and entitlement-downgrade policy — trading recovered revenue against churn of good customers. Use for involuntary-churn reduction."
---

# Skill: Design Dunning and Recovery

Most subscription churn is **involuntary** — a card expired or a charge failed, not a decision to leave. Dunning recovers that revenue, but a clumsy sequence churns good customers and floods support. This skill designs the retry + comms + entitlement policy as one system with an explicit revenue-vs-churn tradeoff.

## When to use

- Reducing involuntary churn / recovering failed renewals.
- Deciding when (and whether) to downgrade or cut off access after a failed payment.
- Auditing an existing dunning flow that over- or under-retries.

## Steps

1. **Classify the failure.** Hard declines (do-not-honor, lost/stolen, closed account) should not be retried like soft declines (insufficient funds, temporary). Retrying a hard decline just burns goodwill and processor fees.
2. **Set the retry schedule.** Choose retry timing and count; prefer smart/adaptive retries (provider-optimized timing) over a fixed cadence where available. Align retries to when funds are likely present (e.g. paydays), not fixed hour-after-hour.
3. **Define the grace period and entitlement policy.** Decide how long access continues during dunning and exactly when entitlements downgrade or suspend. This flows through the entitlement layer — make it deliberate, not a side effect.
4. **Design the comms sequence.** Pre-dunning (card-expiring reminders), in-dunning (payment-failed → update-card, escalating), and recovery/win-back. Keep the tone helpful; give a one-click update-payment path.
5. **Instrument recovery.** Track recovery rate, days-to-recover, involuntary vs voluntary churn, and comms fatigue (unsubscribes/complaints). The tradeoff is only manageable if measured.
6. **Automate to spec.** The [`billing-implementation-engineer`](../../agents/billing-implementation-engineer.md) wires it to provider dunning/retry features + your comms; the policy above is the spec. Card-update comms respect email deliverability (seam to `email-engineering`).

## Anti-patterns

- Retrying hard declines like soft declines.
- Fixed, aggressive retry cadence that burns fees and goodwill.
- Cutting off access instantly on first failure (churns recoverable customers) — or never cutting off (revenue leak).
- Dunning emails with no one-click card-update path.
- No recovery-rate / churn instrumentation, so the policy can't be tuned.

## Output

A dunning policy: failure classification → retry schedule (smart where available) → grace + entitlement-downgrade rules → comms sequence → recovery instrumentation. The architect owns the tradeoff; the engineer automates it.
