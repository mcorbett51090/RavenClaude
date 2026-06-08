---
description: "Size a contact center queue for a target service level using Erlang C, check occupancy, apply shrinkage, and produce a shrinkage-adjusted FTE count with a staffing justification."
argument-hint: "[channel, volume, AHT, SLA target — e.g. 'chat, 200 contacts/hr, 4-min AHT, 80/20 SLA, 20% shrinkage']"
---

You are running `/customer-support-cx-operations:design-support-queue`. Use the
`contact-center-workforce-analyst` discipline and the `workforce-and-queue-design` skill.

## Steps

1. Confirm the Erlang C inputs: channel (voice/chat/email), contact volume per interval (15- or
   30-minute bucket), AHT in seconds, target service level (X% within Y seconds), and operating
   hours per day.

2. Run Erlang C to find agents-needed at the target service level. Use
   `scripts/cx_calc.py erlang-c` (or equivalent calculation). Verify that occupancy at the model's
   agent count is within the channel-appropriate range (voice: 80–85%; chat: 85–90%).

3. If occupancy exceeds the target ceiling, add agents until occupancy is within range — report
   both the SLA-floor count and the occupancy-safe count.

4. Apply shrinkage: collect the shrinkage budget (trained + unplanned components), compute
   shrinkage-adjusted FTE using `scripts/cx_calc.py shrinkage-fte`. Document the shrinkage
   rate breakdown.

5. Check the deflection-first option: traverse the `Deflect-vs-staff` tree in
   `knowledge/cx-ops-decision-trees.md`. If a deflection investment would reduce inbound volume
   meaningfully, model the staffing count at the post-deflection volume and report both scenarios.

6. Fill `templates/sla-and-escalation-matrix.md` with the SLA commitment and its model basis.
   Emit the Structured Output block with: raw agent count, occupancy, shrinkage rate, FTE,
   deflection-first option (if applicable), and handoffs to `cx-ops-lead` (channel model) and
   `knowledge-and-deflection-strategist` (if deflection is the better lever).
