---
description: Harden an Azure workload's network posture — pick hub-spoke vs vWAN from the decision tree, segment subnets with default-deny NSGs, force egress through the hub firewall, and lock every PaaS data plane behind a Private Endpoint.
argument-hint: "[the workload/VNet, e.g. 'payments app and its SQL + Key Vault']"
---

# Harden network and data planes

You are running `/azure-cloud:harden-network-and-data-planes`. Lock down the network and data-plane posture for what the user described (`$ARGUMENTS`), following this plugin's `network-engineer` discipline — private is the baseline, public is the documented exception.

## When to use this

A workload's networking is being designed or reviewed before it carries real traffic. For a fully-PaaS, no-VNet estate (Static Web Apps + serverless + private-endpoint'd data) you may not need a hub firewall at all — say so rather than standing one up for its own sake.

## Steps

1. **Pick the topology from the decision tree, not from habit** — single-region/simple → one segmented VNet; few regions + want to own routing → classic hub-spoke; global/many-branch → Azure Virtual WAN (`network-hub-spoke-vs-virtual-wan.md`). Name the observable (region count, branch aggregation) that resolved it; it's a one-way door on a live estate.
2. **Segment by tier:** one subnet per tier (web/app/data) plus delegated subnets for VNet-integrated PaaS and a dedicated Private Endpoint subnet (`network-segment-subnets-with-nsgs-and-forced-egress.md`).
3. **NSG every subnet, default-deny inbound,** allow only the specific source/port flows; send NSG flow logs to Log Analytics. Never put `sourceAddressPrefix: '*'` on an inbound Allow to a data subnet (same file).
4. **Force egress through the hub firewall** with a UDR sending `0.0.0.0/0` to the firewall's private IP — outbound is logged and allow-listed, not silently open (same file).
5. **Lock every PaaS data plane private:** `publicNetworkAccess: 'Disabled'`, a Private Endpoint, and the matching `privatelink.*` Private DNS zone linked to the VNet — without the DNS zone the endpoint resolves to nothing (`private-by-default-paas-data-planes.md`). Prefer RBAC + managed identity over shared keys.
6. **Make hub gateways/firewall zone-redundant for prod** (house opinion #8).

## Guardrails

- Never leave `allowBlobPublicAccess: true`, a `0.0.0.0/0` rule, or `publicNetworkAccess: 'Enabled'` "to unblock the demo" — the anti-pattern hook flags all four.
- A genuinely-public asset (static-site Storage, public feed) is a scoped, documented exception — one account, not the estate.
- Firewall rules, NSG posture, and any deny-public exception are network-security design → route to `ravenclaude-core/security-reviewer`.
