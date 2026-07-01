# IP Addressing Plan — <organization / site>

> The authoritative allocation table. Allocate **contiguously and hierarchically** so
> routes summarize (see [`../best-practices/allocate-address-space-so-routes-summarize.md`](../best-practices/allocate-address-space-so-routes-summarize.md)).
> This is intent — the source of truth for the addressing plane.

## Supernet & summarization hierarchy

- **Organization supernet (IPv4):** <e.g. 10.0.0.0/8 or a carved 10.0.0.0/12>
- **Organization prefix (IPv6):** <e.g. 2001:db8::/32 → /48 per site>

```
Region  →  Site        →  Pod/Building  →  Segment/VLAN
/12        /16 or /20      /22 or /24       /24 .. /27
(summarizes up at each boundary)
```

## Allocation table

| Block (IPv4) | Block (IPv6) | Purpose | Trust zone | Summarizes to | VLAN | Notes |
|---|---|---|---|---|---|---|
| <10.10.0.0/24> | <2001:db8:10::/64> | User | User | <10.10.0.0/20> | 110 | |
| <10.10.16.0/24> | <2001:db8:10:10::/64> | Server | Server | <10.10.0.0/20> | 210 | |
| <10.10.240.0/24> | | Management | Mgmt | <10.10.240.0/22> | 900 | OOB, isolated |
| <10.10.255.0/31 …> | <…/127> | P2P links | Infra | | | RFC 3021 / 6164 |
| <10.10.254.0/24> | | Loopbacks | Infra | | | one /32 per device |

## Reserved / growth

| Block | Held for | Release condition |
|---|---|---|
| <block> | <future pod / M&A / cloud peering> | <when> |

## Overlap / connectivity check

- [ ] No overlap with existing RFC 1918 usage that must route/merge (VPN, cloud, M&A)
- [ ] P2P links use /31 (v4) / /127 (v6)
- [ ] Management is on its own isolated block
- [ ] Every leaf fits inside a contiguous parent that summarizes

## References
- [`../knowledge/subnetting-and-segmentation-decision-tree.md`](../knowledge/subnetting-and-segmentation-decision-tree.md)
