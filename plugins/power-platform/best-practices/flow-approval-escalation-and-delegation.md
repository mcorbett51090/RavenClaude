# Build approval flows with escalation, delegation, and timeout — not just the happy path

**Status:** Pattern
**Domain:** Power Automate approvals
**Applies to:** `power-platform`

---

## Why this exists

Power Automate's built-in approval connector is elegant for the one-approver happy path, but production approval workflows always encounter the same three gaps: approvers go on leave (no one else can act), approvals time out silently (the request hangs forever), and there is no audit trail when the original approver delegates. Flows built only for the happy path get stuck in production the first time a manager is on vacation. Escalation and delegation are not polish — they are part of the build.

## How to apply

Structure every approval flow using a `Do until` loop around the `Start and wait for an approval` action, with an explicit timeout branch:

```json
// Recommended approval loop shape
"Do_Until": {
  "actions": { "Start_and_wait_approval": { ... } },
  "expression": "@or(equals(body('Start_and_wait_approval')?['outcome'], 'Approve'),
                    equals(body('Start_and_wait_approval')?['outcome'], 'Reject'),
                    greaterOrEquals(outputs('Get_run_duration'), variables('TimeoutDays')))"
}
```

Checklist:
- [ ] **Timeout:** `Start and wait` has a configurable timeout. Set it to a business-meaningful value (e.g., 3 business days). Branch the `Timed out` outcome to an escalation action.
- [ ] **Escalation recipient:** store the escalation address in an environment variable, not a hard-coded email.
- [ ] **Delegation:** use the **Reassign** option on the approval — do not re-create the approval from scratch, which loses the history thread.
- [ ] **Reminder:** add a scheduled child flow or `Send an email` on day N-1 before timeout.
- [ ] **Audit:** after the approval resolves, write the `outcome`, `approver`, `completionDateTime`, and `comments` to a Dataverse row — the email is not an audit record.

**Do:**
- Design the timeout value as an environment variable so it can differ between environments (test: 1 hour, prod: 72 hours).
- Use `Approval` entity in Dataverse (`msdyn_approval`) to surface pending items in model-driven apps alongside email.
- Test the timeout path in a test environment with a 5-minute timeout before promoting.

**Don't:**
- Leave `Start and wait for an approval` with no timeout expression — it can run forever in a free or seeded flow license until the 30-day run limit kills it silently.
- Re-send a new approval when the original times out without cancelling or closing the original — duplicate open approvals cause confusion and double-act.
- Store the approver's decision only in the email reply — email is not a durable audit record.

## Edge cases / when the rule does NOT apply

For a simple, synchronous, one-step approval inside a test environment with a known short SLA, skipping the timeout loop is acceptable if the timeout is set in the connector itself. Document the reason.

## See also

- [`../agents/flow-engineer.md`](../agents/flow-engineer.md) — owns approval-flow design
- [`./flow-error-handling-and-retry-policy.md`](./flow-error-handling-and-retry-policy.md) — the broader error-handling shape this rule extends

## Provenance

Codifies the `flow-engineer` house opinion from CLAUDE.md §3 #10 ("error handling is part of the build") applied to the approval surface; timeout and delegation patterns from Microsoft Learn Power Automate approval best-practice guide.

---

_Last reviewed: 2026-06-05 by `claude`_
