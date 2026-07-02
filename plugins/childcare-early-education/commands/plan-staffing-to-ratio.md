---
description: "Staff each childcare room to the required child:staff ratio and group-size cap by age, hold ratio across the whole day, and read the ratio-driven labor cost per room against its revenue (ratios state-specific, verify-at-use)."
argument-hint: "[rooms by age + enrolled counts + tuition + state]"
---

You are running `/childcare-early-education:plan-staffing-to-ratio`. Use `classroom-ratio-compliance-advisor` + `childcare-center-lead` and the `staffing-to-ratio-scheduling` + `ratios-and-licensing-compliance` skills.

> Advisory, not legal, licensing, or financial advice. Every ratio and group-size number is `[verify-at-use, state-specific]` — confirm against the state licensing regulation. No child PII — work in ages, room configs, and counts.

## Steps
1. Capture each room's age band, enrolled count, tuition, and the state whose rule applies.
2. Look up (and flag `[verify-at-use, state-specific]`) the required child:staff ratio **and** the group-size cap for each age band.
3. Traverse the **staff a room to ratio** tree in `knowledge/childcare-decision-trees.md`: compute ratio-countable teachers needed = ceil(enrolled ÷ ratio), check the group-size cap independently, and confirm coverage holds at open/close/breaks/nap.
4. Model the **whole-teacher step** per room and compare ratio-driven labor cost to room revenue at current enrollment; flag any room just over a boundary.
5. Emit using `templates/ratio-staffing-plan.md` + the Structured Output block, handing the capacity/tuition trade-off to `childcare-center-lead`.
