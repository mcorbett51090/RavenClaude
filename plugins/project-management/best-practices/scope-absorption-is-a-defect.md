# Scope Absorption Without a Change Request Is a Defect

**Status:** Absolute rule
**Domain:** Project Management — Predictive / Change Control
**Applies to:** `project-management`

---

## Why this exists

Every piece of work absorbed into a baselined project without a change request is a silent scope increase: it consumes schedule, budget, and team capacity while the baseline continues to report the original plan. The earned-value picture becomes meaningless, the schedule slips without an authorized cause, and the sponsor makes decisions on a plan that no longer describes reality. Scope creep — work absorbed without change control — is the leading cause of the "how did we end up six weeks late with no warning?" failure mode on predictive projects.

## How to apply

**The test for whether change control applies:**
> Any change that would alter the scope baseline (WBS), schedule baseline (critical path / milestones), or cost baseline (BAC) requires a Change Request before the work begins.

**Change request minimum content:**

| Field | Content |
|---|---|
| CR ID | Sequential number |
| Requester | Named person + date |
| Description | What is being added/changed/removed |
| Scope impact | Which WBS elements are affected |
| Schedule impact | Days of delay to the critical path, if any |
| Cost impact | Estimated additional cost (hours × rate + material) |
| Risk impact | New or changed risks introduced by the change |
| Disposition | Approve / Reject / Defer — by whom, by when |
| Baseline update | If approved: which baselines are revised and the new values |

**Integrated Change Control process (PMBOK):**
1. Change identified → CR drafted.
2. CR reviewed by the Change Control Board (or sponsor on smaller projects).
3. Disposition documented (approve/reject/defer) with the reason.
4. If approved: baselines updated, team informed, status adjusted.
5. If rejected: reason documented; requester notified.

**Do:**
- Socialize the change control process with all stakeholders at project kickoff.
- Provide a lightweight CR template for small projects — the process must be proportionate to the project scale.
- Log all CRs (including rejected ones) in the project record; they are audit material.

**Don't:**
- Start work on a requested change before the CR is dispositioned.
- "Just add it this sprint" as a team shortcut for a baselined predictive project.
- Remove change control for a "small" change without checking its schedule impact on dependent tasks.

## Edge cases / when the rule does NOT apply

- **Agile track (scrum-master)**: the equivalent is visible backlog re-prioritization — a new story is added to the backlog and sized; if it displaces sprint capacity, the sprint backlog changes visibly and the Product Owner makes the trade-off. There is no formal CR, but the absorption must be *visible*, not silent.
- **Urgent defect corrections** that are clearly within scope (fixing what was agreed, not adding what was not): these are not scope changes and do not require a CR.

## See also

- [`../agents/delivery-lead.md`](../agents/delivery-lead.md) — owns baseline management and change control for predictive projects
- [`./baseline-before-you-change-control.md`](./baseline-before-you-change-control.md) — the prerequisite: a baseline must exist before change control can function

## Provenance

Codifies the anti-pattern "Scope changes absorbed with no change request + baseline-impact analysis" from `CLAUDE.md` §4. Integrated Change Control from PMBOK 6th/7th edition, §4.6. _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
