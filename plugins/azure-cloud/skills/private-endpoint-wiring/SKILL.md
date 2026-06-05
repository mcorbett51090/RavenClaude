---
name: private-endpoint-wiring
description: "Step-by-step playbook for locking down Azure PaaS services (Key Vault, Storage, SQL, Cosmos) behind Private Endpoints with Private DNS — covers DNS zone setup, NSG rules, and the disable-public-access checklist."
---

# Private Endpoint Wiring

## When to Use This Skill

Use when provisioning any PaaS data-plane service (Key Vault, Storage Account, Azure SQL, Cosmos DB, Container Registry, App Configuration, Service Bus) in a non-public environment, or when remediating a service flagged as publicly accessible.

## 1. The Three Steps

Every Private Endpoint wiring follows the same three steps regardless of the target service:

1. **Create the Private Endpoint** in the target subnet
2. **Create the Private DNS Zone** (or link to an existing hub zone)
3. **Disable public network access** on the target resource

## 2. Bicep Pattern (Key Vault example)

```bicep
// Step 1: Private Endpoint
resource kvPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-09-01' = {
  name: 'pe-${keyVaultName}'
  location: location
  properties: {
    subnet: {
      id: subnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'kv-connection'
        properties: {
          privateLinkServiceId: keyVault.id
          groupIds: ['vault']
        }
      }
    ]
  }
}

// Step 2: Private DNS Zone Group (links endpoint to the DNS zone)
resource kvDnsGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-09-01' = {
  parent: kvPrivateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'privatelink-vaultcore-azure-net'
        properties: {
          privateDnsZoneId: kvPrivateDnsZone.id
        }
      }
    ]
  }
}

// Step 3: Disable public access
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
    // ...
  }
}
```

## 3. Private DNS Zone Names by Service

| Service | `groupIds` value | Private DNS Zone |
|---|---|---|
| Key Vault | `vault` | `privatelink.vaultcore.azure.net` |
| Storage (blob) | `blob` | `privatelink.blob.core.windows.net` |
| Storage (file) | `file` | `privatelink.file.core.windows.net` |
| Azure SQL | `sqlServer` | `privatelink.database.windows.net` |
| Cosmos DB (SQL) | `Sql` | `privatelink.documents.azure.com` |
| Container Registry | `registry` | `privatelink.azurecr.io` |
| Service Bus | `namespace` | `privatelink.servicebus.windows.net` |
| App Configuration | `configurationStores` | `privatelink.azconfig.io` |

[Verify DNS zone names at build — they change with new service regions and sub-resources.]

## 4. Hub DNS Zone Architecture

In hub-spoke topologies, Private DNS zones live in the **hub** subscription and are linked to the hub VNet. Spoke VNets resolve via the hub DNS (Azure Resolver 168.63.129.16). Do NOT create duplicate zones per spoke.

```
Hub VNet ──── DNS Zone: privatelink.vaultcore.azure.net
              DNS Zone: privatelink.blob.core.windows.net
Spoke VNet ── VNet Link to hub zones (autoRegistration: false)
```

## 5. NSG Rules for Private Endpoint Subnets

Private Endpoint subnets require `PrivateEndpointNetworkPolicies: Disabled` on the subnet. NSG rules apply to the subnet's traffic:

```bicep
// Allow inbound from app subnet to PE subnet on service port
{
  name: 'Allow-AppSubnet-to-PE'
  properties: {
    priority: 100
    direction: 'Inbound'
    access: 'Allow'
    protocol: 'Tcp'
    sourceAddressPrefix: appSubnetPrefix
    destinationPortRange: '443'
  }
}
```

## 6. Disable-Public-Access Checklist

- [ ] `publicNetworkAccess: 'Disabled'` on Key Vault, Storage, SQL, Cosmos
- [ ] `allowBlobPublicAccess: false` on Storage
- [ ] `allowSharedKeyAccess: false` on Storage (force Entra/Managed Identity auth)
- [ ] `networkAcls.defaultAction: 'Deny'` with `bypass: 'AzureServices'` where needed
- [ ] No `0.0.0.0/0` in any firewall rule
- [ ] Defender for Cloud "Restrict public access" recommendations resolved

## Pitfalls

- Creating Private DNS Zones per spoke instead of centralizing in the hub — results in split-brain DNS
- Forgetting `PrivateEndpointNetworkPolicies: Disabled` on the subnet — Private Endpoint won't acquire its IP
- Leaving `publicNetworkAccess: 'Enabled'` after adding a Private Endpoint — the endpoint is additive, not exclusive, unless public access is explicitly disabled
- Using IP-based firewall rules as a substitute for Private Endpoints — IPs rotate; Private Endpoints don't

## See Also

- [`../../agents/network-engineer.md`](../../agents/network-engineer.md) — hub-spoke/vWAN topology and firewall/egress design
- [`../../agents/azure-architect.md`](../../agents/azure-architect.md) — landing zone and subscription topology
- [`../../CLAUDE.md`](../../CLAUDE.md) — house opinion: private-by-default for PaaS data planes
