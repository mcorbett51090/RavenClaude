# Triage an Issue Before Escalating It

**Status:** Pattern
**Domain:** Project Management — Risk / RAID / Issue Management
**Applies to:** `project-management`

---

## Why this exists

An issue escalated immediately upon discovery, without first characterizing its impact and urgency, wastes steering-committee time and trains sponsors to expect noise rather than signal. Conversely, an issue that sits in the log without a triage decision — "someone will look at it" — festers into an unmanaged blocker. Structured triage is the decision between "we can resolve this at team level," "we need sponsor awareness," and "this is an escalation that requires a decision today." The triage discipline converts issues from a venting list into a managed queue.

## How to apply

**Issue triage criteria:**

| Dimension | Questions to answer |
|---|---|
| **Impact** | What project objective (scope/schedule/cost/quality) does this affect, and by how much? |
| **Urgency** | By when does a decision need to be made to prevent the impact from growing? |
| **Authority** | Can the project team resolve this without additional authority, budget, or decision-maker involvement? |
| **Options** | Are there 2–3 resolution paths and, if so, which is recommended? |

**Triage disposition matrix:**

| Impact | Authority to resolve | Disposition |
|---|---|---|
| Low | Team | Handle at team level; log outcome |
| High | Team | Handle at team level; flag in status for awareness |
| Low | Above team | Soft escalation: inform sponsor at next check-in |
| High | Above team | Formal escalation: memo or steering pack; decision required by [date] |

**Issue log entry (minimum):**

| Field | Content |
|---|---|
| Issue ID | Sequential |
| Description | What happened + impact (quantified: "2-day slip on milestone A") |
| Triage disposition | Team / Soft escalation / Formal escalation |
| Resolution options | 2–3 paths with pros/cons |
| Recommended action | One clear recommendation with owner and date |
| Escalation target | Named decision-maker + deadline if formal escalation |

**Do:**
- Complete the triage before the next status touchpoint — do not let issues sit longer than 24 hours without a disposition.
- Bring the recommended action with the issue, not just the problem statement.
- Track time-to-resolve per issue as a team process metric.

**Don't:**
- Escalate every issue regardless of team authority — this trains stakeholders to ignore escalations.
- Let an issue log entry age past the urgency deadline without a documented decision.
- Conflate issues (materialized risks) with risks (potential future events) — they are separate RAID categories with different management rhythms.

## Edge cases / when the rule does NOT apply

- **Safety or regulatory issues**: bypass normal triage; immediately escalate to the appropriate authority with documentation.
- **Issues arising in the final 48 hours before a hard deadline**: triage compresses to "who has the authority to act in the next two hours"; the structure still applies but the time box shrinks.

## See also

- [`../agents/risk-and-raid-analyst.md`](../agents/risk-and-raid-analyst.md) — the agent that owns the issue log and escalation memos
- [`./risk-is-cause-event-consequence.md`](./risk-is-cause-event-consequence.md) — the companion rule for risks (before they materialize as issues)

## Provenance

Codifies the `risk-and-raid-analyst` agent's issue-triage role from `CLAUDE.md` §1. Issue management process from PMBOK 6th edition §13 (Stakeholder Management) and the APM Body of Knowledge (issue tracking + escalation path). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
