---
description: "Design or redesign a field-service dispatch board — priority-queue rules by SLA tier, skill-match routing, geographic density optimization, emergency buffer, and day-of escalation ladder."
argument-hint: "[context, e.g. '3 SLA tiers, 12 techs, HVAC commercial, 4-hour emergency SLA']"
---

You are running `/field-service-management:design-dispatch-board`. Use the
`dispatch-and-scheduling-engineer` discipline and the `dispatch-and-scheduling` skill.

## Steps

1. Confirm the SLA tier structure with the user (or read from context). Map each tier to a
   priority level (P0–P4) using the schedule-priority tree in
   `knowledge/fsm-decision-trees.md`.

2. Build the skill-match matrix: for each technician, list their certifications, equipment
   authorizations, and the SLA tiers they are authorized to serve. This is the hard-constraint
   filter — a skill mismatch is not a soft preference.

3. Analyze the current territory layout for geographic density (jobs per drive-hour using
   `scripts/fsm_calc.py` `route_density()`). Flag any territory where average drive time per job
   exceeds 35 minutes.

4. Design the daily time-block allocation: planned PM window (morning batch), reactive buffer
   (rolling), emergency reserve (always-on), and end-of-day close. Size each block from the
   user's PM-to-reactive job ratio.

5. Write the emergency escalation ladder: in-territory → adjacent-territory (with overtime
   trigger) → approved subcontractor → SLA-miss notification SOP.

6. Fill `templates/dispatch-board.md` with the complete dispatch board design.

7. Emit the Structured Output block with handoffs: `fsm-ops-lead` if SLA tier definitions need
   revision; `parts-and-inventory-analyst` for pre-dispatch parts-readiness integration;
   `technician-productivity-analyst` to baseline utilization after the new board is live.
