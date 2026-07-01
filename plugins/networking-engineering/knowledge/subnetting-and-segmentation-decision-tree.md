# Subnetting & segmentation decision tree

Traverse this before carving address space or drawing segments. Two goals pull
together: **summarizable hierarchy** (so routing stays small) and **trust-boundary
segmentation** (so a compromise stays contained).

```mermaid
flowchart TD
    A[New segment / site to address] --> B{Point-to-point<br/>infra link?}
    B -->|Yes| C[/31 IPv4 RFC 3021<br/>/127 IPv6 RFC 6164]
    B -->|No| D{Size from host count<br/>x growth factor}
    D --> E[Round up to a power-of-two<br/>prefix with headroom]
    E --> F{Does it fit inside the<br/>parent's contiguous block?}
    F -->|No| G[Re-allocate: keep each site/pod<br/>contiguous so it summarizes]
    F -->|Yes| H{What trust zone is this?}
    H -->|User| I[User segment]
    H -->|Server / app| J[Server segment]
    H -->|OT / IoT| K[Isolated segment,<br/>default-deny east-west]
    H -->|DMZ / external| L[DMZ, enforced both ways]
    H -->|Management| M[Out-of-band / separate,<br/>never shared with data]
    I --> N[Place enforcement point<br/>at the boundary; set the<br/>east-west default posture]
    J --> N
    K --> N
    L --> N
    M --> N
    N --> O[Route the segmentation<br/>POLICY VERDICT to<br/>security-engineering]
```

## Allocation reference

| Purpose | Guidance | Standard |
|---|---|---|
| Point-to-point IPv4 link | /31 (2 usable, no waste) | RFC 3021 |
| Point-to-point IPv6 link | /127 | RFC 6164 |
| IPv6 site | /48 per site, /64 per segment | RFC 4291 / addressing best practice |
| Loopbacks | A dedicated /24 (v4) or /64 carve, one host each | — |
| Growth reserve | Reserve at the parent level before handing out leaves | — |

## Segmentation model

| Zone | East-west default | Rationale |
|---|---|---|
| User | Deny to server/mgmt except explicit | Users are the largest attack surface |
| Server | Micro-segment by app tier where feasible | Contain lateral movement |
| OT / IoT | Default-deny, tightly allow-listed | Least patchable, highest risk |
| DMZ | Enforced inbound *and* outbound | Internet-facing = assume hostile |
| Management | Isolated / out-of-band | Control plane compromise = game over |

## Rules of thumb

- **Contiguous or it won't summarize.** Non-contiguous allocation permanently defeats aggregation — the single most common addressing regret.
- **Segment by trust boundary, not by org chart.** Draw the line where trust changes.
- **Management is separate, always.** Never on the segment it manages.
- **You own where the boundary sits; `security-engineering` owns whether the ruleset is safe.**

> Addressing standards are stable (RFCs above). Platform segmentation *features* (VRFs, SGT/TrustSec, micro-seg controllers) are volatile — verify and date. Last reviewed 2026-07-01.
