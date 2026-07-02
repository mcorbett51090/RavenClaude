---
name: booking-and-no-show-control
description: "Control the perishable-inventory leak: design a no-show / late-cancel policy with deposits or card-on-file, a rebook-at-checkout habit, a reminder cadence, and a waitlist that backfills cancellations. Prevent the no-show first; enforce the policy second."
---

# Booking & No-Show Control

A booked slot that no-shows is inventory you cannot resell tomorrow. This skill is the front desk's defense of the calendar: prevent the no-show, capture the rebook, and turn a cancellation into a fill.

## The loop

1. **Set the no-show / late-cancel policy.** Define the notice window, the deposit or card-on-file rule, the fee, and the enforcement + exception path. Size it to the practice's actual no-show rate — a low rate needs a lighter touch than a chronic one. Traverse the no-show-policy tree in [`../../knowledge/salon-spa-decision-trees.md`](../../knowledge/salon-spa-decision-trees.md). Treat benchmark no-show rates as `[verify-at-use]`.
2. **Prevent with reminders.** A confirming reminder cadence (text/email with one-tap reschedule) stops more no-shows than any fee recovers. The easy path must be the confirming path.
3. **Rebook at checkout.** Book the next visit before the client leaves the chair, at the recommended interval. Track rebooking rate per provider — see [`../retail-attach-and-service-mix/SKILL.md`](../retail-attach-and-service-mix/SKILL.md) for the checkout moment it shares.
4. **Backfill from the waitlist.** Every late cancel triggers a waitlist offer / auto-fill so a lost slot becomes a sale.

## Metrics

| Metric | Reads | Note |
|---|---|---|
| No-show rate | no-shows / booked appointments | The leak you're closing; `[verify-at-use]` on any norm |
| Late-cancel rate | cancels inside the notice window | Feeds the deposit-policy decision |
| Rebooking rate at checkout | rebooked / checked-out | The leading indicator of a full future book |
| Waitlist fill rate | filled cancellations / total cancellations | Turns lost inventory into revenue |
| Confirmation rate | confirmed / reminded | Reminder-cadence effectiveness |

## Anti-patterns

- A stated policy that is never enforced — trains clients to ignore it.
- A deposit rule with no easy reschedule path — punishes the loyal, not the flaky.
- "Call us to rebook" instead of booking it at the chair.
- Treating cancellations as gone rather than waitlist triggers.

## See also

- [`../compensation-models-commission-vs-booth-rent/SKILL.md`](../compensation-models-commission-vs-booth-rent/SKILL.md) — a no-show costs the provider a resellable hour too.
- Best practices: [`../../best-practices/a-no-show-is-inventory-you-cant-resell.md`](../../best-practices/a-no-show-is-inventory-you-cant-resell.md), [`../../best-practices/rebook-before-they-leave-the-chair.md`](../../best-practices/rebook-before-they-leave-the-chair.md).
- Command: [`/set-noshow-policy`](../../commands/set-noshow-policy.md).
