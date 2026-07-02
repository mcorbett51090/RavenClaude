---
name: design-segmentation-and-zero-trust
description: Design network segmentation and a zero-trust network access posture by traversing the segmentation decision tree (what to isolate -> blast radius -> enforcement point -> identity model), then return the segment plan (VLANs/VRFs/microsegmentation), the east-west + north-south policy model, the NAC/802.1X posture, and the SASE/SD-WAN or firewall enforcement point. Reach for this when the user asks "how do we segment <IoT/OT/guest/PCI> off the network?". Used by `network-architect` (primary); security verdicts escalate to security-engineering.
---

# Skill: design-segmentation-and-zero-trust

> **Invoked by:** `network-architect` (primary); `network-operations-engineer` when an ops fix touches policy.
>
> **When to invoke:** "segment IoT/OT/guest/PCI off the rest"; "how do we do zero-trust on the network?"; "limit east-west blast radius".
>
> **Output:** segment plan + policy model + NAC posture + enforcement point. The *security verdict* (is this policy sufficient?) escalates to `security-engineering`.

## Procedure

1. **Name what must be isolated and why** — IoT, OT/ICS, guest, BYOD, PCI/cardholder data, dev/test, vendor/3rd-party, management plane. Each has a different trust level and a regulatory driver.
2. **Assess the blast radius** — what can a compromised host on each segment reach today? Flat networks let one compromise pivot everywhere; that is the problem segmentation solves.
3. **Traverse the segmentation decision tree** ([`../../knowledge/network-topology-decision-trees.md`](../../knowledge/network-topology-decision-trees.md)):
   - Coarse isolation, traditional → **VLANs + inter-VLAN ACLs / firewall on a stick**.
   - Routing/tenant isolation → **VRFs** (separate routing tables).
   - Fine-grained, workload-level, "default-deny east-west" → **microsegmentation** (host-based / hypervisor / NSX / Illumio / Cisco ACI).
   - Remote/branch/cloud-edge identity-aware access → **ZTNA / SASE** (replace flat VPN with per-app, identity-gated access).
4. **Define the policy model** — north-south (to/from internet/DC) *and* east-west (segment↔segment). Default-deny east-west where blast radius warrants; allow-list the flows the apps actually need (get the flow inventory — don't guess).
5. **Specify the identity/posture layer** — **802.1X / NAC** for wired+wireless admission (who+what is on the port), device posture (patched? managed?), and dynamic VLAN/segment assignment. Zero-trust = *never trust the network location alone*; authenticate identity + device every time.
6. **Name the enforcement point(s)** — switch ACL, distributed firewall, NGFW, NAC, SASE PoP — and where logging/visibility lands.
7. **Escalate the security verdict** to `security-engineering`: this skill *designs* the segmentation; whether it's *sufficient* against the threat model is their call.

## House guardrails

- **Segment by trust, not by convenience.** A VLAN that mixes IoT and finance is not segmentation.
- **Default-deny east-west is the goal; allow-list from a real flow inventory** — broad `any/any` rules between segments defeat the purpose (the hook flags these).
- **The management plane is a segment too** — out-of-band management, not reachable from user VLANs.
- **Zero-trust is a posture (identity + device + least-privilege), not a single product** — don't let a SASE purchase substitute for the policy design.

## Output contract

```
Isolate: <segments + driver (security/regulatory)>
Blast radius today: <what a compromise can reach>
Mechanism: <VLAN/VRF/microseg/ZTNA — per decision tree>
Policy: <north-south + east-west, default-deny scope, allow-list source>
Identity/posture: <802.1X/NAC, device posture, dynamic assignment>
Enforcement + visibility: <where policy is enforced and logged>
Security verdict: ESCALATE to security-engineering
```

Then emit the Structured Output Protocol JSON block.
