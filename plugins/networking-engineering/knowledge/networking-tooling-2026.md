# Networking tooling map — 2026

> **Volatile by nature.** Vendor features, product names, and capabilities change fast.
> Every entry below carries the intent; **re-verify the specific capability against the
> vendor's current docs before you quote it.** Retrieved 2026-07-01.

## Automation / NetDevOps

| Category | Options (illustrative) | Notes |
|---|---|---|
| Config automation | Ansible (network collections), Nornir, Terraform (for supported network providers) | Ansible is the common enterprise default; Nornir when you want Python-native concurrency |
| Templating | Jinja2 + structured data (YAML), vendor abstractions | The data model is the source of truth; the render is disposable |
| Source of truth / IPAM | NetBox, Nautobot, phpIPAM, Infoblox | NetBox/Nautobot are the common open source-of-truth choices |
| Validation / testing | Batfish (offline config analysis), pyATS/Genie, containerlab / GNS3 / EVE-NG (virtual topologies) | Batfish reasons about config *before* deploy; containerlab for CI test topologies |
| Streaming telemetry | gNMI/gRPC, OpenConfig models, Telegraf | Push telemetry over SNMP polling where the platform supports it |

## Data-center fabric

| Category | Options | Notes |
|---|---|---|
| Fabric control plane | BGP EVPN (multi-vendor), vendor fabric controllers | EVPN is the interoperable standard for VXLAN control |
| Overlay | VXLAN (RFC 7348), Geneve | VXLAN is dominant; Geneve where the ecosystem calls for it |
| Fabric orchestration | Vendor fabric managers | Capabilities differ sharply by vendor/version — verify |

## WAN / SD-WAN / edge

| Category | Options | Notes |
|---|---|---|
| SD-WAN | Multiple vendor platforms | Application-aware steering + IPsec overlays; feature parity varies |
| SASE / SSE | Converged network+security edge offerings | The security verdict routes to `security-engineering` |
| Transport | MPLS, broadband, LTE/5G | The overlay abstracts these into policy classes |

## Services

| Service | Common choices | Notes |
|---|---|---|
| DNS | BIND, Knot, Unbound; managed/cloud DNS | Split-horizon and caching are the usual failure points |
| DHCP / IPAM | ISC Kea, Infoblox, NetBox+plugins | Kea replaced ISC DHCP (EOL); verify version support |
| Load balancing | HAProxy, NGINX, Envoy; hardware/cloud LBs | L4 vs L7 choice drives the feature set |

## Zero-trust / segmentation

| Category | Options | Notes |
|---|---|---|
| Macro/micro-segmentation | VRFs, group-based policy/SGT, host-based micro-seg controllers | Enforcement-point placement is a design decision (architect); ruleset safety is `security-engineering` |
| ZTNA | Identity-aware access brokers | Replaces implicit-trust VPN for app access |

## Standards anchors (stable — cite directly)

- IP addressing: RFC 3021 (/31), RFC 6164 (/127), RFC 4291 (IPv6 addressing)
- Routing: RFC 2328 (OSPFv2), RFC 4271 (BGP-4), RFC 1195 (IS-IS)
- Overlay: RFC 7348 (VXLAN), RFC 8365 (EVPN as VXLAN control plane)

## Seams

- The **CI/CD pipeline** that runs automation → `devops-cicd`.
- **Cloud virtual networking** (VPC/VNet, Transit Gateway, hub-spoke) → `aws-cloud` / `azure-cloud` / `gcp-cloud`.
- **Firewall/appsec verdicts** → `security-engineering`.
- **Monitoring/SLOs** → `observability-sre`.

> This map names *categories and representative options*, not a ranked recommendation. The specific product you choose depends on the environment — and its feature set on the day you check. Last reviewed 2026-07-01.
