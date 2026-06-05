---
scenario_id: 2026-06-05-private-endpoint-dns-resolution-failure
contributed_at: 2026-06-05
plugin: azure-cloud
product: networking
product_version: "n/a"
scope: likely-general
tags: [private-endpoint, private-dns, hub-spoke, nsg, key-vault, name-resolution]
confidence: high
reviewed: false
---

## Problem

After locking a Key Vault down to `publicNetworkAccess: Disabled` and adding a Private Endpoint, an app running in a spoke VNet started failing with `Forbidden` / connection-refused errors reaching the vault. The Private Endpoint showed "approved/succeeded" in the portal, so the team assumed the endpoint was broken and was about to re-enable public access "just to unblock prod" — which would have undone the whole hardening.

## Constraints context

- Topology: classic hub-spoke. The Private DNS zone (`privatelink.vaultcore.azure.net`) was created and linked to the **hub** VNet, where the Private Endpoint's NIC lived, but **not** linked to the **spoke** VNet where the app actually ran.
- The app resolved the vault's public FQDN (`<name>.vault.azure.net`) to a **public IP** because nothing in the spoke's resolution path knew about the `privatelink` zone — so traffic went out the public path and hit `Disabled`.
- A separate, secondary contributor: an NSG on the workload subnet had a tightened outbound rule that the team suspected first (and which was a red herring for the resolution failure).
- This is a network-security design, so the posture routes to `ravenclaude-core/security-reviewer`; `network-engineer` owns the Private Endpoint + DNS wiring.

## Attempts

- Tried: re-enabling `publicNetworkAccess` on the vault to "unblock." Stopped — that defeats private-by-default (house opinion #6) and treats the symptom. Outcome: aborted, correctly.
- Tried: blaming the NSG outbound rule and loosening it. Didn't fix it — the failure was **name resolution**, not a blocked packet. Loosening the NSG widened exposure for nothing. **Confirm what the name resolves to before touching firewall/NSG rules.** Outcome: reverted.
- Tried (the diagnosis that worked): from a VM in the spoke, `nslookup <name>.vault.azure.net` returned a **public IP**, not a `10.x` private IP. That is the signature of a Private-Endpoint DNS gap — the endpoint is fine; the *resolution* is wrong.
- Tried (the fix that worked):
  1. **Linked the `privatelink.vaultcore.azure.net` Private DNS zone to the spoke VNet** (a VNet link per VNet that must resolve the name) and confirmed the zone had the A record pointing at the endpoint's private IP.
  2. Re-ran `nslookup` from the spoke — now resolved to the `10.x` private IP; the app connected.
  3. For estates with central DNS, the durable pattern is a **DNS resolver / forwarder in the hub** so every spoke inherits resolution instead of per-zone-per-spoke links — recommended as the scale fix.
  4. Left the NSG tightened (it was correct); restored `publicNetworkAccess: Disabled`.
  Outcome: private resolution working, vault still public-access-disabled, NSG unchanged.

## Resolution

A Private Endpoint has **two halves**: the endpoint NIC (a private IP in a subnet) **and** the DNS that makes clients resolve the service FQDN to that private IP. The endpoint showing "succeeded" only confirms the first half. The classic failure is the **`privatelink` Private DNS zone not linked to the VNet where the client runs** — common in hub-spoke when the zone is linked to the hub but not every consuming spoke. The diagnostic that cuts straight to it: **`nslookup` the service FQDN from the client's network and check whether you get a public or a private IP** — before suspecting NSGs or the endpoint itself. See [`../knowledge/azure-networking-and-connectivity.md`](../knowledge/azure-networking-and-connectivity.md) and the Private-Endpoint-vs-Service-Endpoint tree in [`../knowledge/azure-compute-decision-tree.md`](../knowledge/azure-compute-decision-tree.md).

**Action for the next consultant hitting this pattern:** when a private-by-default PaaS data plane is unreachable, `nslookup` the FQDN from the client subnet first. Public IP → DNS gap (link the `privatelink.*` zone to that VNet / fix the forwarder), not a broken endpoint and not (usually) the NSG. Never re-enable public access to "unblock." The exact `privatelink` zone name per service type and resolver pricing are version-volatile — `[verify-at-use]`. Route the posture to `ravenclaude-core/security-reviewer`.

**Sources (retrieved 2026-06-05):**
- Private Endpoint DNS configuration (incl. the per-service `privatelink` zone names) — https://learn.microsoft.com/azure/private-link/private-endpoint-dns
- Private Endpoint DNS integration scenarios (hub-spoke + central forwarder) — https://learn.microsoft.com/azure/private-link/private-endpoint-dns-integration
- Azure Private Resolver — https://learn.microsoft.com/azure/dns/dns-private-resolver-overview

The `privatelink` zone FQDNs and resolver behavior are version-sensitive — `[verify-at-use]` against current Microsoft docs.
