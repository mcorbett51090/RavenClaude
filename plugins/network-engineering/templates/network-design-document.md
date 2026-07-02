# Network Design Document — <site / project>

> Fill the boxes. The architect produces this before any config. Trade-offs and rejected alternatives are mandatory.

## 1. Requirements
- **Scale:** <users/endpoints now> / <3-year growth>
- **Sites:** <single / campus / multi-site WAN / hybrid-cloud>
- **Traffic pattern:** <north-south | east-west dominant>
- **Availability target:** <what failure must be survived: link / device / site>
- **Constraints:** <budget / incumbent vendor / existing addressing / regulatory segmentation>

## 2. Topology
- **Chosen:** <collapsed-core | 3-tier | spine-leaf | hub-and-spoke/SD-WAN>
- **Decision-tree path:** <why, from the topology tree>
- **Rejected alternatives:** <what was chosen against + why>

## 3. IP addressing plan
| Site / role | Block | VLAN/segment | Notes |
|---|---|---|---|
| | | | |
- Management range: <oob/mgmt block>
- Point-to-point range: <p2p block>
- Headroom / summarization: <how it stays summarizable>
- IPv6: <dual-stack plan or explicit deferral>

## 4. Routing
- **Protocol(s):** <static/OSPF/BGP/...> — boundary rationale: <...>
- **Design knobs:** <areas / ASNs / route-reflectors / summarization / auth / BFD>
- **Convergence + backup path:** <...>

## 5. Segmentation & security posture
- **Segments:** <IoT/OT/guest/PCI/mgmt + driver>
- **Mechanism:** <VLAN/VRF/microseg/ZTNA>
- **Policy:** <north-south + east-west, default-deny scope>
- **Identity/posture:** <802.1X/NAC>
- **Security verdict:** ESCALATE to security-engineering

## 6. Redundancy / failure model
- First-hop: <HSRP/VRRP> · Link: <LACP> · Chassis: <MLAG/vPC/stack> · WAN: <dual transport / BGP multi-homing>
- **What happens when each component dies:** <...>

## 7. Observability
- Golden signals (utilization/errors/latency/drops) + flow (NetFlow/sFlow) + where data lands.

## 8. Seams
- Cloud VPC / interconnect: <route to cloud plugin> · IaC: terraform-iac · Security verdict: security-engineering
