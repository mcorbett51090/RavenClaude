# Choose hub-spoke vs Virtual WAN by scale and management appetite — not by habit

**Status:** Pattern — strong default; pick the topology from the connectivity decision, not from what the team built last.

**Domain:** Networking / Architecture

**Applies to:** `azure-cloud`

---

## Why this exists

The connectivity subscription's topology is a one-way door — re-platforming hub-to-vWAN (or back) on a live estate is expensive — so it's worth getting from the decision, not from habit. Two patterns dominate. **Classic hub-spoke** is a self-managed hub VNet holding shared services (Azure Firewall, DNS, gateways) with workload spokes peered to it: maximum control, and the right call when there are a handful of regions and the team wants to own the routing. **Azure Virtual WAN** is a Microsoft-managed hub that absorbs the transit routing, branch/VPN/ExpressRoute aggregation, and any-to-any connectivity at scale: the right call for **global, many-region, many-branch** estates where hand-managing peering meshes and route tables becomes the bottleneck. The lever is **scale + how much of the transit plumbing you want Microsoft to manage**, not familiarity.

## How to apply

Traverse the network-topology decision tree (in [`../knowledge/azure-decision-trees.md`](../knowledge/azure-decision-trees.md)) before committing. Single-region, simple → one well-segmented VNet; classic, control-heavy → hub-spoke; global/many-region/many-branch → vWAN.

```text
Single region, few subnets, no on-prem mesh        -> single segmented VNet (NSGs + PE subnet)
Few regions, want to own routing + shared services -> classic hub-spoke (self-managed hub)
Global, many regions/branches, VPN/ER aggregation  -> Azure Virtual WAN (managed hub)
```

```bicep
// Hub-spoke: spoke peered to the hub, using the hub's gateway + firewall
resource peer 'Microsoft.Network/virtualNetworks/virtualNetworkPeerings@2023-11-01' = {
  name: '${spokeVnetName}/to-hub'
  properties: {
    remoteVirtualNetwork: { id: hubVnetId }
    allowForwardedTraffic: true
    useRemoteGateways: true        // spoke uses the hub's VPN/ER gateway
  }
}
```

**Do:**
- Start from the **decision tree**; name the observable that resolved (region count, branch/VPN aggregation need, management appetite).
- Put **shared services in the hub** (firewall, DNS, gateways) either way; spokes are workload VNets.
- Choose **vWAN** when transit routing / branch aggregation at scale is the pain; choose **hub-spoke** when control and a small footprint are the priority.
- Make hub **gateways/firewall zone-redundant** for prod (house opinion #8).

**Don't:**
- Default to whichever the team built last — the wrong one is costly to unwind on a live estate.
- Reach for vWAN for a single-region two-spoke estate (managed-hub overhead you don't need), or hand-manage a global mesh that vWAN would absorb.

## Edge cases / when the rule does NOT apply

- **A single-region, all-PaaS workload** may need neither — one segmented VNet (or no VNet at all) is enough; don't stand up a hub for a hub's sake.
- **An existing hub-spoke** with amortized investment may absorb a new region more cheaply than migrating to vWAN — brownfield weighs the sunk platform.
- **Regulatory isolation** can force a separate connectivity boundary regardless of scale — that's a policy boundary, not a topology preference.
- The topology + firewall/peering **security design** routes to `ravenclaude-core/security-reviewer`.

## See also

- [`../knowledge/azure-decision-trees.md`](../knowledge/azure-decision-trees.md) — `## Decision Tree: Network Topology`
- [`../knowledge/azure-networking-and-connectivity.md`](../knowledge/azure-networking-and-connectivity.md) — hub-spoke / vWAN, edge/ingress, egress
- [`./network-segment-subnets-with-nsgs-and-forced-egress.md`](./network-segment-subnets-with-nsgs-and-forced-egress.md) — the spoke-internal segmentation
- [`../agents/network-engineer.md`](../agents/network-engineer.md) · [`../agents/azure-architect.md`](../agents/azure-architect.md)

## Provenance

Codifies the topology choice in [`../knowledge/azure-networking-and-connectivity.md`](../knowledge/azure-networking-and-connectivity.md) (hub-spoke vs Virtual WAN — Microsoft Learn CAF connectivity, retrieved 2026-05-28; re-confirmed against the CAF network-topology-and-connectivity design area, 2026-05-30).

---

_Last reviewed: 2026-05-30 by `claude`_
