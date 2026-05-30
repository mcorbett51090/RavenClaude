# Make prod zone-redundant by default; paired-region for BCDR

**Status:** Pattern — strong default for prod; single-zone prod needs a written reason tied to cost or a no-AZ region.

**Domain:** Compute / Reliability

**Applies to:** `azure-cloud`

---

## Why this exists

A single-zone prod deployment takes a datacenter-level outage as a full outage — and the fix is usually free or near-free. An **availability zone** is a physically isolated datacenter within a region; a **zone-redundant** resource spreads instances across zones so a single-zone failure doesn't take the workload down. For many services (Container Registry, VPN/ER gateways on AZ SKUs, App Gateway v2, Service Bus Premium, zone-redundant storage) zone redundancy is **automatic in AZ-supporting regions at no extra cost**; for others it's a SKU/instance-count requirement (App Gateway v2 needs ≥2 instances; Functions Flex Consumption AZ needs **≥2 always-ready instances**). House opinion #8 is "zone-redundant by default for prod." Zone redundancy protects against a *zone* outage; surviving a whole-*region* outage is a separate, deliberate choice — **paired-region** BCDR (replicate to the region's geo-pair) sized to your RTO/RPO.

## How to apply

Pick AZ-capable SKUs for prod and set zone redundancy where it's a flag; for stateful tiers, add geo-replication / backup to the paired region per RTO/RPO.

```bicep
// Zone-redundant App Service plan (prod)
resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  sku: { name: 'P1v3', tier: 'PremiumV3', capacity: 3 }
  properties: { zoneRedundant: true }        // spread across zones
}

// Zone-redundant storage; geo-redundant variant replicates to the paired region
resource sa 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: saName
  location: location
  sku: { name: 'Standard_ZRS' }              // ZRS = zone-redundant; GZRS adds paired-region geo
  kind: 'StorageV2'
}
```

**Do:**
- Choose **AZ-capable SKUs** for prod and set `zoneRedundant: true` (or the per-service flag); meet instance-count minimums (App Gateway v2 ≥2; Functions Flex Consumption AZ ≥2 always-ready).
- Use **ZRS/GZRS** for storage prod data; zone-redundant gateways/firewall/Front Door (often free on supported SKUs).
- Size **BCDR separately**: replicate stateful tiers to the **paired region** (GRS auto-replicates; SQL active geo-replication) per RTO/RPO; back up + ASR for VMs.

**Don't:**
- Ship single-zone prod by default — a datacenter blip becomes a full outage for free-to-avoid reasons.
- Conflate zone redundancy (survive a zone) with region failover (survive a region) — they're different controls; you usually want both for prod.
- Assume every region has AZs — some don't; if AZ isn't available, that's a region-selection input, not a reason to skip reliability planning.

## Edge cases / when the rule does NOT apply

- **Dev/test/sandbox** doesn't need zone redundancy — it's a prod posture; paying for AZ in sandbox is waste.
- **Regions without availability zones** can't be made zone-redundant — pick an AZ-supporting region during region selection, or accept the lower SLA explicitly.
- **Cross-zone latency-sensitive** workloads may pin to a single zone deliberately — Microsoft flags this as recommended only when you've verified cross-zone latency is the problem; pair zonal pins with multi-zone failover.
- **Brazil South** is the one regional pair spanning a geography boundary — a data-residency factor in BCDR region choice.

## See also

- [`../knowledge/azure-compute-decision-tree.md`](../knowledge/azure-compute-decision-tree.md) — per-service prod floor (incl. Functions AZ ≥2 always-ready)
- [`../knowledge/azure-landing-zones-and-governance.md`](../knowledge/azure-landing-zones-and-governance.md) — reliability/BCDR (zone-redundant vs paired-region per RTO/RPO)
- [`./compute-data-residency-drives-region-selection.md`](./compute-data-residency-drives-region-selection.md) — region/geography choice that gates AZ + paired-region
- [`../agents/azure-architect.md`](../agents/azure-architect.md) · [`../agents/app-platform-engineer.md`](../agents/app-platform-engineer.md)

## Provenance

Codifies house opinion #8 from [`../CLAUDE.md`](../CLAUDE.md) §3 and the §4 anti-pattern (single-zone prod). Grounded in Microsoft Learn [What are availability zones?](https://learn.microsoft.com/azure/reliability/availability-zones-overview), the per-service reliability guides (ACR/App Gateway v2/gateways auto-ZR on supported SKUs; instance-count minimums), and [paired regions](https://learn.microsoft.com/azure/reliability/cross-region-replication-azure) (geo-pair within a geography, Brazil South exception, GRS auto-replication) — retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
