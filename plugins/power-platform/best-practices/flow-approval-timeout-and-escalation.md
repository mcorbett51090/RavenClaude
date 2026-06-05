# Set Explicit Timeouts and Escalation Paths on Every Approval

**Status:** Absolute rule
**Domain:** Power Automate / Approvals
**Applies to:** `power-platform`

---

## Why this exists

An approval with no timeout waits forever. In production that means a flow paused on an approver who is on vacation, has left the company, or never received the email. The approval action holds a flow license slot, burns daily API requests on heartbeat polling, and blocks any downstream logic indefinitely. When the flow finally times out at the platform's hard limit (30 days), it is deleted with no opportunity for recovery. Every approval that goes unhandled also silently blocks the business process it guards — a PO approval, a leave request, a contract sign-off — until a human manually terminates the flow run.

## How to apply

Set a `requestOptions.timeout` on every `Start and wait for an approval` action. Route the timeout branch to an explicit escalation action (re-assign, notify a delegate, auto-approve, or auto-reject with an audit record).

```json
// Inside the Approval action's settings → "Action Timeout" (ISO 8601)
// P7D = 7 days, PT4H = 4 hours
"requestOptions": {
  "timeout": "P7D"
}
```

**Minimal pattern:**

```
Start and wait for approval (timeout: P7D)
├── Approved → business outcome
├── Rejected → rejection outcome
└── Timed out → Notify manager / re-assign OR auto-reject
              → Append row to Approval Audit log (with reason "Timeout - auto-rejected")
```

**Do:**
- Set `timeout` on every approval action — never leave it at "no timeout."
- Set the timeout to a value that matches the SLA of the business process (leave requests: P1D; PO approvals: P3D; executive sign-off: P7D).
- On timeout, write an audit record explaining why it was auto-resolved, who was the original approver, and the timestamp.
- Configure the approval action to send a reminder before the timeout fires (use a Parallel Branch with a Delay + notification).
- Use a custom email template so approvers can respond from the email without opening the Power Apps portal.

**Don't:**
- Leave the timeout blank or use the platform maximum (30 days) as the default for routine approvals.
- Let the timeout branch terminate the run without an audit record.
- Notify only the original approver on timeout — notify their manager/delegate so the process moves forward.
- Use nested approvals (approvals inside approvals) without a combined timeout budget on the outer flow.

## Edge cases / when the rule does NOT apply

- A fully automated approval (where the "approval" is really a conditional check, not a human action) does not need an approval action at all — use a `Condition` instead.
- An approval that is legally required to remain pending until a specific human responds (e.g., a regulatory sign-off with no delegable authority) may use a long timeout, but must still notify a compliance officer at expiry.

## See also

- [`../agents/flow-engineer.md`](../agents/flow-engineer.md) — owns approval-flow design including escalation
- [`./flow-error-handling-and-retry-policy.md`](./flow-error-handling-and-retry-policy.md) — the broader error-handling discipline that approval timeouts fall under

## Provenance

Codifies `flow-engineer`'s opinion that a production approval with no timeout is a bug (§3 #10 — error handling is part of the build). Pattern sourced from the Power Automate `Start and wait for an approval` action docs + the plugin's `skills/power-automate/` playbook on approval patterns. Standard enterprise practice.

---

_Last reviewed: 2026-06-05 by `claude`_
