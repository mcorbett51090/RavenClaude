# Identify and defend the critical path — not every task is equally important

**Status:** Absolute rule
**Domain:** Predictive delivery — schedule management
**Applies to:** `project-management`

---

## Why this exists

Projects that treat every task as equally important to the end date find out late — usually during a steering pack or a sprint review — that the project is behind. The critical path is the longest chain of dependent tasks with zero float; a one-day delay on any critical-path task delays the project end date by one day. Conversely, a five-day delay on a task with ten days of float has zero effect on the end date. Without critical-path analysis, PMs focus attention on the loudest or most visible tasks, not the ones that actually control the outcome.

## How to apply

**Critical path analysis steps (at baseline and on every re-baseline):**

1. **List all schedule activities** with estimated durations (from the WBS).
2. **Identify dependencies** — which activities cannot start until another finishes? Capture Finish-to-Start (FS), Start-to-Start (SS), Finish-to-Finish (FF) relationships as applicable.
3. **Calculate the forward pass** — Earliest Start (ES) and Earliest Finish (EF) for every activity.
4. **Calculate the backward pass** — Latest Start (LS) and Latest Finish (LF), working backward from the required project end date.
5. **Calculate float** — Float = LS − ES (or LF − EF). Activities with Float = 0 are on the critical path.
6. **Highlight the critical path** in the schedule and communicate it to the team.

**Float formula:**
```
Float = Latest Start (LS) − Earliest Start (ES)
      = Latest Finish (LF) − Earliest Finish (EF)
```

**Schedule management rules once the critical path is identified:**

| Situation | Action |
|---|---|
| A critical-path task is delayed | Immediately assess project end-date impact; raise a change request or acceleration option |
| A non-critical task is delayed but within float | Log it; monitor; no immediate end-date impact |
| Float on a non-critical path is being consumed | Flag it as a developing risk — float eroding to zero makes it critical |
| Resource reassignment proposed | Check whether the resource is on a critical-path task before agreeing to the move |

**Critical path in earned value:**
The SPI (Schedule Performance Index = EV ÷ PV) tells you how much work you've completed versus planned — but it doesn't tell you whether the delay is on the critical path. Always pair EV schedule analysis with a critical-path review.

**Do:**
- Re-calculate float whenever the schedule changes significantly (new activity added, dependency changed, a task overruns).
- Communicate the critical path to the whole team, not just the PM — people make different prioritisation decisions when they understand schedule impact.
- Build schedule contingency (buffer) into the baseline for risk events on the critical path specifically.

**Don't:**
- Declare a task "critical" because a stakeholder is impatient about it; critical path is a mathematical property of the network, not a political designation.
- Focus milestone-tracking conversations exclusively on percentage-complete without asking "is this task on the critical path?"
- Accept a resource swap off a critical-path task without a plan to cover the work.

## Edge cases / when the rule does NOT apply

On agile projects, a physical critical path in the PMBOK sense does not exist — the analogous concept is the delivery-blocking dependency or the sprint-critical item. The principle — know which work controls your delivery date and protect it — applies in every method; the tooling differs. On very short projects (< 4 weeks), a formal CPM calculation may be overkill; a simple dependency list identifying the longest chain is sufficient.

## See also
- [`../agents/delivery-lead.md`](../agents/delivery-lead.md) — schedule management and earned value
- [`../skills/project-charter-and-baseline/SKILL.md`](../skills/project-charter-and-baseline/SKILL.md) — baseline construction including critical path

## Provenance

Codifies `delivery-lead`'s schedule management discipline. Grounded in PMBOK 6 §6.6 (Develop Schedule) and the CPM methodology standard in predictive project management.

---

_Last reviewed: 2026-06-05 by `claude`_
