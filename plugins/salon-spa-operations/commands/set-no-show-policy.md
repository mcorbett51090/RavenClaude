---
description: "Set the salon/spa no-show and late-cancel policy: the cancellation window, the deposit or card-on-file, the fee, the reminder cadence, and the client-facing wording."
argument-hint: "[current no-show rate + booking system + services + risk tolerance]"
---

You are running `/salon-spa-operations:set-no-show-policy`. Use `booking-and-retention-analyst` + the `set-no-show-and-deposit-policy` skill.

## Steps
1. Traverse the deposit-policy tree in `knowledge/salon-spa-operations-decision-trees.md` to match the mechanism to service cost + chair-time.
2. Set the cancellation window (longer for color/packages).
3. Capture security — deposit at booking or card-on-file the system can actually charge; if the system can't, fix that first.
4. Set the fee equal to the unresellable chair-time, and add a reminder cadence.
5. Write the client-facing wording, shown before booking — never at checkout.
6. Emit using `templates/no-show-deposit-policy.md` + the Structured Output block.
