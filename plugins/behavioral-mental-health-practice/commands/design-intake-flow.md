---
description: "Design or audit the end-to-end intake and access workflow for an outpatient behavioral health practice — from first inquiry through first appointment — including waitlist management, no-show policy, and insurance verification."
argument-hint: "[context, e.g. 'solo practice, 3 therapists, 25% no-show rate, no current waitlist protocol']"
---

You are running `/behavioral-mental-health-practice:design-intake-flow`. Use the
`intake-and-scheduling-analyst` discipline and the `intake-and-access` skill.

## Steps

1. Gather or confirm context: practice size (providers, modalities), current no-show rate (if known),
   current intake workflow description (if any), and payer mix (to identify auth-at-intake requirements).

2. Map the current workflow (or design from scratch): inquiry → screening → insurance verification
   → scheduling → intake-packet delivery → first appointment. Identify drop-off points.

3. Design the insurance verification step: confirm it occurs before the first scheduled appointment.
   Flag any payer types that require prior authorization before session 1 (escalate auth mechanics
   to `behavioral-billing-compliance-advisor` if needed).

4. Build the no-show policy: cancellation window, fee structure (if applicable and payer-compliant),
   three-strike protocol, same-day fill protocol from the waitlist. Use `scripts/bh_calc.py
   no-show-rate` to calculate the current rate and model a 5-point improvement.

5. Design the waitlist protocol: active vs. passive waitlist, urgency re-screen cadence (every 2
   weeks), referral-out threshold (4–6 weeks for non-urgent), fill protocol.

6. Produce the intake-workflow SOP with: step-by-step flow, responsible roles, EHR documentation
   standards at each step, and an intake-packet checklist (reference `templates/intake-packet.md`).

7. Emit the Structured Output block with handoffs: `behavioral-billing-compliance-advisor` for
   authorization requirements; `practice-ops-lead` for capacity and slot design implications.
