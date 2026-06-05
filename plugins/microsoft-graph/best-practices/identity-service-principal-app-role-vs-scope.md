# Distinguish app roles from OAuth2 scopes — assigning the wrong one produces silent 403 failures

**Status:** Primary diagnostic
**Domain:** Microsoft Graph / identity
**Applies to:** `microsoft-graph`

---

## Why this exists

Entra app registrations expose both **OAuth2 permission scopes** (used for delegated access — a signed-in user's delegated permission) and **app roles** (used for application access — daemon/service-to-service). Developers frequently confuse them and assign the OAuth2 scope to an application registration when they needed to grant an app role — producing a `403 Forbidden` at runtime because the permission granted is not the type the flow expects. The Graph Explorer and the portal display them in similar-looking lists and do not visually distinguish whether the grant was a scope or an app-role assignment.

## How to apply

| Access type | Permission type | How granted |
|---|---|---|
| Delegated (user signs in) | **OAuth2 permission scope** | User consent or admin consent on the app registration's API permissions (Delegated) |
| Application (daemon, no user) | **App role** | Admin consent only; must be assigned via `appRoleAssignments` on the service principal, not just declared |

Diagnosis checklist when you get a `403` on a Graph call:

1. Confirm whether the access is delegated or application (`identity-delegated-vs-application-is-a-design-choice.md`).
2. Open **Entra → App registrations → {App} → API permissions**: is the permission listed under "Delegated" or "Application"?
3. Confirm **Admin consent has been granted** — a permission listed without a green checkmark is declared but not consented.
4. For application permissions, confirm the **service principal has an app-role assignment** (not just the registration): `GET /servicePrincipals/{sp-id}/appRoleAssignments`.

**Do:**
- Use Microsoft Graph PowerShell or `az rest` to confirm the effective permission set before debugging in code.
- When assigning an app role, use the `resourceId` of the **target API's service principal** (for Graph, this is `00000003-0000-0000-c000-000000000000`) not the app registration itself.
- Document whether each permission in the app is delegated or application to prevent future confusion.

**Don't:**
- Assume "Admin consent granted" on the App registrations → API permissions page means the app role is assigned — these are two different portal operations.
- Use the same app registration for both delegated (user-facing) and application (daemon) flows without clearly separating their permission declarations.
- Rely on the Graph Explorer's "Modify permissions" flow to configure application permissions — Graph Explorer works with delegated access; application permissions must be assigned via PowerShell or the API.

## Edge cases / when the rule does NOT apply

Some Graph API resources support both delegated and application access with the same effective permission name (e.g., `Mail.Read` exists as both a delegated scope and an application role). In these cases, the same surface area applies but the grant mechanism differs — still follow the diagnosis checklist.

## See also

- [`../agents/graph-identity-engineer.md`](../agents/graph-identity-engineer.md) — owns permission-type selection and consent design
- [`./identity-delegated-vs-application-is-a-design-choice.md`](./identity-delegated-vs-application-is-a-design-choice.md) — the upstream rule for choosing which access type is correct

## Provenance

Codifies a common diagnostic from CLAUDE.md §3 #2 ("delegated vs application is a design decision, not a default") applied to the permission-grant mechanics; Microsoft Entra app-role assignment documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
