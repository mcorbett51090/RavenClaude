# Segment by trust, enforce at a chokepoint

**Rule:** Segment populations by trust level (IoT, OT, guest, PCI, management), default-deny east-west where blast radius warrants, and allow-list flows from a *real flow inventory* — not a guess. Name the enforcement point.

**Why:** a flat network lets one compromise pivot everywhere. Segmentation bounds the blast radius. Broad `any/any` rules between segments defeat the purpose; the management plane belongs out-of-band.

**Anti-pattern:** a VLAN that mixes IoT cameras and finance hosts, or "segmentation" whose inter-segment rule is `permit ip any any`. The sufficiency verdict escalates to security-engineering.
