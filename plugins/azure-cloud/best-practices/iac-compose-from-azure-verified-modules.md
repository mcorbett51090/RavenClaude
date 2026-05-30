# Compose from Azure Verified Modules — pin versions, don't hand-roll resources

**Status:** Pattern — strong default; a hand-authored resource where a published AVM exists needs a written reason.

**Domain:** IaC

**Applies to:** `azure-cloud`

---

## Why this exists

Every team that hand-authors a Storage account, a Key Vault, or a VNet from raw resource declarations re-discovers the same WAF defaults (diagnostic settings, private endpoints, RBAC, zone-redundancy) the hard way — usually by shipping one without them. **Azure Verified Modules (AVM)** are Microsoft-maintained, WAF-aligned, versioned modules for **both Bicep and Terraform** that bake those defaults in, including the ALZ accelerator and subscription-vending modules. House opinion #3 is "AVM either way." Composing from AVM means the secure defaults are the *starting* point, the module is patched centrally when a CVE or new best-practice lands, and your IaC is a thin layer of intent over a vetted building block. The discipline that makes this safe: **pin a specific version** (`br/public:avm/res/...:0.x.y`) so a module bump is a reviewed PR, never a surprise on the next deploy.

## How to apply

Reference the public AVM registry, pin the version, and pass only your intent. Let the module's secure defaults stand unless you have a reason to override.

```bicep
// Bicep — pinned AVM resource module (note the explicit version tag)
module kv 'br/public:avm/res/key-vault/vault:0.9.0' = {
  name: 'kv-deploy'
  params: {
    name: kvName
    enableRbacAuthorization: true
    publicNetworkAccess: 'Disabled'        // private-by-default still applies
    diagnosticSettings: [ { workspaceResourceId: lawId } ]   // wired from day one
  }
}
```

```hcl
# Terraform — pin the AVM module version the same way
module "key_vault" {
  source  = "Azure/avm-res-keyvault-vault/azurerm"
  version = "0.9.0"   # pinned, not "~> 0.9" — a bump is a reviewed change
}
```

**Do:**
- Default to the published **AVM** for a resource; check the registry before hand-authoring.
- **Pin an exact version** and bump it through a PR (so the change set shows in `what-if`/`plan`).
- Keep the **secure defaults** the module ships (private endpoints, diagnostics, RBAC) unless overriding for a documented reason.
- Use the **ALZ accelerator** + **subscription-vending** AVM modules for the platform foundation rather than re-implementing the management-group tree.

**Don't:**
- Float to a range (`~>`, `latest`) on shared infra — an unreviewed module bump can change defaults under you.
- Fork an AVM to tweak one property when a module parameter already exposes it.
- Re-author a Storage/Key Vault/VNet from raw resources "to keep it simple" — you'll re-derive the WAF defaults and miss some.

## Edge cases / when the rule does NOT apply

- **No AVM exists** for the resource/feature yet — hand-author it, follow the AVM interface conventions (diagnostics, RBAC, private-endpoint params) so it's swappable later.
- **A bug or missing parameter in the module** can justify a temporary raw resource or a pinned fork — track it as a migration item back onto AVM.
- **Highly bespoke resources** (a one-off with no reuse) may not warrant module overhead — but the common building blocks always do.

## See also

- [`../knowledge/azure-iac-decision-and-bicep.md`](../knowledge/azure-iac-decision-and-bicep.md) — AVM for both Bicep + Terraform, ALZ accelerator + vending modules
- [`./iac-what-if-before-every-deploy.md`](./iac-what-if-before-every-deploy.md) — previewing the version bump
- [`./lz-flat-management-group-hierarchy.md`](./lz-flat-management-group-hierarchy.md) — stamped by the ALZ-accelerator + vending AVM modules
- [`../agents/bicep-iac-engineer.md`](../agents/bicep-iac-engineer.md) — owns AVM composition

## Provenance

Codifies house opinion #3 (AVM either way) from [`../CLAUDE.md`](../CLAUDE.md) §3. Grounded in Microsoft Learn / AVM spec [SNFR25 resource-naming + AVM module conventions](https://azure.github.io/Azure-Verified-Modules/) and the IaC knowledge file (retrieved 2026-05-30); the diagnostic-settings `workspaceResourceId` + private-by-default defaults confirmed against the AVM module READMEs.

---

_Last reviewed: 2026-05-30 by `claude`_
