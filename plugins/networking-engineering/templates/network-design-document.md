# Network Design Document (HLD) — <site / fabric / project name>

> High-level design. Captures **intent and rationale**, not device config. The
> `network-implementation-engineer` renders this into configuration and automation.
> Fill every section; "N/A" is an answer, a blank is a gap.

## 1. Purpose & scope

- **What this network serves:** <users / apps / sites>
- **In scope / out of scope:** <boundaries>
- **Constraints:** <budget, existing gear, vendor, compliance, timeline>

## 2. Requirements

| Requirement | Target | Source |
|---|---|---|
| Availability | <e.g. 99.9%, N+1> | <SLA / stakeholder> |
| Convergence | <e.g. sub-second on link failure> | <design> |
| Scale (hosts/sites/growth) | <counts + growth factor> | <capacity plan> |
| Segmentation / compliance | <zones, regulatory> | <security> |

## 3. Topology

- **Physical:** <diagram / description — devices, links, redundancy>
- **Logical:** <L2 domains, L3 boundaries, fabric/overlay if any>
- **Failure domains:** <what's contained where>

## 4. IP addressing plan

| Block | Prefix | Purpose | Summarizes to | VLAN/segment |
|---|---|---|---|---|
| <region/site> | <CIDR> | <user/server/infra/mgmt> | <parent prefix> | <id> |

- **IPv6 plan:** <site /48, segment /64 mapping>
- **Reserved / growth:** <blocks held back>

## 5. Routing design

- **Protocol(s) + why:** <static / OSPF / IS-IS / BGP — the decision-tree node>
- **Areas / AS structure:** <area 0 + edges / ASNs / route-reflectors>
- **Summarization boundaries:** <where routes aggregate>
- **Redundancy & convergence:** <ECMP, FHRP, BFD, targets>
- **Default route:** <where it points, failure behavior>

## 6. Segmentation & policy

| Segment | Trust zone | East-west default | Enforcement point |
|---|---|---|---|
| <name> | <user/server/OT/DMZ/mgmt> | <deny/allow-list> | <FW/ACL/SGT> |

> Policy **verdict** (is the ruleset safe?) → `security-engineering`.

## 7. Services

- **DNS:** <servers, zones, split-horizon?>
- **DHCP / IPAM:** <scopes, reservations, source of truth>
- **Load balancing / NAT:** <L4/L7, VIPs, NAT scheme>

## 8. Failure & rollback

- **Failure scenarios considered:** <link, device, path, transport>
- **Rollback approach for changes:** <commit-confirm / staged>

## 9. Open questions & risks

| Item | Impact | Owner | Status |
|---|---|---|---|

## 10. References

- Routing decision: [`../knowledge/routing-protocol-decision-tree.md`](../knowledge/routing-protocol-decision-tree.md)
- Addressing/segmentation: [`../knowledge/subnetting-and-segmentation-decision-tree.md`](../knowledge/subnetting-and-segmentation-decision-tree.md)
