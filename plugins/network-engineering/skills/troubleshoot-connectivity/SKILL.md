---
name: troubleshoot-connectivity
description: Isolate a network connectivity fault methodically, bottom-up the OSI stack (L1 link -> L2 VLAN/ARP/MAC -> L3 routing/ACL -> L4 port/firewall -> L7 DNS/app), naming the specific isolating test and confirming command at each layer, then return the ranked most-likely fault and how to confirm it. Reach for this when the user says "X can't reach Y" or reports intermittent/slow connectivity. Used by `network-operations-engineer` (primary).
---

# Skill: troubleshoot-connectivity

> **Invoked by:** `network-operations-engineer` (primary).
>
> **When to invoke:** "users at X can't reach Y"; "the link is slow/flapping"; "intermittent drops"; any reachability or performance fault.
>
> **Output:** a bottom-up OSI isolation walk with the confirming command at each layer + the ranked most-likely fault. (You produce the walk + commands; the live devices are outside the repo.)

## The method: isolate, don't guess

Never change config "to see if it helps." Find the *working boundary*, then bisect toward the break. Walk the layers bottom-up — most "routing problems" are really layer 1 or 2.

| Layer | Check | Confirming command (vendor-portable) |
|---|---|---|
| **L1 — physical** | Link up? Errors/CRC? Duplex/speed mismatch? SFP/cable? | `show interface` (status, errors, duplex); check optics/light levels |
| **L2 — data link** | Right VLAN? MAC learned? ARP resolving? STP blocking? Trunk allowing the VLAN? | `show mac address-table`, `show arp`, `show spanning-tree`, `show interface trunk` |
| **L3 — network** | Route to the destination? Correct gateway? ACL dropping? Asymmetric path? MTU/fragmentation? | `ping`, `traceroute`, `show ip route <dst>`, `show access-lists`, ping with DF + size for MTU |
| **L4 — transport** | Port open? Firewall/stateful drop? NAT correct? Connection table? | `telnet/nc <host> <port>`, firewall session/log, `show nat translations` |
| **L7 — application** | DNS resolving (right answer, sane TTL)? TLS/cert? App health? Load-balancer probe? | `dig`/`nslookup`, `curl -v`, load-balancer health/pool status |

## Procedure

1. **Scope the fault precisely** — who/what is affected, who is *not*, since when, what changed. The fault is usually where the symptom *isn't* — the working users define the boundary.
2. **Establish the working boundary**, then **bisect**: test reachability from progressively closer/farther points (same VLAN → gateway → next hop → destination) to localize the break to a segment.
3. **Walk the layers bottom-up** at the localized segment, running the confirming command at each. Stop at the first layer that fails — that's your fault domain.
4. **Form a single hypothesis and confirm it with a command before acting** (Capability Grounding Protocol: the network's state is a hypothesis until a `show`/`ping`/`dig`/`tcpdump` confirms it).
5. **Check "what changed" against the change log** — a recent change is the prime suspect; this is why `plan-network-change` insists on documented diffs.
6. **Fix at the cause, leave a guardrail**, and capture the diagnosis for the next person.

## Common fault signatures

- **Works locally, fails across subnets** → L3 (route/gateway/ACL).
- **Intermittent / one-directional** → asymmetric routing, MTU/fragmentation, or a flapping link.
- **DNS name fails but IP works** → L7 DNS (resolution path / stale TTL / split-horizon).
- **Slow not down** → duplex mismatch, congestion/drops, MTU, or an overloaded link — check interface errors and utilization.
- **New host can't get on** → L2 (wrong VLAN / NAC denial / DHCP scope exhaustion).

## Output contract

```
Scope: <affected vs unaffected, since when, what changed>
Boundary: <working point ... break localized to <segment>>
OSI walk: <per-layer result + the command that showed it>
Most-likely fault: <ranked> — confirm with <command>
Fix + guardrail: <cause fix + how to prevent recurrence>
```

Then emit the Structured Output Protocol JSON block.
