# Use PIM for privileged roles — no standing Owner or Contributor

**Status:** Absolute rule
**Domain:** Azure identity / governance
**Applies to:** `azure-cloud`

---

## Why this exists

Standing `Owner` or `Contributor` at subscription scope is the widest blast radius an identity can hold in Azure. A compromised account with standing Owner can delete all resources, exfiltrate secrets, and assign itself new roles — with nothing to time-box the access. Azure AD Privileged Identity Management (PIM) converts standing assignments to just-in-time (JIT) eligible assignments: the user requests elevation, provides a justification, and receives time-limited access (e.g., 1 hour). The hook in `check-azure-anti-patterns.sh` flags `Owner`/`Contributor` role assignments at subscription/MG scope in IaC for exactly this pattern.

## How to apply

Configure PIM eligibility via Bicep or Terraform, not standing assignment:

```bicep
// WRONG — standing Owner assignment (hook flags this)
resource wrongAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, 'owner-standing')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8e3af657-a8ff-443c-a75c-2fe8c4bcb635') // Owner
    principalId: adminObjectId
    principalType: 'User'
  }
}

// RIGHT — PIM eligible assignment (user must activate)
resource pimEligible 'Microsoft.Authorization/roleEligibilityScheduleRequests@2022-04-01-preview' = {
  name: guid(subscription().id, 'owner-eligible')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8e3af657-a8ff-443c-a75c-2fe8c4bcb635')
    principalId: adminObjectId
    requestType: 'AdminAssign'
    scheduleInfo: {
      expiration: {
        type: 'NoExpiration'
      }
    }
  }
}
```

PIM policy settings (configure in Entra → PIM → Azure resources → Role settings):
- **Maximum activation duration**: 1 hour (production), 4 hours (break-glass)
- **Require justification on activation**: Yes
- **Require MFA on activation**: Yes
- **Require approval**: Yes for Owner; discretionary for Contributor

**Do:**
- Convert all standing Owner/Contributor subscription-scope assignments to PIM eligible.
- Scope Contributor to resource groups, not subscriptions, wherever possible.
- Enable PIM audit logs and alert on activation of sensitive roles.
- Maintain two break-glass accounts (emergency access) with standing Owner — document, vault the credentials, and audit monthly.

**Don't:**
- Grant standing Owner "temporarily" — temporary assignments become permanent.
- Create a service principal with standing Owner for automation — use managed identity + least-privilege.
- Forget break-glass accounts — PIM misconfiguration can lock out admins; two break-glass accounts are the safety net.

## Edge cases / when the rule does NOT apply

- **Break-glass emergency accounts**: two standing Owner accounts at the root management group are standard and expected. Store credentials in a physical safe; audit access quarterly.
- **Service principals for IaC pipelines**: use WIF + minimum required role (e.g., `Contributor` scoped to the target RG). PIM is for human identity; automation uses role assignments scoped to the deployment target.

## See also

- [`../agents/entra-identity-engineer.md`](../agents/entra-identity-engineer.md) — owns PIM configuration and privileged identity design.
- [`./identity-rbac-least-privilege-and-custom-roles.md`](./identity-rbac-least-privilege-and-custom-roles.md) — PIM is the time-gating layer; RBAC scope is the blast-radius layer.
- [`./entra-wif-for-ci-cd-not-client-secrets.md`](./entra-wif-for-ci-cd-not-client-secrets.md) — WIF removes the need for service principal secrets in CI/CD.

## Provenance

Codifies house opinion #5 from `CLAUDE.md` §3: "Least-privilege + PIM; no standing Owner." The hook in `hooks/check-azure-anti-patterns.sh` flags this pattern. Grounded in `knowledge/entra-identity-and-access.md` and Microsoft's PIM documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
