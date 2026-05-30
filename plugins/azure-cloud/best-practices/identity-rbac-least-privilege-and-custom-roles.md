# Scope RBAC to the resource/RG with least-privilege roles — custom over wildcard, PIM over standing Owner

**Status:** Absolute rule — `Owner`/`Contributor` at subscription/MG scope in IaC is the privilege-escalation default mistake; the hook flags it.

**Domain:** Identity / Authorization

**Applies to:** `azure-cloud`

---

## Why this exists

The path of least resistance is to assign `Contributor` (or `Owner`) at subscription scope and move on — and that is precisely how an estate ends up with a dozen principals that can do anything anywhere. House opinion #5 is "least-privilege + PIM": scope each assignment to the **resource group or resource**, not the subscription/MG; prefer a **built-in role that names the exact data/control actions** (e.g. `Key Vault Secrets User`, `Storage Blob Data Reader`) over a broad one; author a **custom role** when no built-in fits rather than over-granting; and give platform teams elevated access only **just-in-time through PIM**, never standing `Owner`. Microsoft's own guidance caps a subscription at **≤3 owners**. The anti-pattern hook flags `Owner`/`Contributor` assigned at subscription/MG scope in IaC.

## How to apply

Assign a narrowly-scoped built-in role at RG/resource scope. When none fits, define a custom role enumerating the exact `Actions`/`DataActions` with `assignableScopes` set to the RG — not the subscription.

```bicep
// Built-in, narrowly scoped: the app's MI reads secrets — nothing more
resource secretsUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(kv.id, app.id, 'kv-secrets-user')
  scope: kv                                  // resource scope, not the subscription
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions',
      '4633458b-17de-408a-b874-0445c86b69e6')  // Key Vault Secrets User
    principalId: app.identity.principalId
    principalType: 'ServicePrincipal'
  }
}
```

```json
// Custom role — enumerate exact actions, scope to the RG (avoid wildcards)
{
  "Name": "Payments Deploy Operator",
  "Description": "Deploy + restart the payments app; no role or policy writes.",
  "Actions": [
    "Microsoft.Web/sites/read",
    "Microsoft.Web/sites/restart/action",
    "Microsoft.Web/sites/slots/*"
  ],
  "NotActions": [],
  "AssignableScopes": [ "/subscriptions/<sub>/resourceGroups/rg-payments-prod-eastus-001" ]
}
```

**Do:**
- Scope assignments to the **RG or resource**; reach for the **most specific built-in role** that grants exactly the needed actions.
- Write a **custom role** (explicit `Actions`/`DataActions`, RG-scoped `assignableScopes`) when no built-in fits — explicit actions over a `*` wildcard.
- Grant platform/admin elevation through **PIM** (just-in-time, time-bound, approval-gated); keep subscription owners **≤3**.

**Don't:**
- Assign `Owner`/`Contributor` at **subscription/MG** scope in IaC (the hook flags it) — or hand out standing `Owner`.
- Use a `*` wildcard `Action` when the specific operations are knowable — future actions get silently included.
- Put a custom role with `DataActions` at MG scope — RBAC forbids it; scope data-plane roles at subscription/RG.

## Edge cases / when the rule does NOT apply

- **Platform teams** legitimately need broad scope — but through **PIM** (eligible, not active), never a standing assignment.
- **A genuinely cross-RG operator** (e.g. a backup principal) may need subscription scope — use the narrowest built-in role (e.g. `Backup Operator`), not `Contributor`, and document it.
- The **role/scope design itself** is a security decision → route to `ravenclaude-core/security-reviewer`.

## See also

- [`../knowledge/entra-identity-and-access.md`](../knowledge/entra-identity-and-access.md) — RBAC least-privilege, PIM, the authorization section
- [`./passwordless-by-default.md`](./passwordless-by-default.md) — the managed identity this role gets assigned to
- [`./lz-flat-management-group-hierarchy.md`](./lz-flat-management-group-hierarchy.md) — why app-team RBAC rides subscription/RG scope, not the MG tree
- [`../agents/entra-identity-engineer.md`](../agents/entra-identity-engineer.md) — owns RBAC/PIM · [`../agents/azure-ops-engineer.md`](../agents/azure-ops-engineer.md) — enforces it

## Provenance

Codifies house opinion #5 from [`../CLAUDE.md`](../CLAUDE.md) §3 and the §4/§7 anti-pattern (`Owner`/`Contributor` at subscription/MG scope — hook-flagged). Grounded in Microsoft Learn [Azure RBAC best practices](https://learn.microsoft.com/azure/role-based-access-control/best-practices) (least privilege; ≤3 subscription owners), [custom roles](https://learn.microsoft.com/azure/role-based-access-control/custom-roles) (5,000/tenant limit; `DataActions` can't be MG-scoped; prefer explicit actions over `*`), and [role definitions](https://learn.microsoft.com/azure/role-based-access-control/role-definitions) (`Actions − NotActions`) — retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
