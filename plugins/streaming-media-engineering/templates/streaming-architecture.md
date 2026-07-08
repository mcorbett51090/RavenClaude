# Streaming Architecture — <project / date>

> Output template for the VOD/live + protocol + packaging + CDN + DRM decision and the architecture that follows. One per platform (revisit on a protocol/DRM change). Every codec/protocol/CDN/DRM/QoE cell carries a source + date or `[verify-at-use]`; no PII.

## Header
- **Project / use-case:** _____
- **Audience & their device/browser reach:** _____
- **Prepared:** 2026-__-__  · **Owner:** _____

## 1. VOD vs live & latency
| Decision | Choice | Basis | Flag |
|---|---|---|---|
| VOD / live / interactive | | how content is produced | n/a |
| Required end-to-end latency (s) | | use-case | _[verify-at-use]_ |
| Peak concurrency | | scale | _[verify-at-use]_ |

## 2. Protocol & packaging
| Decision | Choice | Basis | Flag |
|---|---|---|---|
| Protocol (HLS / DASH / LL-HLS / LL-DASH / WebRTC) | | latency + reach | _[verify-at-use]_ |
| Packaging (CMAF/fMP4 — shared fragments?) | | HLS+DASH hedge | _[verify-at-use]_ |
| Segment / part duration | | latency vs cache | _[verify-at-use]_ |

## 3. CDN & DRM
| Decision | Choice | Basis | Flag |
|---|---|---|---|
| CDN strategy (single / multi-CDN + shield) | | resilience vs cost | _[verify-at-use]_ |
| DRM matrix (Widevine / FairPlay / PlayReady) | | device/browser reach | _[verify-at-use]_ |
| Encryption + key delivery (CENC, tokens/signed URLs) | | decided early | _[verify-at-use]_ |

## 4. ABR-ladder philosophy & cost
- **Ladder philosophy:** _per-title / fixed, codec tiers, cap by reach_
- **Codec tiers:** _reach (H.264) + efficiency (HEVC / AV1 / VP9)_ — _[verify-at-use]_
- **Cost envelope:** _egress / storage / encode at scale_ — _[ESTIMATE]_

## Headline + risks
- **Headline decision:** _the VOD/live + protocol + DRM bet, in one line_
- **Top risks:** _the reversal-expensive assumptions + how they're verified_
- **Two things that would change the answer:** _____

---
_Plus the ravenclaude-core Structured Output block. All codec/protocol/CDN/DRM/QoE cells: verify-at-use before commitment. Seams: transcoding-pipeline-engineer (codec/ladder/packaging), playback-and-delivery-engineer (player/QoE/edge)._
