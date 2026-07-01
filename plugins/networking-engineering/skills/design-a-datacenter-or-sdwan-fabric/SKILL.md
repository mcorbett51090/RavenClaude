---
name: design-a-datacenter-or-sdwan-fabric
description: Design a data-center fabric (spine-leaf underlay + VXLAN/EVPN overlay) or an SD-WAN/WAN-edge topology (transports, underlay policy, overlay tunnels, failover, application steering). Returns the underlay + overlay design, the redundancy/failover behavior, and the scaling story. Used by `network-architect` (primary).
---

# Skill: design-a-datacenter-or-sdwan-fabric

> **Invoked by:** `network-architect` (primary).
>
> **When to invoke:** "design a spine-leaf fabric"; "we need VXLAN/EVPN"; "design our SD-WAN"; "how do we connect these sites over the WAN?".
>
> **Output:** an underlay + overlay design (DC) or a transport + tunnel + steering design (SD-WAN), plus the failover behavior and scaling limits.

## Procedure — data center (spine-leaf)

1. **Underlay first.** A CLOS spine-leaf where every leaf connects to every spine, no leaf-to-leaf or spine-to-spine. Routed underlay (eBGP, one ASN per device, or OSPF for small fabrics) carries only loopback reachability for the overlay tunnel endpoints. ECMP across spines is the point.
2. **Overlay for tenancy and L2 stretch.** VXLAN provides the L2-over-L3 transport; **EVPN** (BGP address-family) is the control plane that distributes MAC/IP reachability, replacing flood-and-learn. VTEPs on the leaves; spines stay L3-only.
3. **Size the fabric.** Oversubscription ratio (leaf uplink : downlink), spine count = the ECMP width and the failure-domain math, port counts, and the growth unit (add a leaf pair, add a spine). State the scale ceiling.
4. **Place the border and services.** Border leaves for external/WAN connectivity, service leaves for firewalls/LBs; decide where inter-tenant routing and the default gateway (anycast/distributed) live.

## Procedure — SD-WAN / WAN edge

1. **Inventory the transports.** MPLS, broadband, LTE/5G — each a path with cost, latency, and reliability characteristics. The overlay abstracts them into policy.
2. **Build the overlay.** Encrypted tunnels (IPsec) between edges over every transport, a controller/orchestrator for policy, and an underlay-independent addressing/routing plane.
3. **Define application-aware steering + failover.** Per-application path selection (SLA classes: loss/latency/jitter thresholds), brownout/blackout detection, and deterministic failover order. State what happens when the primary transport degrades vs fails.
4. **Set the security posture at the edge.** Segmentation carried across the overlay; the appsec *verdict* on the edge policy routes to `security-engineering`.

## Quick map

| Goal | Choice | Why |
|---|---|---|
| Non-blocking, horizontally-scalable DC | Spine-leaf CLOS | Predictable latency + ECMP + simple growth |
| L2 stretch / multi-tenancy in the fabric | VXLAN + EVPN control plane | Scales past flood-and-learn; MP-BGP distributes reachability |
| Small fabric, few tenants | Consider L3-only / simpler overlay | EVPN earns its complexity at scale, not below it |
| Multi-transport WAN with app SLAs | SD-WAN overlay | Transport-independent policy + app-aware failover |

## Guardrails
- **Don't stretch L2 further than you must** — a fabric-wide L2 domain is a fabric-wide blast radius; prefer routed + anycast gateway.
- **EVPN/SD-WAN capabilities are vendor- and version-specific and volatile** — verify against the platform and cite a retrieval date ([`../../knowledge/networking-tooling-2026.md`](../../knowledge/networking-tooling-2026.md)).
- **State the oversubscription ratio** — an undocumented one becomes a mystery bottleneck.
- **Failover must be deterministic and tested**, not "the tunnels will figure it out."
