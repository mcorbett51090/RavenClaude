# Network engineering — 2026 capability map

> **Last reviewed:** 2026-06-29. Confidence: **Medium** — this maps *volatile* facts (vendor platforms, product names, standard adoption). Every row carries the re-verify-at-use rider: **treat product/vendor specifics as a starting point and confirm against the vendor's current docs before committing them to a client design.** The durable engineering principles live in [`network-topology-decision-trees.md`](network-topology-decision-trees.md) (High confidence).

## How to use this file

The agents quote *principles* with confidence; they quote *this map's specifics* with a retrieval date and a "verify before committing" note. This mirrors the marketplace freshness pattern used by `ai-coding-model-guidance` for fast-moving vendor facts.

## Domains & the dominant approaches (2026)

| Domain | Durable approach (High confidence) | Representative platforms/standards (verify) |
|---|---|---|
| **Datacenter fabric** | Spine-leaf CLOS with an L2/L3 overlay for mobility + scale | VXLAN/EVPN; vendor fabrics: Cisco ACI/Nexus, Arista EOS/CloudVision, Juniper Apstra |
| **Campus / access** | 3-tier or collapsed-core; 802.1X admission; wired+wireless unified policy | Cisco Catalyst/Meraki, Aruba (HPE) CX/Central, Juniper Mist (AIOps) |
| **WAN / branch** | Transport-independent, policy-driven, app-aware; failover across dual transport | SD-WAN: Cisco Catalyst SD-WAN (Viptela), VMware/Broadcom VeloCloud, Fortinet, Palo Alto Prisma |
| **Secure edge** | Converge networking + security at an identity-aware edge (SASE/SSE) | Zscaler, Palo Alto Prisma Access, Netskope, Cloudflare, Cisco |
| **Zero-trust / NAC** | Identity + device posture + least privilege; never trust location alone | Cisco ISE, Aruba ClearPass; microseg: Illumio, Cisco Secure Workload, VMware NSX |
| **Routing** | BGP at boundaries, OSPF/IS-IS internal, BFD for fast convergence, summarize | Multi-vendor; standards-based (RFCs) over proprietary where portability matters |
| **DNS/DHCP/IPAM (DDI)** | Authoritative DDI as one managed system; document the IP plan | Infoblox, BlueCat, EfficientIP; cloud-native DNS for cloud zones |
| **Load balancing / ADC** | L4/L7 with health probes, persistence, graceful drain | F5, Citrix/NetScaler, HAProxy, NGINX, cloud LBs |
| **Observability** | Network golden signals (utilization/errors/latency/drops) + flow + streaming telemetry | NetFlow/sFlow/IPFIX, SNMP, gNMI/gRPC streaming telemetry, syslog → NMS/observability stack |
| **Automation / NetDevOps** | Config as code, idempotent, reviewed, tested before deploy | Ansible, Nautobot/NetBox (SoT), Batfish (pre-deploy validation), Terraform providers, Git |
| **IPv6** | Dual-stack the norm; design addressing for it, don't bolt it on | SLAAC/DHCPv6, prefix delegation |

## Notable directions (verify before quoting)

- **AIOps in network management** (Mist, CloudVision, Meraki) — anomaly detection and assisted root-cause; treat as an aid, not a replacement for the OSI method.
- **SASE/SSE consolidation** — the network and security edges keep merging; the *posture* (zero-trust) is what matters, not the box.
- **NetDevOps maturing** — source-of-truth-driven automation (NetBox/Nautobot) + pre-deploy validation (Batfish) is the direction for change safety; pairs with this plugin's `plan-network-change` and `terraform-iac`.
- **400G/800G in the DC; Wi-Fi 7 in campus** — capacity baselines keep rising; re-check current generation before sizing.

## Seams (where this plugin hands off)

| Question | Route to |
|---|---|
| Cloud VPC/VNet internal networking, security groups, managed LB/DNS | `aws-cloud` / `azure-cloud` / `gcp-cloud` |
| Hybrid interconnect *cloud side* (Direct Connect/ExpressRoute config) | the relevant cloud plugin (this plugin owns the on-prem/BGP side) |
| Kubernetes networking, CNI, service mesh (east-west service traffic) | `cloud-native-kubernetes` |
| "Is this firewall/segmentation policy *sufficient* vs the threat model?" | `security-engineering` |
| Codifying network config as reviewable IaC | `terraform-iac` |
| App-layer tracing / APM / SLOs | `observability-sre` |
