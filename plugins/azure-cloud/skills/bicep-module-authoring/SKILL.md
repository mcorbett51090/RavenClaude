---
name: bicep-module-authoring
description: "Playbook for writing production-ready Bicep modules — parameter hygiene, AVM alignment, what-if verification, output contracts, and the CI/CD integration checklist. Covers both standalone and AVM-wrapper patterns."
---

# Bicep Module Authoring

## When to Use This Skill

Use when writing a new Bicep module from scratch, wrapping an AVM module with project-specific defaults, or reviewing a module before it enters a shared library.

## 1. Module Skeleton

```bicep
// modules/storage-account/main.bicep
@description('Name of the Storage Account (3-24 chars, lowercase alphanumeric).')
param name string

@description('Azure region for the resource.')
param location string = resourceGroup().location

@description('Environment tag value (dev|test|prod).')
@allowed(['dev', 'test', 'prod'])
param environment string

@description('Resource tags merged with the required set.')
param tags object = {}

var requiredTags = {
  environment: environment
  managedBy: 'bicep'
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: name
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  tags: union(requiredTags, tags)
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    publicNetworkAccess: 'Disabled'
    supportsHttpsTrafficOnly: true
  }
}

@description('Resource ID of the Storage Account.')
output resourceId string = storageAccount.id

@description('Name of the Storage Account.')
output name string = storageAccount.name
```

## 2. Parameter Hygiene Rules

| Rule | Detail |
|---|---|
| Decorate every parameter | `@description`, `@allowed`, `@minLength`/`@maxLength` where applicable |
| No secrets as parameters | Passwords, keys, connection strings → Key Vault reference or Managed Identity |
| No hardcoded subscription/tenant GUIDs | Use `subscription().subscriptionId` / `tenant().tenantId` |
| Required vs optional | Required params have no default; optional ones do — be explicit |
| Naming | camelCase for params/vars, PascalCase for resource symbolic names |

## 3. AVM Alignment

```bicep
// Prefer an AVM module over a raw resource when one exists [verify-at-build]
module storageAccount 'br/public:avm/res/storage/storage-account:0.9.0' = {
  name: 'storageAccountDeployment'
  params: {
    name: name
    location: location
    skuName: 'Standard_LRS'
    allowBlobPublicAccess: false
    publicNetworkAccessEnabled: false
    tags: tags
  }
}
```

Check the AVM registry at `aka.ms/avm` before writing a raw resource block.

## 4. What-If Before Apply

```bash
# Validate and preview changes — never skip this in a pipeline
az deployment group what-if \
  --resource-group rg-myapp-prod-eastus \
  --template-file main.bicep \
  --parameters @params.prod.json \
  --result-format FullResourcePayloads
```

Gate the apply step on human approval for `prod` environments; auto-apply is acceptable for `dev`/`test`.

## 5. Output Contract

Every module must export:
- `resourceId` — used by dependent modules to construct dependencies
- `name` — used by deployment scripts and observability config
- Role-specific outputs (e.g. `primaryEndpoint` for Storage, `fqdn` for App Service)

Never output secrets or connection strings. Reference Key Vault from the consuming module.

## 6. CI/CD Pipeline Gate Checklist

- [ ] `az bicep build` — compiles and validates syntax
- [ ] `az deployment group validate` — ARM schema validation (catches type mismatches)
- [ ] `az deployment group what-if` — diff review gate before apply
- [ ] Policy compliance check (`az policy state trigger-scan`) in pre-prod
- [ ] Deployment Stacks (not classic RG deployments) for managed lifecycle + `DenySettings`

## 7. Deployment Stacks Pattern

```bash
az stack group create \
  --name myapp-prod \
  --resource-group rg-myapp-prod-eastus \
  --template-file main.bicep \
  --parameters @params.prod.json \
  --deny-settings-mode DenyWriteAndDelete \
  --action-on-unmanage DetachAll
```

Deployment Stacks tracks all resources in the deployment and enforces `DenySettings` — the replacement for Blueprints. [verify-at-build]

## Pitfalls

- Outputting a connection string or storage key — use Managed Identity or Key Vault reference instead
- Writing a raw `Microsoft.*` resource block when an AVM module exists — duplicates maintenance burden
- Skipping `what-if` and applying directly — produces undocumented drift
- Using `Contributor` or `Owner` role assignments at subscription scope in a module — the anti-patterns hook flags these
- Hard-coding the API version as `@latest` — lock to a specific version to prevent silent schema changes

## See Also

- [`../../agents/bicep-iac-engineer.md`](../../agents/bicep-iac-engineer.md) — Bicep vs Terraform decision, Deployment Stacks, CI/CD pipeline
- [`../../agents/azure-architect.md`](../../agents/azure-architect.md) — landing zone and subscription topology
- [`../../CLAUDE.md`](../../CLAUDE.md) — house opinions on IaC and passwordless defaults
