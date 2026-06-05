# Use Bicep for Azure-only IaC, Terraform for multi-cloud or existing Terraform estates

**Status:** Pattern
**Domain:** Azure IaC
**Applies to:** `azure-cloud`

---

## Why this exists

Bicep and Terraform are both correct answers for Azure IaC — but in different contexts. Bicep is Azure-native: it compiles to ARM, supports every Azure resource on day-one GA, and has zero provider lag. Terraform's azurerm provider sometimes lags new Azure features by weeks or months. Bicep is the right choice when the estate is Azure-only and the team is not already running Terraform for other clouds. Terraform is the right choice when the estate is multi-cloud, when the team has an existing Terraform skill/toolchain investment, or when OpenTofu is required for licensing reasons. Picking randomly — or defaulting to Terraform "because everyone uses Terraform" in an Azure-only estate — means managing provider version lag and two toolchains unnecessarily.

## How to apply

**Decision:**

| Context | Pick |
|---|---|
| Azure-only estate, new project | Bicep + AVM modules |
| Multi-cloud estate (Azure + AWS or GCP) | Terraform/OpenTofu + azurerm provider |
| Existing Terraform estate, adding Azure | Terraform/OpenTofu to avoid a second tool |
| Azure + Kubernetes manifests | Bicep for Azure infra + Helm/Kustomize for manifests |
| Licensing constraint (no HashiCorp BSL) | OpenTofu + azurerm |

```bicep
// Bicep — Azure-only: Storage Account using AVM module
module storage 'br/public:avm/res/storage/storage-account:0.11.0' = {
  name: 'storage-${uniqueString(resourceGroup().id)}'
  params: {
    name: 'st${appName}${env}'
    location: location
    skuName: 'Standard_ZRS'           // Zone-redundant for prod
    publicNetworkAccess: 'Disabled'   // private-by-default
    privateEndpoints: [
      {
        service: 'blob'
        subnetResourceId: privateEndpointSubnet.id
        privateDnsZoneResourceIds: [ blobDnsZone.id ]
      }
    ]
    managedIdentities: { systemAssigned: true }
  }
}
```

```hcl
# Terraform — multi-cloud: same storage account for reference
module "storage" {
  source  = "Azure/avm-res-storage-storageaccount/azurerm"
  version = "~> 0.2"

  name                = "st${var.app_name}${var.env}"
  resource_group_name = azurerm_resource_group.this.name
  location            = var.location
}
```

**Do:**
- Use AVM (Azure Verified Modules) in both Bicep and Terraform — they ship the WAF-compliant defaults.
- Commit the Bicep `.bicepparam` and Terraform `.tfvars` per environment; don't mix paradigms in the same repo.
- Run `az bicep build` or `terraform validate` in CI before `az deployment what-if` or `terraform plan`.
- Use Deployment Stacks (Bicep) or Terraform state isolation for lifecycle management.

**Don't:**
- Mix Bicep and Terraform for the same resource type in the same environment — pick one per scope.
- Hand-author Bicep modules where an AVM module exists — resource parity and WAF defaults come for free.
- Choose Terraform for an Azure-only estate solely because the team "has heard of it."

## Edge cases / when the rule does NOT apply

- **Azure Arc-enabled Kubernetes**: Bicep can provision Arc resources; Kubernetes manifests are still Helm/Kustomize.
- **Pulumi or CDK for Azure**: valid alternatives for teams with strong TypeScript/Python experience — this rule governs the Bicep-vs-Terraform choice for the more common declarative HCL/ARM path.

## See also

- [`../agents/bicep-iac-engineer.md`](../agents/bicep-iac-engineer.md) — owns Bicep + Terraform authoring and AVM module selection.
- [`./iac-compose-from-azure-verified-modules.md`](./iac-compose-from-azure-verified-modules.md) — AVM is the module layer regardless of whether Bicep or Terraform is the host language.
- [`./iac-what-if-before-every-deploy.md`](./iac-what-if-before-every-deploy.md) — what-if/plan applies to both tools before apply.

## Provenance

Codifies house opinion #3 from `CLAUDE.md` §3: "Bicep for Azure-only, Terraform for multi/hybrid-cloud; AVM either way; Deployment Stacks." Grounded in `knowledge/azure-iac-decision-and-bicep.md`.

---

_Last reviewed: 2026-06-05 by `claude`_
