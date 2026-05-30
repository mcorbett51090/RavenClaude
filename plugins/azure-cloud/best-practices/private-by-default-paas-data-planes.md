# Private-by-default for PaaS data planes

**Status:** Absolute rule — a public PaaS data plane is the single highest-blast-radius default mistake in an Azure estate.

**Domain:** Networking / Security

**Applies to:** `azure-cloud`

---

## Why this exists

Key Vault, Storage, Azure SQL, Cosmos, App Configuration, and Container Registry all ship with their data plane **reachable from the public internet** unless you turn that off. A secret store or a customer database one firewall rule away from `0.0.0.0/0` is the most common way an otherwise well-architected Azure estate leaks. The fix is cheap and structural: reach every PaaS data plane over a **Private Endpoint** wired to a **Private DNS zone**, with `publicNetworkAccess` set to `Disabled`. Public exposure then becomes an explicit, justified, reviewed exception rather than the silent default. This is the plugin's strongest single posture (house opinion #6), and the anti-pattern hook flags `publicNetworkAccess: 'Enabled'`, `0.0.0.0/0`, `allowBlobPublicAccess: true`, and `allowSharedKeyAccess: true`.

## How to apply

Disable public access at resource creation, then add a Private Endpoint + Private DNS zone so in-VNet callers resolve the resource to its private IP.

```bicep
resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: kvName
  location: location
  properties: {
    sku: { family: 'A', name: 'standard' }
    tenantId: tenant().tenantId
    enableRbacAuthorization: true
    publicNetworkAccess: 'Disabled'          // not 'Enabled'
    networkAcls: { defaultAction: 'Deny', bypass: 'AzureServices' }
  }
}

resource pe 'Microsoft.Network/privateEndpoints@2023-11-01' = {
  name: 'pe-${kvName}'
  location: location
  properties: {
    subnet: { id: privateEndpointSubnetId }
    privateLinkServiceConnections: [ {
      name: 'kv'
      properties: { privateLinkServiceId: kv.id, groupIds: [ 'vault' ] }
    } ]
  }
}
// + a privatelink.vaultcore.azure.net Private DNS zone, linked to the VNet,
//   with an A record group wired from the Private Endpoint.
```

**Do:**
- Set `publicNetworkAccess: 'Disabled'` (or `networkAcls.defaultAction: 'Deny'`) at creation, not as a follow-up hardening pass.
- Pair every Private Endpoint with the matching `privatelink.*` Private DNS zone linked to the consuming VNet — without DNS the endpoint resolves to nothing.
- Prefer Entra/RBAC + managed identity over shared keys (`allowSharedKeyAccess: false`, `enableRbacAuthorization: true`).

**Don't:**
- Leave `allowBlobPublicAccess: true` or a `0.0.0.0/0` firewall rule "to unblock the demo."
- Treat public access as the baseline and private as the upgrade — it's the reverse.

## Edge cases / when the rule does NOT apply

- **Genuinely public assets** — a Storage account fronting a public static website, or a public package feed — are a legitimate public data plane, but document the exception and scope it (one account, not the whole estate).
- **Services without Private Link support** at a given SKU/tier require service-firewall allow-lists (specific VNets/IPs, never `0.0.0.0/0`) as the fallback — still not open public access.
- **Sandbox / throwaway environments** under the `sandbox` archetype (no prod connectivity) may relax this; anything on a promotion path may not.
- Any deny-public **exception** is a network-security decision and routes to `ravenclaude-core/security-reviewer`.

## See also

- [`../knowledge/azure-networking-and-connectivity.md`](../knowledge/azure-networking-and-connectivity.md) — Private Endpoints, Private DNS, hub-spoke, edge/ingress, the private-by-default section
- [`../knowledge/azure-compute-decision-tree.md`](../knowledge/azure-compute-decision-tree.md) — the data tier whose planes this rule locks down
- [`../agents/network-engineer.md`](../agents/network-engineer.md) — owns Private Endpoints + deny-public posture
- [`../agents/entra-identity-engineer.md`](../agents/entra-identity-engineer.md) — managed identity that reaches a Private-Endpoint'd resource

## Provenance

Codifies house opinion #6 from [`../CLAUDE.md`](../CLAUDE.md) §3 ("Private-by-default for PaaS data planes") and the matching anti-pattern (§4) + the four grep checks in the `check-azure-anti-patterns.sh` hook (§7). Grounded in Microsoft Learn CAF connectivity + WAF guidance as captured in the networking knowledge file (retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
