---
name: select-routing-protocol
description: Choose the right routing protocol (static, OSPF, EIGRP, IS-IS, BGP) for a given boundary and scale by traversing the routing-protocol decision tree (administrative boundary -> scale -> multi-vendor -> convergence/policy need), then return the recommendation, the design knobs (OSPF areas, BGP ASNs/route-reflectors/communities, summarization), and why the alternatives were ruled out. Reach for this when the user asks "OSPF vs BGP vs static between <X>?". Used by `network-architect` (primary).
---

# Skill: select-routing-protocol

> **Invoked by:** `network-architect` (primary).
>
> **When to invoke:** "should we use OSPF/BGP/EIGRP/static between <sites/segments>?"; "how do we route between <our network> and <ISP/partner/cloud>?".
>
> **Output:** protocol recommendation + design knobs + the ruled-out alternatives.

## Procedure

1. **Identify the boundary first** — routing choice is driven by *where the boundary is*, not by preference:
   - Inside one administrative domain you control → an IGP.
   - Crossing an administrative boundary (ISP, partner, different org, the internet, often cloud) → **BGP** (policy + scale + you don't trust the other side's IGP).
2. **Traverse the routing-protocol decision tree** in [`../../knowledge/network-topology-decision-trees.md`](../../knowledge/network-topology-decision-trees.md):
   - Trivial, stable, few routes → **static** (with a floating static for backup). Don't run a protocol you don't need.
   - Single-vendor IGP, simple → **EIGRP** (Cisco) is fine where it's already in use; otherwise prefer a standard.
   - Multi-vendor IGP, scalable, standards-based → **OSPF** (or **IS-IS** for very large/SP-style flat scaling).
   - Scale, multi-homing, policy, administrative boundary, cloud peering → **BGP** (iBGP inside, eBGP at edges).
3. **Specify the design knobs** for the chosen protocol:
   - **OSPF:** area design (area 0 backbone, stub/NSSA at edges), summarization at ABRs, reference-bandwidth, authentication.
   - **BGP:** ASN plan (private vs public), iBGP full-mesh vs **route reflectors**, eBGP at edges, **communities** for policy, prefix-lists/AS-path filters, max-prefix, summarization.
   - **All:** convergence (timers, BFD), authentication, and summarization to keep tables small.
4. **State the convergence and failure behavior** — what reroutes, how fast (add **BFD** for sub-second), and what is the backup path.
5. **Rule out the alternatives explicitly** — "OSPF over BGP internally because it's one administrative domain and we don't need per-prefix policy; BGP only at the ISP edge."

## House guardrails

- **Don't run a dynamic protocol where a static route is correct** — and don't run a static route where the topology will change.
- **BGP at every boundary you don't fully control** — including most cloud interconnects (Direct Connect/ExpressRoute use BGP).
- **Always summarize** at area/AS boundaries; an un-summarized table is a convergence and stability tax.
- **Authenticate adjacencies** and filter what you advertise/accept — an open BGP edge is a route-hijack/leak risk (escalate the security verdict to `security-engineering`).

## Output contract

```
Boundary: <inside one domain | crossing an administrative boundary>
Protocol: <chosen> — because <decision-tree path>
Design knobs: <areas/ASNs/RRs/summarization/auth/BFD>
Convergence: <what reroutes, how fast, backup path>
Ruled out: <alternatives + why>
```

Then emit the Structured Output Protocol JSON block.
