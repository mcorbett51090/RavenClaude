---
description: "Rebuild a class grid on real demand: read fill vs per-class break-even by slot and class type, cut/merge/re-time on the data, set a no-show/waitlist policy, and pick the instructor pay model — with the fill and margin implications named (verify-at-use)."
argument-hint: "[class list + times + capacity + fill by slot + instructor roster/pay + no-show rate]"
---

You are running `/fitness-studio-gym-operations:optimize-class-grid`. Use `class-schedule-coach-ops` + the `class-schedule-and-instructor-utilization` skill.

> Advisory, not legal/financial advice. Fill targets and instructor-pay norms are `[verify-at-use]`. No member PII — work in slot-level fill and roster data, never named members.

## Steps
1. Capture the grid: classes, times, capacity, **attended** fill by slot and class type, instructor roster and current pay model, no-show rate.
2. Compute the **break-even headcount** per slot: (instructor pay + allocated room cost) / contribution per attendee.
3. Traverse the **schedule the class grid on fill** tree in `knowledge/fitness-studio-decision-trees.md` — cut/merge slots below break-even, re-time toward waitlists, add capacity only where a waitlist proves demand.
4. Traverse the **instructor pay model** tree to match flat / per-head / base+per-head to the grid's fill economics; set a **no-show/late-cancel + auto-promote waitlist** policy to reclaim held seats.
5. Name the fill and margin movement expected, each owner, and flag every benchmark `[verify-at-use]`. Emit against `templates/studio-kpi-dashboard.md` (grid + instructor sections) + the Structured Output block. Escalate employment-classification/comp-law questions to `people-operations-hr`.
