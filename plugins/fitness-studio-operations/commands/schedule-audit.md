---
name: schedule-audit
description: "Audit the class schedule and staff ops: build a per-slot utilization grid with prune/grow calls, recommend an instructor pay model worked at low/high attendance, flag 1099-vs-W2, and set a no-show policy."
argument-hint: "[schedule with attendance + capacity, instructor roster, current pay terms]"
---

You are running `/fitness-studio-operations:schedule-audit`. Use `class-and-instructor-ops-lead` + the `optimize-class-schedule` and `design-instructor-pay-model` skills.

## Steps
1. Build a per-slot utilization grid (attendance / capacity) with instructor cost-per-class and margin-per-class.
2. Traverse the capacity tree in `knowledge/fitness-studio-operations-decision-trees.md`; make prune/hold/grow/move calls against the target fill band; protect anchor classes (clear cuts with member-retention-analyst).
3. Traverse the pay-model tree; recommend hourly / per-head / rev-share (+ floor), worked at low and high attendance.
4. Flag the 1099-vs-W2 question (control + relationship) — defer the binding call to people-operations-hr + counsel.
5. Set a no-show/late-cancel policy: window + penalty + enforcement mechanism.
6. Emit using `templates/class-schedule-and-pay-plan.md` + the Structured Output block.
