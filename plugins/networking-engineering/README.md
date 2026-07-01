# networking-engineering

Design, build, and operate **enterprise, campus, and data-center networks** — the physical
and logical L2/L3 layer under your applications and cloud. Two specialist agents cover the
full lifecycle from topology design to device config to NetDevOps automation and
troubleshooting.

## Install

```
/plugin install networking-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## The team

| Agent | Reach for it when |
|---|---|
| **network-architect** | You're deciding the *shape*: IP addressing & segmentation, OSPF vs BGP, a spine-leaf/VXLAN-EVPN fabric or SD-WAN, zero-trust segmentation. |
| **network-implementation-engineer** | You're *building or running* it: writing switch/router/firewall/LB config, DNS/DHCP/NAT/ACLs, managing config-as-code with drift detection, or troubleshooting a break layer by layer. |

## What's inside

- **5 skills** — design IP addressing & segmentation, choose a routing design, design a DC/SD-WAN fabric, configure switching/routing/services, automate with NetDevOps.
- **Knowledge bank** — two Mermaid decision trees (routing-protocol choice, subnetting & segmentation), a layered L1→L7 troubleshooting reference, and a dated-2026 tooling map.
- **5 best-practices** — rollback-before-change, summarizable addressing, trust-boundary segmentation, IGP-vs-BGP, config-as-code.
- **3 templates** — network design document (HLD), change plan & rollback, IP addressing plan.
- **1 advisory hook** — flags L2 trunk sprawl and change docs missing a rollback path.

## When to reach for a different plugin

- **Cloud virtual networking** (VPC/VNet, Transit Gateway, hub-spoke, cloud load balancers) → `aws-cloud` / `azure-cloud` / `gcp-cloud`. This plugin owns the physical/enterprise network; the cloud plugins own the virtual overlay in a provider.
- **Is this firewall ruleset safe?** (appsec verdict, exploitability) → `security-engineering`. This plugin decides where the boundary sits; security-engineering signs off on the ruleset.
- **Network monitoring, SLOs, reliability incidents** → `observability-sre`.
- **Kubernetes networking** (CNI, service mesh, ingress) → `cloud-native-kubernetes`.

## House opinions (the short version)

No change without a rollback path · allocate address space so routes summarize · keep the
L2 blast radius small · segment by trust boundary, not convenience · IGP for reachability,
BGP for policy · config-as-code is the source of truth · design for the failure case first.

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution.
