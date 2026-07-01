# IGP for reachability, BGP for policy

**Status:** Strong default
**Domain:** Design / routing
**Applies to:** `networking-engineering`

---

## Why this exists

OSPF/IS-IS and BGP solve different problems, and using the wrong one adds either a missing
capability or needless complexity and a new failure mode. An IGP gives you fast, automatic
*reachability* inside one administration. BGP gives you *policy* — attribute-driven path
selection — plus scale and a clean administrative boundary. Reach for BGP on a small
single-admin LAN and you've bought policy complexity you don't need; try to express
inter-AS policy in an IGP and you can't. Match the tool to the job: reachability vs policy.

## How to apply

**Do:**
- Use an **IGP (OSPF/IS-IS)** for internal reachability and fast convergence.
- Use **BGP** where you need policy control, scale beyond an IGP's comfort, or an administrative/Internet boundary (multi-homing, AS-to-AS, DC eBGP underlay).
- When both are present, let the **IGP carry reachability and BGP carry policy** — don't redistribute one wholesale into the other.

**Don't:**
- Pick BGP because it's powerful — its power is policy; without a policy need it's overhead plus a churn-amplifying failure mode.
- Stretch an IGP across an administrative boundary that wants policy separation.
- Blindly redistribute everything between protocols — that's how routing loops and unexpected paths appear.

## Edge cases / when the rule does NOT apply

- **Spine-leaf eBGP underlay** deliberately uses BGP *as* the IGP for the fabric — a recognized design pattern with per-device ASNs, not a violation of this rule.
- **Very small static-routed networks** need neither; don't add a dynamic protocol to a handful of stable stub links.

## See also
- [`../knowledge/routing-protocol-decision-tree.md`](../knowledge/routing-protocol-decision-tree.md)
- [`../skills/choose-a-routing-design/SKILL.md`](../skills/choose-a-routing-design/SKILL.md)

## Provenance
Codifies the `network-architect` house opinion "BGP is policy; IGP is reachability". Grounded in OSPF (RFC 2328) and BGP (RFC 4271) design intent. Last reviewed 2026-07-01.

---

_Last reviewed: 2026-07-01 by `claude`_
