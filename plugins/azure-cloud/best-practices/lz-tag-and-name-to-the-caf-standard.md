# Tag + name to the CAF standard — names carry only what's permanent, tags carry the rest

**Status:** Pattern — strong default; ad-hoc names and missing tags make an estate un-attributable and un-automatable.

**Domain:** Landing Zones / Governance

**Applies to:** `azure-cloud`

---

## Why this exists

Two facts make naming and tagging a day-one decision, not a cleanup task. First, **Azure resource names can't be changed after creation** — so a name must encode only what is *permanent* (resource type, workload, environment, region, instance), and everything mutable (owner, cost-center, lifecycle) belongs in **tags**, which *can* change. Second, without enforced tags an estate is **un-attributable** — you can't do chargeback, you can't find the owner of a runaway resource, you can't automate by metadata. CAF gives the standard: a naming convention `{abbr}-{workload}-{env}-{region}-{instance}` (e.g. `rg-payments-prod-eastus-001`) using the **documented Azure resource abbreviations**, plus a baseline **tag set** (`owner` / `cost-center` / `environment` / `application`). House opinion #9 names both. Mind the per-resource **name rules** (length, allowed characters — some resources forbid hyphens, some cap at 24 chars like Storage).

## How to apply

Derive names from the CAF abbreviation + components in IaC; enforce the tag set with policy. Don't encode mutable facts in the name.

```bicep
// Name = permanent facts only, built from CAF components; tags carry the mutable ones
param workload string = 'payments'
param env string = 'prod'
param region string = 'eastus'
param instance string = '001'

var rgName = 'rg-${workload}-${env}-${region}-${instance}'   // rg-payments-prod-eastus-001
var commonTags = {
  owner: 'team-payments'
  'cost-center': 'CC-4187'
  environment: env
  application: workload
}

resource sa 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  // Storage: 3-24 chars, lowercase alphanumeric, NO hyphens — abbreviations adapt per-resource rules
  name: 'st${workload}${env}${region}${instance}'
  location: region
  tags: commonTags
  sku: { name: 'Standard_ZRS' }
  kind: 'StorageV2'
}
```

**Do:**
- Name with the CAF pattern `{abbr}-{workload}-{env}-{region}-{instance}` using the **documented abbreviations** (`rg-`, `st`, `kv-`, `vnet-`, `pep-`, …).
- Encode only **permanent** facts in the name; put **mutable** facts (owner, cost-center) in **tags**.
- Apply the baseline **tag set** (`owner`/`cost-center`/`environment`/`application`) and **enforce it with policy** (`Modify`/`Append`/`deny`-untagged).
- Respect **per-resource name rules** — length and character constraints differ (Storage 3–24 lowercase no-hyphen; many others allow hyphens).

**Don't:**
- Bake a mutable fact (owner, team, cost-center) into a **name** — you can't change the name when it changes.
- Skip tags and plan to "add them later" — un-tagged resources are un-attributable for chargeback.
- Rely on **subscription-scope tags as a security boundary** — elevated users can mutate them.

## Edge cases / when the rule does NOT apply

- **Resources with tight name rules** (Storage, Key Vault, ACR) can't take the full hyphenated pattern — adapt the abbreviation form to the rules; the *components* stay the same.
- **Globally-unique names** (Storage, public DNS) may need a hash/suffix for uniqueness — append it, keep the readable prefix.
- **Management groups / subscriptions** often carry department info that workload resources don't — CAF expects the convention to flex per resource type, not be identical everywhere.
- **No documented abbreviation** for a resource → pick a sensible stable prefix (AVM does the same).

## See also

- [`../knowledge/azure-landing-zones-and-governance.md`](../knowledge/azure-landing-zones-and-governance.md) — CAF tags + naming, subscription vending
- [`./cost-budgets-tags-and-policy-guardrails.md`](./cost-budgets-tags-and-policy-guardrails.md) — enforcing the tag set + chargeback
- [`./gov-azure-policy-as-guardrails.md`](./gov-azure-policy-as-guardrails.md) — the policy that enforces required tags
- [`../agents/azure-architect.md`](../agents/azure-architect.md) · [`../agents/azure-ops-engineer.md`](../agents/azure-ops-engineer.md)

## Provenance

Codifies house opinion #9 from [`../CLAUDE.md`](../CLAUDE.md) §3. Grounded in Microsoft Learn CAF [define your naming convention](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming) (names are immutable; `{abbr}-{workload}-{env}-{region}-{instance}`), [resource abbreviations](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/resource-abbreviations), [define your tagging strategy](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/resource-tagging), and [resource name rules](https://learn.microsoft.com/azure/azure-resource-manager/management/resource-name-rules) — retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
