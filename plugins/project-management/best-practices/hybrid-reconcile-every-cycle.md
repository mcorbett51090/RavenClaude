# On a Hybrid Project, Reconcile the Outer Baseline Against Inner Velocity Every Cycle

**Status:** Absolute rule
**Domain:** Project Management — Hybrid delivery
**Applies to:** `project-management`

---

## Why this exists

A hybrid project has a predictive outer layer (baseline, change control, earned value, milestone governance) and agile inner sprints. The failure mode unique to hybrid is *divergence without acknowledgment*: the sprint team re-prioritizes the backlog each sprint (correct agile behavior), while the outer baseline continues to report the original milestone plan (correct predictive behavior) — but the two stop reflecting each other. The sponsor sees "on track" in the steering pack while the backlog has quietly shifted; the discrepancy surfaces only when the milestone is missed. Reconciliation every sprint prevents the gap from compounding.

## How to apply

**Reconciliation checklist (end of every sprint):**

- [ ] **Burn-up vs baseline**: plot actual story-points-delivered to date against the plan-of-record delivery curve. Is the team on the burn-up line?
- [ ] **Scope delta**: were any stories added or removed from the release backlog this sprint? Do they affect the milestone scope commitment?
- [ ] **Milestone forecast**: given current velocity, recalculate the predicted completion date. Does it still land within the baselined milestone window?
- [ ] **Change request trigger**: if the forecast date slips past the milestone date, or if scope was added without a corresponding time extension, a Change Request is required before the next sprint starts.
- [ ] **Steering pack update**: the reconciliation result feeds the next stakeholder status update (RAG, narrative, EAC).

**Reconciliation artifact (lightweight):**

```
Sprint [N] reconciliation — [project name] — [date]
Delivered to date:   [X points / X stories]
Planned to date:     [X points / X stories]
Variance:            [±X points — ahead/behind]
Backlog remaining:   [X points]
Forecast completion: [YYYY-MM-DD]  (was: [original baseline date])
Scope delta this sprint: [added/removed items with point values]
Change request triggered: [YES (CR-XXX raised) / NO]
RAG:                 [Green/Amber/Red]  Narrative: [1 sentence]
```

**Do:**
- Run the reconciliation with both the delivery-lead and scrum-master present — it requires both the outer and inner view.
- Use the same velocity window (3–5 sprint average) for the forecast, not the most optimistic recent sprint.
- Treat a widening divergence (> 2 sprints of consecutive under-delivery) as an Amber risk trigger.

**Don't:**
- Let the outer baseline and inner backlog drift for more than one sprint without a documented reconciliation.
- Rebaseline the outer milestone silently — it requires a Change Request even on a hybrid project.
- Substitute the burn-up chart for the steering-pack narrative; sponsors need the decision-grade interpretation, not just the chart.

## Edge cases / when the rule does NOT apply

- **Discovery/Alpha phase**: if the outer baseline was deliberately set as a horizon (not a commitment), reconciliation is about learning and scope refinement, not milestone defense. State this explicitly in the charter.
- **Single-sprint project**: there is no outer baseline; a pure sprint plan suffices.

## See also

- [`../agents/delivery-lead.md`](../agents/delivery-lead.md) — owns the outer baseline and change control
- [`../agents/scrum-master.md`](../agents/scrum-master.md) — owns the inner sprint cadence and velocity
- [`./baseline-before-you-change-control.md`](./baseline-before-you-change-control.md) — the outer baseline the reconciliation protects

## Provenance

Codifies the hybrid collaboration model from `CLAUDE.md` §2 ("Hybrid → delivery-lead + scrum-master collaborate; reconcile each cycle"). Hybrid reconciliation practice from PMBOK 7 (development approach + tailoring). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
