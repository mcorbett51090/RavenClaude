# Network engineering — decision trees

> **Last reviewed:** 2026-06-29. Confidence: **High** for the durable design principles (topology selection, routing-protocol boundaries, OSI troubleshooting, segmentation) — these are stable network-engineering fundamentals. Vendor-specific feature support is in the companion [`network-engineering-2026-capability-map.md`](network-engineering-2026-capability-map.md) and carries its own freshness rider.
>
> Source of truth for the agents' decision-tree traversals (Capability Grounding Protocol). Inline priors live on the agents; this file is re-read on demand.

## 1. Topology selection

```mermaid
flowchart TD
  A[New / refreshed network] --> B{Datacenter with<br/>heavy east-west traffic?}
  B -- Yes --> C[Spine-leaf CLOS<br/>+ VXLAN/EVPN overlay]
  B -- No --> D{Single small site<br/>≤ ~2 switches?}
  D -- Yes --> E[Collapsed-core<br/>core+distribution combined]
  D -- No --> F{Campus with many<br/>access switches?}
  F -- Yes --> G[3-tier<br/>access / distribution / core]
  F -- No --> H{Many branches<br/>to a few hubs?}
  H -- Yes --> I[Hub-and-spoke →<br/>SD-WAN for transport independence]
  H -- No --> G
```

**Why:** match the topology to the *traffic pattern and scale*, not to fashion. Spine-leaf gives predictable any-to-any east-west latency (great for DC/virtualization, overkill for a small office). Collapsed-core is right-sized for a small site. 3-tier scales a campus. SD-WAN modernizes hub-and-spoke with policy-driven, transport-independent branch connectivity.

## 2. Routing-protocol selection

```mermaid
flowchart TD
  A[Need to route between X and Y] --> B{Crossing an administrative<br/>boundary? ISP / partner /<br/>cloud / internet}
  B -- Yes --> C[BGP<br/>policy + scale + don't trust their IGP]
  B -- No --> D{Topology trivial,<br/>stable, few routes?}
  D -- Yes --> E[Static<br/>+ floating static backup]
  D -- No --> F{Need standards-based /<br/>multi-vendor?}
  F -- No --> G[EIGRP if Cisco-only<br/>and already in use]
  F -- Yes --> H{Very large / SP-style<br/>flat scaling?}
  H -- Yes --> I[IS-IS]
  H -- No --> J[OSPF<br/>areas + summarization]
```

**Why:** the *boundary* drives the choice. BGP at any boundary you don't fully control (including most cloud interconnects — Direct Connect/ExpressRoute use BGP). An IGP inside a domain you own. Static when running a protocol buys nothing. Always summarize at area/AS edges; authenticate adjacencies; add BFD for sub-second convergence.

## 3. Segmentation / zero-trust mechanism

```mermaid
flowchart TD
  A[Need to isolate a population] --> B{Granularity?}
  B -- "Coarse (VLAN-level)" --> C[VLANs + inter-VLAN ACLs /<br/>firewall-on-a-stick]
  B -- "Routing/tenant isolation" --> D[VRFs<br/>separate routing tables]
  B -- "Workload-level, default-deny east-west" --> E[Microsegmentation<br/>host/hypervisor/ACI/Illumio]
  B -- "Remote/branch identity-aware access" --> F[ZTNA / SASE<br/>per-app, identity-gated]
  C --> G[Add 802.1X / NAC<br/>for admission + posture]
  D --> G
  E --> G
  F --> G
  G --> H[Escalate sufficiency verdict<br/>→ security-engineering]
```

**Why:** segment by *trust*, not convenience. Default-deny east-west from a real flow inventory; the management plane is its own out-of-band segment. Zero-trust = never trust network location alone (identity + device posture + least privilege). This plugin *designs* the segmentation; `security-engineering` rules whether it's *sufficient*.

## 4. Connectivity troubleshooting triage (bottom-up OSI)

```mermaid
flowchart TD
  A["Fault: X can't reach Y"] --> B[Scope: who's affected,<br/>who isn't, what changed]
  B --> C[L1: link up? errors? duplex/SFP?]
  C -- ok --> D[L2: VLAN? ARP/MAC? STP? trunk?]
  C -- fail --> Z[Fix L1 — most 'routing' bugs live here]
  D -- ok --> E[L3: route? gateway? ACL? MTU?]
  D -- fail --> Z2[Fix L2]
  E -- ok --> F[L4: port open? firewall/NAT?]
  E -- fail --> Z3[Fix L3]
  F -- ok --> G[L7: DNS? TLS? app/LB health?]
  F -- fail --> Z4[Fix L4]
  G -- fail --> Z5[Fix L7]
```

**Why:** isolate before you fix; confirm each layer with a command before forming the next hypothesis. Establish the working boundary, then bisect toward the break. The fault is usually where the symptom *isn't*.

## Quick reference — first-hop & link redundancy

| Need | Mechanism |
|---|---|
| Gateway redundancy | HSRP / VRRP / GLBP |
| Link aggregation | LACP (802.3ad) |
| Multi-chassis (no STP block, active-active uplinks) | MLAG / vPC / stacking |
| Loop prevention (where MLAG isn't used) | RSTP / MST (and prune the L2 domain) |
| Sub-second failure detection | BFD (with the routing protocol) |
| WAN path redundancy | Dual transport + SD-WAN failover / BGP multi-homing |
