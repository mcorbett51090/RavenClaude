# Quarantine unused apps and flows before deletion; don't silently delete production resources

**Status:** Pattern
**Domain:** Power Platform governance
**Applies to:** `power-platform`

---

## Why this exists

The Power Platform CoE Starter Kit's inactivity signals (last modified, last used, run count = 0) identify resources that appear abandoned, but "no recent usage" is not "safe to delete." A flow might run quarterly; an app might be used by one administrator who was on leave. Deleting without a quarantine period — during which the owner receives a notification and can object — creates incidents where production automation is silently removed. Equally, leaving unused resources running wastes capacity and makes DLP audit noise. The quarantine pattern threads the needle: disable (not delete) the resource, notify the owner, and delete only after a defined silence window.

## How to apply

Use the CoE Starter Kit's **App Quarantine** and flow **Lifecycle Management** flows as the orchestration layer, or implement the equivalent steps manually:

```
Step 1: Signal — identify inactive resources via the Inventory tables in the CoE Dataverse solution.
Step 2: Notify — email the owner + co-owners with a 30-day objection window (customize with an env var).
Step 3: Disable — if no objection, disable (not delete): suspend the flow / unpublish the app.
Step 4: Watch — monitor for re-activation requests for an additional 14 days.
Step 5: Delete — only after Step 4 window expires with no owner action.
```

Environment variable names (if you build your own):
- `admin_QuarantineNotificationDays` — days before disabling (default 30)
- `admin_DeleteAfterDays` — days after disabling before deletion (default 14)
- `admin_GracePeriodContact` — email address that receives objection requests

**Do:**
- Write an audit row to a Dataverse table at each step (notified, disabled, deleted) with the acting admin's user ID.
- Exclude resources in active, production-labelled environments from the quarantine signal unless specifically targeted by an admin.
- Confirm the flow's connection references are still bound before disabling — a broken connection reference already signals the owner has moved on.

**Don't:**
- Delete a resource that is inside a solution that is also used by other resources — remove the component from the solution, wait one quarantine cycle, then delete.
- Use the CoE bulk-delete scripts against the Default environment without filtering by environment type — the Default environment contains every licensed user's personal work.
- Substitute "last modified" as the sole signal — a flow authored once and running reliably for two years has a very old "last modified" date.

## Edge cases / when the rule does NOT apply

Resources flagged as security risks by the `pac solution check` rule set (e.g., a custom connector calling an unauthorized endpoint) skip the notification window and go straight to admin disable. The security escalation overrides the quarantine ceremony.

## See also

- [`../agents/power-platform-admin.md`](../agents/power-platform-admin.md) — owns tenant governance and lifecycle management
- [`./gov-managed-environments-and-sharing-limits.md`](./gov-managed-environments-and-sharing-limits.md) — the environment strategy these lifecycle decisions operate within

## Provenance

Codifies `power-platform-admin`'s opinion from CLAUDE.md §3 applied to resource lifecycle; aligned with CoE Starter Kit Lifecycle Management module documented in Microsoft Learn.

---

_Last reviewed: 2026-06-05 by `claude`_
