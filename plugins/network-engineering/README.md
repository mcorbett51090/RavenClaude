# network-engineering

> Enterprise network-engineering team for Claude Code — the **network layer below the cloud VPC**. Two specialist agents, a decision-tree knowledge bank, skills, best-practices, templates, and an advisory hook. Requires `ravenclaude-core@>=0.7.0`.

## What it's for

The cloud plugins (`aws-cloud` / `azure-cloud` / `gcp-cloud`) own **VPC/VNet-level** networking; `cloud-native-kubernetes` owns **service-mesh / CNI** east-west traffic. This plugin owns everything else network: **campus / datacenter / WAN topology, routing & switching, IP addressing, segmentation & zero-trust, redundancy, and day-2 operations.**

## Agents

| Agent | Use it for |
|---|---|
| **network-architect** | Designing a network — topology (collapsed-core / 3-tier / spine-leaf / SD-WAN), routing-protocol choice (static / OSPF / BGP), VLAN/VXLAN segmentation + zero-trust, IP addressing, redundancy/HA. Design-before-config; protocol-before-vendor. |
| **network-operations-engineer** | Running a network — bottom-up OSI troubleshooting, staged & reversible change management, DNS/DHCP/IPAM/load-balancer operation, network observability. |

## Skills

- `design-network-topology` — topology + addressing + redundancy from requirements.
- `select-routing-protocol` — protocol choice by administrative boundary and scale.
- `design-segmentation-and-zero-trust` — segments, NAC/802.1X, microsegmentation, SASE/ZTNA.
- `troubleshoot-connectivity` — methodical bottom-up OSI fault isolation.
- `plan-network-change` — windowed, reversible change with a tested rollback.

## Knowledge bank

- `network-topology-decision-trees.md` — 4 Mermaid decision trees (topology, routing-protocol, segmentation, troubleshooting triage) + a redundancy quick-reference. **High confidence** (durable principles).
- `network-engineering-2026-capability-map.md` — dated vendor/platform/standard map + the seam table. **Medium confidence**; carries a re-verify-at-use rider.

## Templates

`network-design-document.md` · `network-change-plan.md` · `troubleshooting-runbook.md`

## Advisory hook

`flag-network-smells.sh` (PreToolUse) flags permissive `any/any` firewall/ACL permits, cleartext management (telnet / `ip http server`), and network change docs missing a rollback or a change window. Advisory by default; `NETENG_STRICT=1` makes it blocking.

## House opinions

Design before config · protocol before vendor · no change without a tested rollback · troubleshoot bottom-up and isolate before you fix · segment by trust with default-deny east-west · document a summarizable IP plan · BGP at boundaries / IGP inside / static when a protocol buys nothing · zero-trust is a posture not a product · redundancy + a failure model are part of the design · volatile vendor claims carry a retrieval date.

## Seams

Cloud VPC/VNet & managed LB/DNS → the cloud plugins · k8s/service mesh → `cloud-native-kubernetes` · firewall/segmentation *sufficiency* verdict → `security-engineering` · config-as-IaC → `terraform-iac` · app-layer tracing/SLOs → `observability-sre`.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install network-engineering@ravenclaude
```
