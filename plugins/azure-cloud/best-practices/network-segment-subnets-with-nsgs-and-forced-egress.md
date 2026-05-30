# Segment VNets by tier, NSG every subnet, force egress through the firewall

**Status:** Pattern — strong default for any VNet carrying a real workload; a flat, NSG-less VNet needs a written reason.

**Domain:** Networking / Security

**Applies to:** `azure-cloud`

---

## Why this exists

`private-by-default-paas-data-planes` locks down the PaaS *data planes*; this rule covers the **VNet that the compute sits in**. A single flat subnet with no NSGs and unrestricted internet egress is the network equivalent of running everything as root: any compromised pod or VM can talk to anything, in or out, and the only egress audit trail is "it went to the internet." The CAF/WAF posture is **segment by tier** (web / app / data, plus delegated subnets for PaaS like Container Apps environments and App Service VNet integration), put an **NSG on every subnet** (default-deny inbound, allow only the flows you need), and **force all egress through a central firewall** with a UDR so outbound traffic is logged and allow-listed — not silently open. This composes with the hub-spoke topology: the firewall lives in the hub, spokes route through it.

## How to apply

Give each tier its own subnet with an NSG; add a route table that sends `0.0.0.0/0` to the hub firewall so egress is inspected, not direct.

```bicep
resource appNsg 'Microsoft.Network/networkSecurityGroups@2023-11-01' = {
  name: 'nsg-app-prod-eastus'
  location: location
  properties: { securityRules: [
    { name: 'allow-from-web-tier', properties: {
        priority: 100, direction: 'Inbound', access: 'Allow', protocol: 'Tcp',
        sourceAddressPrefix: '10.10.1.0/24', destinationPortRange: '443',
        sourcePortRange: '*', destinationAddressPrefix: '*' } }
    // implicit DenyAllInbound (priority 65500) does the rest — default-deny
  ] }
}

resource egressViaFirewall 'Microsoft.Network/routeTables@2023-11-01' = {
  name: 'rt-app-forced-egress'
  location: location
  properties: { routes: [ {
    name: 'default-to-hub-firewall'
    properties: { addressPrefix: '0.0.0.0/0', nextHopType: 'VirtualAppliance',
                  nextHopIpAddress: hubFirewallPrivateIp } } ] }   // not direct to internet
}
```

**Do:**
- One **subnet per tier** (web/app/data) + **delegated** subnets for PaaS that needs VNet integration (Container Apps env, App Service, Private Endpoints).
- An **NSG on every subnet**, default-deny inbound, allow only the specific source/port flows; send NSG flow logs to Log Analytics.
- A **UDR** forcing `0.0.0.0/0` egress through the **hub Azure Firewall** (or NVA) so outbound is logged + allow-listed.
- Reserve a dedicated **Private Endpoint subnet** for the deny-public PaaS data planes.

**Don't:**
- Run a flat VNet with one big subnet and no NSGs — a compromise then has lateral free rein.
- Leave egress direct-to-internet — you lose the audit trail and the allow-list chokepoint.
- Put an NSG rule with `sourceAddressPrefix: '*'` on an inbound `Allow` to a data subnet — that's `0.0.0.0/0` by another name.

## Edge cases / when the rule does NOT apply

- **Fully-PaaS estates with no VNet** (Static Web Apps + serverless + private-endpoint'd data) may not need a hub firewall — but any PaaS with VNet integration still gets subnet NSGs.
- **Some PaaS-delegated subnets** restrict which NSG rules / UDRs apply (Container Apps, App Service integration have documented constraints) — follow the service's subnet requirements rather than forcing a generic rule.
- **Sandbox** VNets under the loose-policy archetype may skip forced egress — anything on a promotion path may not.
- Firewall rules, NSG posture, and egress allow-lists are **network-security design** → route to `ravenclaude-core/security-reviewer`.

## See also

- [`../knowledge/azure-networking-and-connectivity.md`](../knowledge/azure-networking-and-connectivity.md) — topology, NSGs, UDRs, Azure Firewall egress, the private-by-default section
- [`./private-by-default-paas-data-planes.md`](./private-by-default-paas-data-planes.md) — the Private Endpoint subnet this design reserves
- [`./network-hub-spoke-vs-virtual-wan.md`](./network-hub-spoke-vs-virtual-wan.md) — where the central firewall lives
- [`../agents/network-engineer.md`](../agents/network-engineer.md) — owns segmentation + egress

## Provenance

Codifies the CAF/WAF connectivity posture captured in [`../knowledge/azure-networking-and-connectivity.md`](../knowledge/azure-networking-and-connectivity.md) (segment by tier, NSGs on subnets, UDRs forcing egress through the hub firewall — Microsoft Learn, retrieved 2026-05-28; default-deny NSG semantics re-confirmed 2026-05-30).

---

_Last reviewed: 2026-05-30 by `claude`_
