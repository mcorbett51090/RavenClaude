# The Sprint Goal Is a Single Business Objective, Not a Task List

**Status:** Pattern
**Domain:** Project Management — Agile / Scrum
**Applies to:** `project-management`

---

## Why this exists

A sprint "goal" that reads "complete user stories 42, 43, 44, and fix bug 117" is a task list, not a goal. It offers no basis for mid-sprint trade-offs, no way to measure whether the sprint succeeded as a unit, and no way to communicate the sprint's value to stakeholders. When a sprint goal is absent or is a task list, every impediment requires escalation because there is no principle with which the team can evaluate alternative paths. A single, well-formed sprint goal gives the team the authority to adapt within the sprint while keeping the coherent objective.

## How to apply

**Sprint goal formula (Scrum Guide 2020):**
> A sprint goal is a single objective for the Sprint that gives the Scrum Team flexibility regarding the exact work needed to achieve it.

**Drafting checklist:**

- [ ] One sentence; one objective.
- [ ] States the *business outcome*, not the implementation method ("users can upload a profile photo" rather than "implement S3 upload").
- [ ] Measurable: a stakeholder can observe whether the goal was achieved at the Sprint Review.
- [ ] Sufficiently narrow that the team can commit to it within capacity.
- [ ] Agreed by the whole team before sprint planning closes.

**Well-formed examples:**

| Not a goal | Goal |
|---|---|
| "Complete 5 stories from the backlog" | "A buyer can place an order without leaving the catalog page" |
| "Fix the reported bugs and add logging" | "The checkout errors from last sprint are resolved and observable in production logs" |

**What the sprint goal enables:**
- Mid-sprint impediment: the team can ask "does this path still achieve the goal?" rather than escalating every blocker.
- Sprint Review: stakeholders evaluate the *outcome*, not the story count.
- Incomplete sprint: the team and PO can assess which stories serve the goal and which can be dropped without voiding the sprint.

**Do:**
- Craft the sprint goal during backlog refinement (before planning), not at the end of planning when time is running out.
- Make it visible on the team board for the entire sprint.
- Distinguish the sprint goal from the sprint backlog — the backlog is the *how*, the goal is the *what and why*.

**Don't:**
- Write a compound goal ("users can upload photos AND the admin can view audit logs") — that is two sprints.
- Change the sprint goal mid-sprint (that is a sprint cancellation trigger, not a quick edit).
- Accept a sprint goal that cannot be verified at the Sprint Review.

## Edge cases / when the rule does NOT apply

- **Hardening / stabilization sprints**: the goal may be operational ("all P1 bugs from the release are resolved and verified in staging") — a task-list goal is appropriate when the sprint is explicitly scoped to a list of defects. This should be the exception, not the norm.
- **First sprint of a brand-new product with no prior backlog**: the goal may be more exploratory ("we know whether the core technical spike is feasible") — acceptable once, not as a recurring pattern.

## See also

- [`../agents/scrum-master.md`](../agents/scrum-master.md) — facilitates sprint planning and owns the goal-drafting process
- [`./capacity-before-commitment-agile.md`](./capacity-before-commitment-agile.md) — the sprint goal must be achievable within the capacity-sized commitment

## Provenance

Codifies house opinion #8 ("Empiricism over theater — ceremonies exist to drive decisions") from `CLAUDE.md` §3. Sprint Goal definition and guidance from the Scrum Guide 2020 (Schwaber & Sutherland). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
