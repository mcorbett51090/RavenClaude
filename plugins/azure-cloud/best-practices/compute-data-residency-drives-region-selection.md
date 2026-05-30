# Let data residency and the paired region drive region selection — pick the geography first

**Status:** Pattern — strong default; choosing a region by latency/cost alone, before checking the residency boundary and its geo-pair, is a re-platform waiting to happen.

**Domain:** Architecture / Compliance

**Applies to:** `azure-cloud`

---

## Why this exists

Region is one of the hardest things to change after the fact — resources can't be moved between regions, and data already at rest carries compliance weight. Teams routinely pick a region for **latency** or **price** and only later discover it violates a **data-residency** requirement, or that its **paired region** (where GRS backups and BCDR land) sits in a different country. In Azure, a **geography** is the data-residency boundary (e.g. "United States," "Europe"); a **region** lives inside exactly one geography; and most regional services keep data at rest within that geography. Paired regions are (with the lone exception of **Brazil South**) within the same geography — which is *why* GRS and paired-region DR satisfy residency. So the correct order is: **establish the residency/sovereignty boundary → pick a geography → pick a region inside it that has availability zones and an acceptable paired region → then optimize latency/cost** within those constraints.

## How to apply

Resolve residency first (the decision tree in [`../knowledge/azure-decision-trees.md`](../knowledge/azure-decision-trees.md)), then choose a region with AZs and a compliant pair, then tune for latency/cost.

```text
1. Residency boundary?  -> the required geography (US / EU / sovereign cloud / specific country)
2. AZ support?          -> prefer a region IN that geography that has availability zones (house opinion #8)
3. Paired region?       -> confirm the geo-pair is also inside the compliant geography (mind Brazil South)
4. Latency / cost / service availability -> optimize WITHIN the above; verify the service exists in-region
```

```bicep
// Region is a parameter, never hardcoded — residency drives the value passed in
@allowed([ 'eastus', 'westeurope', 'northeurope' ])   // constrained to compliant geographies
param location string
// GRS storage will auto-replicate to this region's PAIRED region — confirm it's in-geography
resource sa 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: saName
  location: location
  sku: { name: 'Standard_GZRS' }    // geo + zone redundant; pair must satisfy residency
  kind: 'StorageV2'
}
```

**Do:**
- Establish the **residency/sovereignty boundary** before naming a region; constrain `location` to compliant geographies.
- Confirm the chosen region has **availability zones** and that its **paired region** is inside the compliant geography (watch **Brazil South**).
- Check the **service is available in-region** (a few regions only carry a subset) and whether any **non-regional** services (Entra ID, Traffic Manager, CDN) store data outside the geography.
- Optimize **latency/cost only within** the residency-valid set.

**Don't:**
- Pick a region by ping time or price first, then retrofit compliance — region moves are re-platforms.
- Assume GRS keeps data in-country without checking the geo-pair (Brazil South is the exception).
- Hardcode a region in IaC — parameterize it so the residency constraint is enforced at the boundary.

## Edge cases / when the rule does NOT apply

- **Sovereign clouds** (Azure Government, 21Vianet) are separate geographies with reduced service sets — verify service availability *and* feature parity, not just presence.
- **Non-regional services** (Entra ID, Azure DNS, Front Door, CDN) don't honor a single region by design — exclude sensitive customer content from edge caches and treat identity data per its own residency rules.
- **Multi-geo** apps store data per-geo deliberately — that's residency-by-design, not an exception.
- The cross-domain residency/sovereignty *architecture* (spanning non-Azure systems) → `ravenclaude-core/architect`.

## See also

- [`../knowledge/azure-decision-trees.md`](../knowledge/azure-decision-trees.md) — `## Decision Tree: Region / Data Residency Selection`
- [`./compute-zone-redundant-by-default-for-prod.md`](./compute-zone-redundant-by-default-for-prod.md) — AZ + paired-region reliability that region choice gates
- [`../knowledge/azure-landing-zones-and-governance.md`](../knowledge/azure-landing-zones-and-governance.md) — reliability/BCDR + CAF region guidance
- [`../agents/azure-architect.md`](../agents/azure-architect.md) — owns region/residency

## Provenance

Grounded in Microsoft Learn [What are Azure regions?](https://learn.microsoft.com/azure/reliability/regions-overview) (geography = residency boundary; region inside one geography; sovereign clouds), [paired regions](https://learn.microsoft.com/azure/architecture/aws-professional/regions-zones#paired-regions) (pairs within a geography; Brazil South exception; GRS auto-backup to the pair), and [data residency / public-sector](https://learn.microsoft.com/azure/azure-government/documentation-government-overview-wwps) (regional vs non-regional services, Entra ID) — retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
