# Decompose the WBS to work packages — not further

**Status:** Absolute rule
**Domain:** Predictive delivery — scope management
**Applies to:** `project-management`

---

## Why this exists

The Work Breakdown Structure (WBS) is a scope decomposition, not a task list. Over-decomposing the WBS to activity level produces a structure that must be maintained like a Gantt but is neither the schedule nor the RAID register — it belongs nowhere and becomes a PM artefact that only the PM reads. The work package is the correct terminal node: it is small enough to be owned by one person, large enough to be a meaningful deliverable or outcome, and big enough that it can be estimated, assigned, and measured in earned value without micromanagement. The activity-level schedule (the Gantt) is derived from the WBS — it is not the WBS.

## How to apply

**Work package definition — all four criteria must hold:**

| Criterion | Test |
|---|---|
| Single owner | One named person is accountable — not "the team," not "TBD" |
| Measurable output | Completion can be verified objectively (a document, a build, a test result — not "progress") |
| Estimable | Effort and duration can be estimated with reasonable confidence |
| Sized correctly | 1–10 working days of effort at the lowest level; larger at higher levels |

**The decomposition test:**

```
Deliverable → Work packages → [STOP HERE in the WBS]
                            ↓
                       Activities (these go in the schedule/Gantt, not the WBS)
```

**Example (correct):**

```
1.0 System integration
    1.1 Integration design document  [work package — 5 days, owner: Solution Architect]
    1.2 UAT test pack prepared       [work package — 8 days, owner: QA Lead]
    1.3 Integration sign-off         [work package — 2 days, owner: Business Analyst]
```

**Example (over-decomposed — wrong in the WBS):**

```
1.0 System integration
    1.1 Draft integration design
    1.2 Review integration design
    1.3 Revise integration design
    1.4 Circulate for approval ...
```

The revision/review activities belong in the schedule or in the task board, not the WBS.

**Earned value alignment:**
Work packages are the units at which planned value (PV) is assigned and earned value (EV) is measured. An over-decomposed WBS creates spurious EV precision — the schedule variance of an individual review step is not meaningful input to the forecast.

**Do:**
- Assign a single named owner to every work package at WBS decomposition time.
- Use a WBS dictionary entry (brief description + acceptance criteria + responsible person) for every work package if the project is large enough to warrant it.
- Treat the WBS as a scope document — the schedule (with activities and durations) is a separate deliverable that derives from it.

**Don't:**
- Continue decomposing past the point where a single named person can own the output.
- Include activities, meetings, reviews, or approval steps as WBS nodes — those go in the schedule.
- Build the WBS in a task-management tool that forces you to the activity level; use the WBS for scope and use the schedule for activities.

## Edge cases / when the rule does NOT apply

For small projects (< 3 months, single team), the WBS and the schedule can collapse — a flat list of work packages with durations is sufficient. The single-owner and verifiable-output rules still apply even if the two-level hierarchy is unnecessary. Agile projects do not use a WBS; they use a product backlog decomposed to user stories — the single-owner and acceptance-criteria disciplines still apply at the story level.

## See also
- [`../agents/delivery-lead.md`](../agents/delivery-lead.md) — predictive scope and WBS methodology
- [`../skills/project-charter-and-baseline/SKILL.md`](../skills/project-charter-and-baseline/SKILL.md) — WBS construction through to baseline

## Provenance

Codifies `delivery-lead`'s scope methodology. Grounded in PMBOK 6 §5.4 (Create WBS) and the PMI WBS Practice Standard — work package as terminal WBS node is the defined standard.

---

_Last reviewed: 2026-06-05 by `claude`_
