# Changelog — networking-engineering

All notable changes to this plugin are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this plugin adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-07-01

### Added

- Initial build-out of the `networking-engineering` plugin.
- **2 agents:** `network-architect` (topology, IP addressing & segmentation, routing-protocol choice, DC fabric / SD-WAN, zero-trust segmentation) and `network-implementation-engineer` (device config, OSPF/BGP/VLAN/ACL/NAT, DNS/DHCP, NetDevOps automation, layered troubleshooting).
- **5 skills:** design-ip-addressing-and-segmentation, choose-a-routing-design, design-a-datacenter-or-sdwan-fabric, configure-switching-routing-and-services, automate-network-with-netdevops.
- **Knowledge bank (4 docs):** routing-protocol decision tree (Mermaid), subnetting & segmentation decision tree (Mermaid), layered L1→L7 troubleshooting reference, and a dated 2026 tooling map.
- **5 best-practices:** rollback-before-change, summarizable addressing, trust-boundary segmentation, IGP-for-reachability/BGP-for-policy, config-as-code-is-source-of-truth.
- **3 templates:** network design document (HLD), change plan & rollback, IP addressing plan.
- **1 advisory hook** (`flag-network-hygiene-smells.sh`): flags trunk `vlan all` L2 sprawl and change/runbook docs missing a rollback path; advisory by default, blocking under `NETENG_STRICT=1`.
