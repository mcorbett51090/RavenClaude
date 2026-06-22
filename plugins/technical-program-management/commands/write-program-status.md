---
description: Write a decision-led program status update — lead with the change in risk/critical path, the decision needed, and the explicit ask; roll up the worst dependency, not the average; push activity to the bottom.
argument-hint: "[the program + this period's events, e.g. 'billing program, week of 6/14: API slipped, ledger ahead']"
---

# Write program status

You are running `/technical-program-management:write-program-status`. Draft the
status for `$ARGUMENTS` using the `technical-program-manager` discipline: status
leads with decisions and asks, not activity.

## Steps

1. **Open with what changed** in the risk / critical-path picture this period.
2. **State the decision needed** (specific choice + deadline + cost of delay), or
   omit if none.
3. **State the ask** — what you need from the reader, by when.
4. **Roll up overall status from the worst dependency**, not the average — a green
   status with a red dependency is a lie.
5. **Push activity/completed work to the bottom**, under "supporting detail."

Use the [`program-status-update`](../templates/program-status-update.md) template.

## Guardrails

- Never open with "This week the team…" — that's activity-led and has failed.
- If any critical-path dependency is red, the overall status cannot be green.
