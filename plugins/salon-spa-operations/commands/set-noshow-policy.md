---
description: "Design a no-show / late-cancel policy sized to the shop's actual no-show rate — notice window, deposit or card-on-file, fee, enforcement, and the reminder + rebooking loop that prevents most no-shows in the first place (verify-at-use on norms)."
argument-hint: "[current no-show rate + booking channel + whether card-on-file is possible]"
---

You are running `/salon-spa-operations:set-noshow-policy`. Use `front-desk-booking-manager` + the `booking-and-no-show-control` skill.

> Operations decision-support, not legal advice. Deposit / card-on-file rules carry payment-processor and consumer-protection implications — flag them `[verify-at-use]` and route to a professional and the processor's terms. No client PII — work in rates and policies, never a client record.

## Steps
1. Capture the shop's **measured** no-show and late-cancel rate, booking channel, service value/length mix, and whether payment-on-file at booking is possible.
2. Traverse the **no-show policy & deposit** tree in `knowledge/salon-spa-decision-trees.md`.
3. Set the prevention layer first — reminder cadence with one-tap reschedule — then the enforcement layer: notice window, deposit / card-on-file sized to the rate, a fair fee, consistent enforcement, and an exception path. Wire the waitlist auto-fill.
4. Name every payment/consumer-protection specific as `[verify-at-use]` and route it to a professional.
5. Emit using the calendar section of `templates/salon-kpi-dashboard.md` + the Structured Output block, with a rebooking target (see `best-practices/rebook-before-they-leave-the-chair.md`).
