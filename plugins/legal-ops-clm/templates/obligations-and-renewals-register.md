# Obligations & Renewals Register — <contract / counterparty>

> Output of `obligations-and-renewals-analyst` / the `obligations-and-renewals` skill. **Not legal advice** — this
> extracts and tracks what the contract says; a lawyer interprets ambiguous language. An obligation with no owner,
> or a renewal with no notice-window deadline, is not ready to track.

## 1. Contract repository metadata

| Field | Value |
|---|---|
| Counterparty | |
| Contract type | |
| Total / annual value | |
| Effective date | |
| Expiry date | |
| Auto-renew? | <yes/no> |
| Notice-window deadline | <the actionable date — track this, not just expiry> |
| Owner (named) | |
| Status | |
| Governing law | |
| Source / repository link | |

## 2. Obligations register

| Obligation (deliverable / SLA / payment / notice / audit right) | Owner (named) | Due date or trigger | Status | Source clause |
|---|---|---|---|---|
| | | | | |
| | | | | |

_An obligation with no named owner is one nobody meets. Flag any ambiguous obligation for a lawyer rather than guessing._

## 3. Renewal / expiry tracker + tiered alerts

| Contract | Expiry | Auto-renew? | Notice-window deadline | Alert tier (90/60/30) | Owner | Decision (renew / renegotiate / exit) |
|---|---|---|---|---|---|---|
| | | | | | | |

_Track the notice window, not just the expiry — an auto-renew fires unless notice is given inside the window._

## 4. Reports this enables

- Expiring-soon / notice-window-closing
- Obligation-due (by owner)
- By-value / by-counterparty
- <route the alert pipeline build to a data plugin if it becomes a system>

---

```
Status: ...
Files changed: ...
Not legal advice: ...
Risk / approval routing: ...
Handoff: ...
Open questions: ...
Grounding checks performed: ...
```
