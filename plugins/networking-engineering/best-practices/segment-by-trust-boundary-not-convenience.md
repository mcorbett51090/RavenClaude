# Segment by trust boundary, not by convenience

**Status:** Strong default
**Domain:** Design / segmentation / security posture
**Applies to:** `networking-engineering`

---

## Why this exists

Segmentation exists to contain a compromise: when an attacker lands on one host, the
segment boundary is what stops lateral movement to everything else. If you draw segments
for administrative tidiness — one VLAN per department — the boundaries don't line up with
where trust actually changes, and the "segmentation" contains nothing. A flat network
with cosmetic VLANs is a single blast radius wearing a costume. Draw the lines where trust
changes, put an enforcement point there, and default the east-west policy to deny.

## How to apply

**Do:**
- Segment along **trust boundaries**: user vs server vs OT/IoT vs DMZ vs management.
- Put an **enforcement point** at every boundary and set the east-west default to deny-with-explicit-allow for a zero-trust posture.
- Keep the **management plane on its own isolated/out-of-band segment** — never shared with the traffic it manages.
- Isolate OT/IoT hardest — it's the least patchable, highest-risk population.

**Don't:**
- Create VLANs per org-chart box and call it segmentation.
- Put management interfaces on a user or server segment.
- Allow-all east-west "for now" — "now" becomes the permanent posture.

## Edge cases / when the rule does NOT apply

- **Very small networks** where a single trust zone genuinely covers everything — don't manufacture segments that add operational cost with no containment benefit. But *management still stays separate*.
- The **ruleset's safety verdict** is not yours to sign off — you own where the boundary sits and its default posture; whether a specific firewall ruleset is safe routes to `security-engineering`.

## See also
- [`../knowledge/subnetting-and-segmentation-decision-tree.md`](../knowledge/subnetting-and-segmentation-decision-tree.md)
- [`../skills/design-ip-addressing-and-segmentation/SKILL.md`](../skills/design-ip-addressing-and-segmentation/SKILL.md)

## Provenance
Codifies the `network-architect` house opinion "segment by trust boundary, not by convenience" and zero-trust segmentation principles. Last reviewed 2026-07-01.

---

_Last reviewed: 2026-07-01 by `claude`_
