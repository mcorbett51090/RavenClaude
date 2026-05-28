# Azure networking & connectivity

**Last reviewed:** 2026-05-28 · **Confidence:** high (Microsoft Learn CAF connectivity + WAF, retrieved 2026-05-28). Network-security design escalates to `ravenclaude-core/security-reviewer`.
**Owner:** `network-engineer`.

## Topology
- **Hub-spoke** (classic) or **Azure Virtual WAN** (managed, large-scale/global) for the connectivity subscription. Hub holds shared services (firewall, DNS, gateways); spokes are workload VNets peered to the hub.
- **VNet / subnet** design: segment by tier (web/app/data) + delegate subnets for PaaS (Container Apps env, App Service VNet integration). **NSGs** on subnets, **UDRs** to force egress through the firewall.

## Private-by-default (house opinion #6 — the strongest single Azure posture)
**PaaS data planes get a Private Endpoint; `publicNetworkAccess` defaults to Disabled.** Key Vault, Storage, Azure SQL, Cosmos, App Configuration, Container Registry — reach them over a **Private Endpoint** wired to a **Private DNS zone** (e.g. `privatelink.vaultcore.azure.net`), with public access **off**. Public access is an **explicit, justified exception**, not the default. (The hook flags `publicNetworkAccess: 'Enabled'`, `0.0.0.0/0`, `allowBlobPublicAccess: true`, `allowSharedKeyAccess: true`.)

## Edge & ingress
- **Azure Front Door** — global HTTP(S) load balancing + CDN + WAF for internet-facing apps (multi-region).
- **Application Gateway** — regional L7 LB + WAF (single-region, VNet-internal options).
- **WAF** (on Front Door or App Gateway) — OWASP rule sets in front of public apps.
- **Load Balancer / Traffic Manager** for L4 / DNS-based routing.

## Egress & protection
- **Azure Firewall** (or NVA) in the hub for centralized, logged, allow-listed egress; UDRs route spokes through it.
- **DDoS Protection** on public-facing VNets.
- **Private Link** for consuming/exposing services privately across tenants.

## Reliability
**Zone-redundant** gateways/firewalls/Front Door where supported (house opinion #8); paired-region for DR.

## Seams
- The compute that sits in these VNets is `app-platform-engineer`; the IaC that deploys the network is `bicep-iac-engineer` (AVM has networking modules).
- Identity for private access (managed identity to reach a Private-Endpoint'd Key Vault) is `entra-identity-engineer`.
- All network-security design (firewall rules, NSG posture, WAF policy, deny-public exceptions) routes through `ravenclaude-core/security-reviewer`.
