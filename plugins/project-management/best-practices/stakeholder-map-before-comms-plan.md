# Build the Stakeholder Map Before the Comms Plan

**Status:** Pattern
**Domain:** Project Management — Stakeholder / Communications
**Applies to:** `project-management`

---

## Why this exists

A communications plan written before the stakeholder map sends the same depth of information to everyone. An executive who wants a one-page RAG summary receives a 12-page status report; a technical workstream lead who needs risk details gets the executive summary. Both are disserved, and the team spends time producing content that no one reads. The power/interest grid forces a deliberate categorization of each stakeholder's influence and need *before* any communication artifact is designed.

## How to apply

**Step 1 — Build the stakeholder register:**

| Stakeholder | Role | Power (H/M/L) | Interest (H/M/L) | Stance (Champion/Neutral/Resistant) | Preferred channel | Preferred cadence |
|---|---|---|---|---|---|---|
| … | … | … | … | … | … | … |

**Step 2 — Map to the power/interest grid:**

```
High power    | Manage closely    | Keep satisfied
              | (engage deeply,   | (light-touch but
              | decision-makers)  | politically important)
--------------+-----------+-------
Low power     | Keep informed     | Monitor only
              | (operational      | (minimal effort)
              | stakeholders)     |
              Low interest        High interest
```

**Step 3 — Design communication artifacts by quadrant:**

| Quadrant | Artifact | Depth | Cadence |
|---|---|---|---|
| High power / High interest | Steering pack + briefing | Decision-grade, narrative-first | Weekly to fortnightly |
| High power / Low interest | 1-page executive summary | Headline + RAG + ask | Monthly or milestone-driven |
| Low power / High interest | Detailed status + risk log | Full | Weekly |
| Low power / Low interest | Distribution copy | Brief FYI | Per milestone |

**Do:**
- Refresh the map at each project phase — stakeholder power and interest shift as scope matures.
- Identify any Resistant/High-Power stakeholders early; engagement strategy is a project risk if not managed.
- Flag the stakeholder map as a controlled document; changes route through the comms lead.

**Don't:**
- Send all stakeholders the same status report regardless of quadrant.
- Build the comms plan before the stakeholder register is agreed with the sponsor.
- Treat the map as a one-time Define-phase artifact — reassess it at each phase gate.

## Edge cases / when the rule does NOT apply

- **Internal team projects with no external stakeholders**: the power/interest grid degenerates; a simple RACI matrix suffices.
- **Crisis communications**: the plan must be executed immediately; the map is implied. Complete the formal map in the post-incident retrospective.

## See also

- [`../agents/stakeholder-comms-lead.md`](../agents/stakeholder-comms-lead.md) — the agent that builds and owns the stakeholder register and comms plan
- [`./status-leads-with-narrative-and-matches-the-numbers.md`](./status-leads-with-narrative-and-matches-the-numbers.md) — the companion rule that status artifacts are tailored by audience

## Provenance

Codifies the `stakeholder-comms-lead` agent's operating model from `CLAUDE.md` §1. Power/interest grid from PMBOK 6th/7th edition (PMI, Stakeholder Management knowledge area) and Mendelow (1981). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
