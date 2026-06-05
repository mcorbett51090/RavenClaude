---
name: permission-least-privilege-review
description: "Step-by-step playbook for auditing a Microsoft Graph app's permission scope list: delegated vs application decision, narrowing over-broad scopes, finding resource-scoped alternatives, and the escalation criteria for ravenclaude-core/security-reviewer. Owned by graph-identity-engineer."
---

# Permission Least-Privilege Review

## When to invoke

- Selecting permissions for a new Graph app registration.
- Auditing an existing app's scope list before a security review or compliance audit.
- A call is returning `403 Forbidden` and the scope is unclear.
- The app currently uses `.ReadWrite.All` or `.All` permissions and needs narrowing.

## Step 1 — Delegated vs application: make the decision explicit

| Type | When to use | Identity at runtime |
|---|---|---|
| **Delegated** | A signed-in user is present; the action is on behalf of that user | The user + the app (both must consent) |
| **Application** | No user; daemon, background job, scheduled task, service | The app only (admin consent required) |

**Never default to application permissions "because it's simpler."** Application permissions grant the app access to ALL users' data in the tenant (e.g., `Mail.Read` application reads every mailbox). Delegated limits the blast radius to the signed-in user's data.

Decision rule:
```
Is a user interactively signed in?
├── YES → delegated
└── NO  → application (proceed to Step 2 with extra scrutiny)
```

## Step 2 — Scope narrowing checklist

For each scope in the app's manifest:

| Check | Action |
|---|---|
| Is it `*.ReadWrite.All` when only read is needed? | Replace with `*.Read.All` |
| Is it `*.All` when a resource-scoped permission exists? | Find the narrower permission (see table below) |
| Is it an application permission when a delegated one would work? | Downgrade to delegated |
| Is it `Directory.ReadWrite.All`? | Escalate to security-reviewer — this is near-tenant-admin |
| Is it `Mail.ReadWrite` application when only read is needed? | Replace with `Mail.Read` |

**Common resource-scoped alternatives:**

| Broad scope | Narrower alternative | Tradeoff |
|---|---|---|
| `Files.ReadWrite.All` | `Files.ReadWrite` (delegated, signed-in user's files only) | User must be signed in |
| `Calendars.ReadWrite` (application) | `Calendars.ReadWrite` (delegated) | Scoped to signed-in user |
| `Group.ReadWrite.All` | `Group.Read.All` + `GroupMember.ReadWrite.All` | Split read vs membership write |
| `Sites.ReadWrite.All` | `Sites.Selected` (application, site-specific consent) | Requires Site admin to grant; preferred for service apps |

## Step 3 — Sites.Selected for SharePoint/OneDrive daemon apps

If the app is a daemon accessing specific SharePoint sites:

1. Register the app with `Sites.Selected` (application permission).
2. Have a SharePoint site admin grant the app access to specific sites via the Graph API or SharePoint admin center.
3. The app can only read/write those specific sites — not the entire tenant.

This is the least-privilege choice for SharePoint service integrations. `Sites.ReadWrite.All` on a daemon app is a high-blast anti-pattern.

## Step 4 — Verify consent state

A `403 Forbidden` from Graph is almost always one of:
1. **Missing admin consent** for an application permission (use `GET /servicePrincipals/{id}/appRoleAssignments` to verify granted roles).
2. **Missing user consent** for a delegated permission (the user hasn't seen the consent dialog).
3. **Correct permission but wrong type** (delegated permission granted but app is using client-credentials flow → application context; vice versa).
4. **Scope missing from the access token** (the permission is granted in Entra but not included in the token's `scp` claim — check token with jwt.ms).

```python
import jwt  # PyJWT
import base64, json

# Decode token (no verification — for debugging only)
parts = access_token.split(".")
payload = json.loads(base64.b64decode(parts[1] + "=="))
print("scp:", payload.get("scp"))    # delegated scopes
print("roles:", payload.get("roles"))  # application roles
```

## Step 5 — Escalation criteria

Always escalate to `ravenclaude-core/security-reviewer` when:

- [ ] Any application permission that grants tenant-wide data access (`Mail.Read`, `User.Read.All`, `Files.ReadWrite.All`, `Directory.*` as application).
- [ ] `Directory.ReadWrite.All` — this is effectively a Tier 0 / tenant admin scope.
- [ ] The app will be granted admin consent by an Entra Global Admin (document why each scope is necessary; security-reviewer signs off on the justification).
- [ ] A client secret is used instead of certificate credentials for an application-permission app.
- [ ] The app handles regulated data (PHI, PII, financial) even with narrow scopes.

## Pitfalls

- Requesting `offline_access` without a stated reason — this enables long-lived refresh tokens; document the session duration requirement.
- Using `User.Read.All` (application) when `User.Read` (delegated) plus the signed-in user's profile is sufficient.
- Testing with a Global Admin account and concluding "it works" — admins bypass consent and some permission checks; always test with a standard user account.
- Adding permissions "just in case" — every unused permission is a blast radius waiting to be exploited; audit quarterly and remove unused scopes.
