---
name: choose-a-routing-design
description: Recommend a routing design from the topology's scale, administrative boundaries, and policy needs — static vs an IGP (OSPF/IS-IS) vs BGP, plus area/AS structure, summarization, and redundancy (ECMP, FHRP, fast convergence). Returns the protocol choice with its reason, the area/AS design, and the failure-domain story. Used by `network-architect` (primary).
---

# Skill: choose-a-routing-design

> **Invoked by:** `network-architect` (primary).
>
> **When to invoke:** "OSPF or BGP?"; "how do I structure the routing?"; "why won't this scale?"; before committing a routing topology.
>
> **Output:** a routing-protocol recommendation + the area/AS design + a summarization plan + the redundancy/convergence story.

## Procedure

1. **Classify the topology's scale and boundaries.** How many routers, how many sites, whose administrative control? Traverse [`../../knowledge/routing-protocol-decision-tree.md`](../../knowledge/routing-protocol-decision-tree.md): a few routers one admin owns → static or a single IGP area; a large single administration → a multi-area IGP; multiple administrations or Internet/WAN edge or policy control → BGP.
2. **Separate reachability from policy.** Use an **IGP** (OSPF/IS-IS) for internal reachability and fast convergence; use **BGP** where you need *policy* (path selection by attribute), *scale* beyond an IGP's comfort, or an *administrative boundary* (AS-to-AS, Internet edge, DC underlay). Don't run BGP to do an IGP's job or vice versa.
3. **Structure to bound the failure domain.** OSPF areas (a backbone area 0 + stub/NSSA edges), IS-IS levels, or BGP route-reflectors/confederations exist to keep an LSDB flood or a churn event local. Place area/level boundaries where you can summarize.
4. **Summarize at the boundary.** Aggregate routes at area/AS edges so a flapping link doesn't ripple network-wide. This is only possible if the addressing plan (see the addressing skill) was allocated contiguously.
5. **Design the redundancy and convergence.** Redundant paths with ECMP where symmetric; FHRP (VRRP/HSRP) at the first hop; tuned timers / BFD for sub-second convergence where the SLA needs it; graceful restart where the platform supports it. State the convergence target.
6. **Emit the artifacts.** Protocol choice + reason (the tree node), the area/AS map, the summarization boundaries, and the failure/convergence behavior.

## Quick map

| Topology | Default | Why |
|---|---|---|
| A handful of routers, one admin, stable | Static (+ floating static for backup) | Fewer moving parts than a protocol earns here |
| Enterprise/campus, one administration | OSPF or IS-IS, multi-area | Fast convergence, automatic reachability |
| Internet/WAN edge, multi-homing | BGP | Policy + provider-independence + the Internet speaks BGP |
| Spine-leaf data center | eBGP underlay (+ EVPN overlay) | Scales, simple failure domains, per-device ASN |
| Multiple autonomous administrations | BGP between them, IGP within | Policy boundary is an AS boundary |

## Guardrails
- **Don't pick BGP for prestige** — its power is policy/scale; on a small single-admin network it's overhead and a new failure mode.
- **Never leave summarization on the table** when the addressing supports it — unsummarized IGPs are how a small flap becomes a network event.
- **A default route needs an owner** — know what it points at and the behavior when that path fails.
- **State the convergence target** — "it reconverges eventually" is not a design.
