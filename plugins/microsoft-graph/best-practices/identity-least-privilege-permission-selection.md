# Least-privilege permission selection — request the narrowest scope that works

**Status:** Absolute rule — a `.ReadWrite.All` / `.All` permission where a narrower one would do is an over-privilege defect, and the verdict is a security control.

**Domain:** Identity

**Applies to:** `microsoft-graph`

---

## Why this exists

Every permission an app holds is attack surface: a compromised app, a leaked credential, or a buggy code path can do everything its scopes allow. `Directory.ReadWrite.All` granted "to be safe" lets an app rewrite the directory; `Mail.ReadWrite` where `Mail.Read` was needed lets it send and delete. Over-broad scopes also make admin consent harder to get — a reviewer who sees `full access to all mailboxes` for an app that only needs to read one will (correctly) refuse. The least-privileged permission for a scenario is **not** obvious and can differ between delegated and application access (e.g. reading users app-only needs only `User.Read.All`, not `Directory.Read.All`). So least-privilege is a deliberate selection you verify against the permissions reference, justify, and route to review — never a guess rounded up.

## How to apply

Start from the operation and climb to the **smallest** permission that covers it. Walk the ladder, stop at the first rung that works.

```text
Read the signed-in user's own profile      → User.Read           (delegated, no admin consent)
Read other users' basic profiles           → User.ReadBasic.All  (no admin consent)
Read all users' full profiles              → User.Read.All       (admin consent)
Read users AND groups AND apps AND policies → Directory.Read.All  ← over-privilege if you only needed users

Read mail   → Mail.Read        (NOT Mail.ReadWrite)
Read files  → Files.Read.All    (NOT Files.ReadWrite.All)
One site    → Sites.Selected    (NOT Sites.ReadWrite.All)  — see resource-scoped doc
```

```http
# Request exactly the scopes the feature needs — here, read-only user + own profile
GET https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize
  ?client_id={app}&scope=openid+profile+https://graph.microsoft.com/User.Read.All
  &response_type=code&...
```

**Do:**

- Pick `.Read` over `.ReadWrite`; pick the resource-specific permission (`User.Read.All`) over the umbrella (`Directory.Read.All`).
- Verify the *actual* least-privileged permission for your operation against the [Microsoft Graph permissions reference](https://learn.microsoft.com/graph/permissions-reference) — don't assume the obvious-named one is narrowest.
- Justify each scope in one line and **escalate the scope list to `ravenclaude-core/security-reviewer`**.
- Drop a permission the moment the feature that needed it is gone.

**Don't:**

- Request `.ReadWrite.All` / `Directory.*` as a catch-all "so I don't have to come back."
- Carry permissions that no current code path exercises.
- Treat `Application.ReadWrite.All`, `AppRoleAssignment.ReadWrite.All`, or `RoleManagement.*` as ordinary — they let an app act as other identities; flag loudly.

## Edge cases / when the rule does NOT apply

A genuinely broad admin tool (e.g. a tenant migration utility) may legitimately need `Directory.ReadWrite.All` — but that breadth is the thing you document and route to review, not the default. Some operations have **no** narrow permission and only a `.All` exists `[verify-at-build]`; that's a constraint to note, not over-privilege. Incremental/dynamic consent (delegated only) lets you request scopes feature-by-feature over time rather than all up front — a least-privilege *technique*, not an exception to the rule.

## See also

- [`./identity-resource-scoped-over-tenant-wide.md`](./identity-resource-scoped-over-tenant-wide.md) — `Sites.Selected` / RSC beat `.All` when they exist
- [`./identity-delegated-vs-application-is-a-design-choice.md`](./identity-delegated-vs-application-is-a-design-choice.md) — least-privilege differs by access type
- [`./identity-admin-consent-and-the-consent-framework.md`](./identity-admin-consent-and-the-consent-framework.md) — broader scopes pull in admin consent
- [`../knowledge/identity-auth-decision-trees.md`](../knowledge/identity-auth-decision-trees.md) — consent + permission-type trees
- [`../agents/graph-identity-engineer.md`](../agents/graph-identity-engineer.md) — owns selection; escalates the verdict
- [Microsoft Graph permissions reference](https://learn.microsoft.com/graph/permissions-reference) — authoritative permission names/IDs

## Provenance

From the Microsoft Learn permissions-overview, permissions-reference, and Azure-AD-Graph→Microsoft-Graph permissions-differences pages (retrieved 2026-05-30 via Microsoft Learn MCP) — the latter documents that reading users app-only needs only `User.Read.All`, not the broader `Directory.Read.All`. Codifies team house opinion #1 ("least-privilege permissions, always"). Permission names and least-privilege mappings are volatile — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
