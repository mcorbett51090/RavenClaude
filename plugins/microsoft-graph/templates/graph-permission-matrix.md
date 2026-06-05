> Use this template to build the **permission matrix** for a Microsoft Graph integration: one row per capability the app needs, mapping it to the exact permission, the delegated-vs-application decision, the consent tier, the least-privilege alternative considered, and the runtime error-disposition. This is the *decision artifact* that feeds the [`graph-app-registration`](graph-app-registration.md) worksheet — fill this first (what the app must do → the narrowest permission that does it), then transcribe the chosen permissions into the registration. Pairs with the [`permission-least-privilege-review`](../skills/permission-least-privilege-review/SKILL.md) skill (the audit playbook) and the [`identity-auth-decision-trees.md`](../knowledge/identity-auth-decision-trees.md) + [`api-error-disposition-decision-trees.md`](../knowledge/api-error-disposition-decision-trees.md) trees.

# Graph Permission Matrix: [Integration Name]

## Metadata

| Field | Value |
|---|---|
| Integration / app name | [name] |
| Runtime context | [ ] User signed in (delegated) / [ ] Daemon (application) / [ ] Both |
| Auth flow | [auth-code+PKCE / client-credentials / OBO / device-code] |
| Owner / team | [name] |
| Last reviewed | [YYYY-MM-DD] |
| Security-reviewer sign-off | [name / date — required for any tenant-wide application permission] |

> **Volatile-fact discipline (CLAUDE.md §3 #9):** every permission name, consent requirement, and `Sites.Selected`-style alternative below is version-volatile. Confirm each against [Microsoft Graph permissions reference](https://learn.microsoft.com/graph/permissions-reference) at fill time and date it; mark anything unconfirmed `[verify-at-use]`.

---

## 1. Capability → permission matrix

One row per *capability the app actually performs*. Start from the capability, not from a permission you already know — that's how over-privilege creeps in. Fill the "narrower alternative considered" column even when you keep the broad one (record *why* you couldn't narrow it).

| # | Capability (what the app does) | Resource / endpoint | Permission | Type (DEL/APP) | Consent (user/admin) | Narrower alternative considered (and why kept/dropped) | Least-privilege verdict |
|---|---|---|---|---|---|---|---|
| 1 | [e.g. read the signed-in user's calendar] | `GET /me/events` | `Calendars.Read` | DEL | user | `Calendars.Read.Shared` not needed → dropped | ✅ narrowest |
| 2 | [e.g. send mail as a service account] | `POST /users/{id}/sendMail` | `Mail.Send` | APP | admin | scoped to specific mailboxes via application access policy | ⚠ tenant-wide unless policy-scoped → **security-reviewer** |
| 3 | [e.g. read specific SharePoint sites] | `GET /sites/{id}/drive` | `Sites.Selected` | APP | admin + per-site grant | `Sites.Read.All` rejected (tenant-wide) → `Sites.Selected` chosen | ✅ site-scoped |
| 4 | | | | | | | |

**Type / consent rules (do not guess — traverse the tree):**
- A **daemon/no-user** capability → **application** permission → **admin consent always**. Application permissions are tenant-wide by default; record the resource-scoping control (application access policy, `Sites.Selected`) or escalate.
- A **user-present** capability → prefer **delegated** (blast radius = the signed-in user). Only go application if acting beyond the user is genuinely required, and justify it.
- See [`identity-auth-decision-trees.md`](../knowledge/identity-auth-decision-trees.md) (delegated-vs-application + user-vs-admin-consent trees).

---

## 2. Runtime error-disposition (wire this into the handler, per capability)

For each capability, confirm the handler dispositions Graph failures by the **specific** status — the cause is not interchangeable (see [`api-error-disposition-decision-trees.md`](../knowledge/api-error-disposition-decision-trees.md)).

| Status | What it means here | Handler action | Retry same call? |
|---|---|---|---|
| 401 | token expired / CAE claims challenge | re-acquire token (honor `WWW-Authenticate`), retry | yes, after re-auth |
| 403 | wrong permission **type** or not consented | fix the matrix row above — re-auth won't help | **no** |
| 429 | throttled | wait ≥ `Retry-After`, backoff+jitter | yes, after wait |
| 410 | (delta) token gone | follow `Location`, full resync, reconcile | **never** the old token |
| 409/412 | conflict / precondition (ETag) | re-read, reconcile, re-issue | re-issue reconciled |
| 5xx | transient | bounded backoff + jitter | yes, bounded |

- [ ] A `403` triggers a **permission/consent review** (this matrix), not a token refresh.
- [ ] A `429` honors `Retry-After` as a floor (no fixed `sleep(1)` retry).
- [ ] Delta consumers have a `410` resync branch.

---

## 3. Credentials & secrets

| Field | Value |
|---|---|
| Credential type | [ ] Managed identity (Azure-hosted) / [ ] Certificate (prod off-Azure) / [ ] Client secret (dev/short-lived only) |
| Secret storage (if secret/cert) | [Key Vault URI / env-var **name** — NEVER a literal in this file] |
| Rotation plan | [e.g. cert auto-rotated 30 days before expiry] |

> Secrets are a **reference, never a literal** — no client secret, certificate, tenant ID, or app ID value belongs in this filled template. Secret/credential handling escalates to `ravenclaude-core/security-reviewer` (CLAUDE.md §3 #8).

---

## 4. Sign-off checklist

- [ ] Every row is the **narrowest** permission that performs the capability (no `.ReadWrite.All` where `.Read` works; no application where delegated works).
- [ ] Every **application** permission has admin consent recorded and a resource-scoping control or a documented reason it must be tenant-wide.
- [ ] Any `Directory.ReadWrite.All`, any tenant-wide application data scope, any secret-over-certificate choice, and any regulated-data handling → **escalated to `ravenclaude-core/security-reviewer`** (skill Step 5).
- [ ] No unused/"just-in-case" permissions (each is blast radius); quarterly re-audit scheduled.
- [ ] Permission names verified against the live permissions reference and dated.

**Security reviewer sign-off:** [Name] [Date]
