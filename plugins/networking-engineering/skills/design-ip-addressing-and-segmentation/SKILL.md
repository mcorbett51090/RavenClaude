---
name: design-ip-addressing-and-segmentation
description: Produce a hierarchical IPv4/IPv6 addressing plan and a segmentation model for a site, campus, or data center — sized for growth, allocated so routes summarize, and carved along trust boundaries. Returns the address plan, the VLAN/segment map, and the inter-segment policy baseline. Used by `network-architect` (primary) and `network-implementation-engineer`.
---

# Skill: design-ip-addressing-and-segmentation

> **Invoked by:** `network-architect` (primary); `network-implementation-engineer` when implementing an existing plan.
>
> **When to invoke:** "design the subnetting"; "how should I lay out the IP space?"; "segment this flat network"; before any new site/DC build.
>
> **Output:** a hierarchical addressing plan (with summarization boundaries), a VLAN/segment map, and the inter-segment (east-west) policy baseline.

## Procedure

1. **Size from real counts, not round numbers.** Count hosts/segment today, apply a growth factor, and round up to a power-of-two prefix with headroom. Undersizing forces renumbering; grotesque oversizing wastes summarizable space.
2. **Allocate hierarchically so routes aggregate.** Give each site/pod/segment a *contiguous* block that summarizes to one prefix at the boundary above it (region → site → building/pod → VLAN). Traverse [`../../knowledge/subnetting-and-segmentation-decision-tree.md`](../../knowledge/subnetting-and-segmentation-decision-tree.md).
3. **Reserve deliberately.** Carve out blocks for infrastructure (loopbacks, point-to-point links — use /31 for P2P per RFC 3021, /127 for IPv6 per RFC 6164), management, and future growth *before* handing out user space.
4. **Plan IPv6 alongside IPv4.** A /48 per site, /64 per segment; align the IPv6 segment map to the IPv4 one so operators reason about one topology, not two.
5. **Segment by trust boundary.** Draw the segments where trust changes — user vs server vs OT/IoT vs DMZ vs management — not per-department-for-tidiness. Each boundary gets an enforcement point; the east-west default is deny-with-explicit-allow for a zero-trust posture.
6. **Emit the artifacts.** The address-allocation table (block → purpose → summarization parent), the VLAN/segment map, and the inter-segment policy matrix. Hand the policy *verdict* to `security-engineering`.

## Quick map

| Need | Choice | Why |
|---|---|---|
| Point-to-point link (IPv4 / IPv6) | /31 / /127 | Two-host links waste a /30's network+broadcast; RFC 3021 / RFC 6164 |
| Site block | Contiguous, summarizable /20–/16 | One route leaves the site, not fifty |
| Management network | Separate, tightly-filtered segment | Compromise of user space must not reach the control plane |
| OT / IoT | Its own segment, default-deny east-west | Highest-risk, least-patchable devices |

## Guardrails
- **Never allocate non-contiguously if you can avoid it** — it permanently defeats summarization.
- **Don't overlap address space you may later need to route/merge** (M&A, VPN, cloud peering) — check RFC 1918 usage against future connectivity.
- **Management plane is separate** — never on the same segment/VLAN as the traffic it manages.
- Segmentation *policy verdicts* (is this ruleset safe?) route to `security-engineering`; you own where the boundary sits and the default posture.
