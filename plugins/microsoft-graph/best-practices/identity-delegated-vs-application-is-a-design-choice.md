# Delegated vs application permissions is a design choice — state it before writing auth code

**Status:** Absolute rule — picking delegated or application by convenience instead of by "is there a signed-in user?" is a security defect, not a style preference.

**Domain:** Identity

**Applies to:** `microsoft-graph`

---

## Why this exists

Microsoft Graph supports exactly two access scenarios, and they have profoundly different blast radii. In **delegated access** the app calls Graph *on behalf of a signed-in user* and **can never access anything that user couldn't access themselves** — the effective access is the intersection of the app's scope and the user's own permissions. In **app-only (application) access** the app calls Graph *as itself with no user*, and an application permission like `Files.Read.All` lets it read **every** file in the tenant. Choosing application when delegated was correct silently grants tenant-wide reach with no user ceiling; choosing delegated when the workload is a daemon means it breaks the moment there's no interactive user. Because the choice changes who can consent (application permissions **always** require admin consent) and how much data is reachable, it is a design decision that must be stated and justified — never defaulted.

## How to apply

Ask one question first: **is there a signed-in user in the loop at call time?**

- **Yes, a user is present** (web app, SPA, mobile, CLI a person runs) → **delegated** permission (a *scope*, e.g. `User.Read`, `Mail.Read`).
- **No user — a daemon, background service, timer job, or connector agent** → **application** permission (an *app role*, e.g. `User.Read.All` application).

```text
# Delegated — token carries the user; access is capped by the user's own rights
GET /me/messages          scope: Mail.Read (delegated)   → only this user's mail

# Application — no user; access is whatever the permission covers, tenant-wide
GET /users/{id}/messages  role:  Mail.Read (application) → ANY mailbox in tenant
```

**Do:**

- Write the choice as a sentence in the design: "App-only because it's a nightly sync with no user" or "Delegated because it acts as the signed-in user."
- Remember that connector/background agents *require* application permissions — delegated permissions cause registration failures there `[verify-at-build]`.
- Treat application permissions as the higher-trust path: admin-consent-only, no user ceiling.

**Don't:**

- Reach for an application permission "so it always works" — that trades a user ceiling for tenant-wide exposure.
- Use a delegated permission for an unattended/background job — there's no user to consent or to scope it.
- Assume the same display string means the same blast radius — `Files.Read.All` delegated is bounded by the user; application is not.

## Edge cases / when the rule does NOT apply

A web API that must call Graph **as the original user** is still delegated — but it uses the [on-behalf-of flow](./auth-pick-the-flow-by-client-type.md), not a fresh delegated sign-in. Some Graph resources expose only delegated *or* only application permissions for a given operation; the [permissions reference](https://learn.microsoft.com/graph/permissions-reference) is authoritative on which exist `[verify-at-build]`. A few permissions (e.g. RSC) are neither classic delegated nor classic tenant-wide application — see [resource-scoped over tenant-wide](./identity-resource-scoped-over-tenant-wide.md).

## See also

- [`./identity-least-privilege-permission-selection.md`](./identity-least-privilege-permission-selection.md) — once you've picked the type, pick the narrowest permission
- [`./identity-admin-consent-and-the-consent-framework.md`](./identity-admin-consent-and-the-consent-framework.md) — application permissions are admin-consent-only
- [`./auth-pick-the-flow-by-client-type.md`](./auth-pick-the-flow-by-client-type.md) — the flow follows from this choice
- [`../knowledge/identity-auth-decision-trees.md`](../knowledge/identity-auth-decision-trees.md) — "Delegated vs Application" tree
- [`../agents/graph-identity-engineer.md`](../agents/graph-identity-engineer.md) — owns this decision; escalates the verdict
- [Overview of Microsoft Graph permissions — permission types](https://learn.microsoft.com/graph/permissions-overview#permission-types) — authoritative

## Provenance

From the Microsoft Learn "Overview of Microsoft Graph permissions" and "Overview of permissions and consent in the Microsoft identity platform" pages (retrieved 2026-05-30 via Microsoft Learn MCP), codifying team house opinion #2 ("delegated vs application is a design decision, not a default"). The `Files.Read.All` delegated-vs-app contrast and the connector-agent application-permission requirement are drawn directly from those pages. Permission existence/type per resource is volatile — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
