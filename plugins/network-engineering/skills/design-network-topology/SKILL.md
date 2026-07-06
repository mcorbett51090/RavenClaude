---
name: design-network-topology
description: Design a campus/datacenter/branch/WAN network topology by traversing the topology decision tree (scale -> traffic pattern -> redundancy need -> topology), then return the recommended topology (collapsed-core vs 3-tier vs spine-leaf vs hub-and-spoke/SD-WAN), an IP addressing plan (summarizable, room to grow), the redundancy/failure model (HSRP/VRRP, dual-homing, MLAG), and a labelled diagram description. Reach for this when the user asks to "design the network for <site/DC>". Used by `network-architect` (primary).
---

# Skill: design-network-topology

> **Invoked by:** `network-architect` (primary).
>
> **When to invoke:** "design the network for our new office/datacenter/branch"; "what topology for <N> users / <traffic pattern>?"; any greenfield or refresh topology question.
>
> **Output:** topology recommendation + IP addressing plan + redundancy/failure model + diagram description + the trade-off named.

## Procedure

1. **Gather the inputs that actually drive the design** — don't design in a vacuum:
   - Scale: endpoints/users now and at 3-year growth.
   - Traffic pattern: north-south (client→server/internet) vs east-west (server↔server) dominant?
   - Sites: single site, campus, multi-site WAN, hybrid-cloud?
   - Availability target: what failure must be survived (a link? a switch? a site?).
   - Constraints: budget, existing vendor, existing addressing, regulatory segmentation (PCI/OT).
2. **Traverse the topology decision tree** in [`../../knowledge/network-topology-decision-trees.md`](../../knowledge/network-topology-decision-trees.md). The short form:
   - Small site (≤ ~2 switches, north-south traffic) → **collapsed-core** (core+distribution combined).
   - Larger campus, many access switches → **3-tier** (access / distribution / core).
   - Datacenter, east-west dominant, predictable latency → **spine-leaf (CLOS)**, usually with **VXLAN/EVPN** overlay.
   - Many branches to a few hubs → **hub-and-spoke**, modern form **SD-WAN** (transport-independent, policy-driven).
3. **Produce the IP addressing plan.** Allocate summarizable blocks per site/role (a /16 per site, /24 per VLAN is a common starting frame); leave headroom; reserve management and point-to-point ranges; document the plan — an undocumented IP plan means the network isn't designed.
4. **Specify the redundancy / failure model.** First-hop redundancy (HSRP/VRRP/GLBP), link aggregation (LACP), multi-chassis (MLAG/vPC/stacking), dual-homing, and for WAN dual-transport + SD-WAN failover. State explicitly: *what happens when each component dies.*
5. **Describe the diagram** (layers, devices, links, VLANs/segments, the redundancy paths). The architect renders it; you specify it.
6. **Name the trade-off and the rejected alternatives** — e.g., "spine-leaf rejected for a 30-user office: east-west is negligible and collapsed-core is a fraction of the cost."

## Output contract

```
Inputs: <scale / traffic / sites / availability / constraints>
Topology: <chosen> — because <decision-tree path>
Addressing: <summarizable plan with headroom>
Redundancy: <first-hop / link / chassis / site failure model>
Diagram: <layers + devices + links + segments described>
Trade-off: <what was chosen against and why>
Seam: <cloud VPC / interconnect parts routed to the cloud plugin>
```

Then emit the cross-plugin Structured Output Protocol JSON block ([`../../../ravenclaude-core/skills/structured-output/SKILL.md`](../../../ravenclaude-core/skills/structured-output/SKILL.md)).
