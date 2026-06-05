# Assign a named owner to every close-calendar step, not just a task

**Status:** Absolute rule
**Domain:** Close / controllership
**Applies to:** `finance`

---

## Why this exists

A close calendar that lists tasks without owners tells you *what* must happen but leaves the "who is responsible if it doesn't" question unanswered. When a step slips — an accrual isn't posted, a sub-ledger feed doesn't arrive — a task list produces a debate about whose job it was. A named-owner list produces an escalation to a named person within minutes. Controllers routinely inherit calendars with vague "Finance team" assignments that cannot be escalated and do not survive staff changes.

## How to apply

Structure every close-calendar row with five columns:

| Day | Step | Owner (name / role) | Prerequisite | Reviewer |
|---|---|---|---|---|
| D+1 | Post payroll JE | Payroll Accountant | Payroll register sign-off | Controller |
| D+2 | AP sub-ledger close | AP Supervisor | All invoices in | Controller |
| D+3 | Reconcile AR sub-ledger to GL | AR Analyst | AR aging exported | Controller |

**Rules for owner assignment:**
- One person per step, never a team name.
- If a step depends on a feed from another system or team, the *receiver* owns confirming arrival and raising an alert if it is late — not the sender's team.
- Every owner gets a backup (vacation coverage) named in the calendar header, not improvised on the day.

**Do:**
- Name the individual, not the team ("Maria Chen — AP" not "Accounts Payable").
- Include a `Prerequisite` column so owners know what they are waiting on before they start.
- Review the owner list at the start of each quarter to catch role changes.

**Don't:**
- Assign "Finance team" or "Controller's office" — these are not people.
- Leave the Reviewer column empty; unsigned work is unreviewed work.
- Set target dates without a time-of-day deadline; "Day+2" without a time produces end-of-day rushes.

## Edge cases / when the rule does NOT apply

For a sole-proprietor or two-person finance team, shared ownership by role is acceptable when names are interchangeable and both parties know it. Document the acknowledgment in the calendar header. Even then, a reviewer is still required.

## See also

- [`../agents/controller.md`](../agents/controller.md) — owns the close-calendar build and the step-by-step reconciliation discipline.
- [`./controller-every-journal-entry-carries-a-memo-and-reviewer.md`](./controller-every-journal-entry-carries-a-memo-and-reviewer.md) — the companion rule for JE sign-off within the same close.

## Provenance

Codifies the `controller` agent's operational standard from CLAUDE.md §3 house opinion #6 ("audit trail in every workpaper — date prepared, preparer, reviewer, source-data lineage") applied to close-calendar design. Close-calendar ownership discipline is a standard controller-function practice and a recurring finding in external-audit management letters when absent.

---

_Last reviewed: 2026-06-05 by `claude`_
