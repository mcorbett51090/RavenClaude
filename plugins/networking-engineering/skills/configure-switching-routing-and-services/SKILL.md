---
name: configure-switching-routing-and-services
description: Produce reviewable device configuration for L2 (VLAN/trunk/STP), L3 (OSPF/BGP, summarization, filters), and edge services (ACLs, NAT, DNS, DHCP) that implements a given design — always with pre/post validation and a rollback path. Returns the config plus its validation and rollback plan. Used by `network-implementation-engineer` (primary).
---

# Skill: configure-switching-routing-and-services

> **Invoked by:** `network-implementation-engineer` (primary).
>
> **When to invoke:** "write the OSPF/BGP config"; "set up these VLANs/trunks/ACLs/NAT"; "configure DNS/DHCP for this segment".
>
> **Output:** vendor-appropriate, reviewable config + a pre/post validation checklist + an explicit rollback path.

## Procedure

1. **Restate the design and the success criteria.** What must be true after the change (these prefixes reachable, this neighbor up, this east-west flow denied). Config with no acceptance criteria can't be validated.
2. **Capture pre-change state.** Routing table, neighbor/adjacency state, interface counters, the specific flows you're about to affect. This is your diff baseline and half your rollback evidence.
3. **Write L2 deliberately.** VLANs and trunks with an explicit allowed-VLAN list (never "all"), STP root placement chosen (not accidental), and edge ports hardened (portfast + BPDU guard) so a user port can't become root.
4. **Write L3 with filters and summarization.** OSPF areas / BGP neighbors with the intended summarization and route filters (prefix-lists/route-maps). Inbound and outbound policy is explicit, most-specific-first; there is a deliberate default, not an accidental one.
5. **Order ACLs correctly and log the denies that matter.** First-match wins → most-specific and highest-risk rules first, no shadowed entries, an explicit terminating deny. NAT rules match the addressing plan and don't collide with the ACLs.
6. **Configure services as dependencies.** DHCP scopes/reservations, DNS forwarders/zones, and any helper/relay — verify resolution and lease behavior explicitly, because "the network is down" is DNS half the time.
7. **Apply behind a rollback.** Commit-confirm / rollback timer where supported, or a staged saved-rollback. Validate post-change against step 1 *from a second path* before you confirm.

## Quick map

| Element | Do | Common bug |
|---|---|---|
| Trunk | Explicit allowed-VLAN list | `switchport trunk allowed vlan all` sprawls the L2 domain |
| Edge port | portfast + BPDU guard | A looped user port becoming STP root |
| ACL | Most-specific first, explicit deny | A shadowed rule that never matches |
| BGP/OSPF | Filters + summarization + a chosen default | Redistributing everything; an accidental default |
| Change | Commit-confirm + post-validate | Applying with no rollback and no verification |

## Guardrails
- **No change without a rollback path** — a config that can cut your own management plane needs an auto-revert.
- **Validate from a second path** — verifying from the box you just changed can lie.
- **Never trust `allowed vlan all` or an unfiltered redistribute** — both are how a local change becomes a network event.
- Config *syntax* is platform- and version-specific — confirm against the target platform, don't assume one vendor's CLI.
