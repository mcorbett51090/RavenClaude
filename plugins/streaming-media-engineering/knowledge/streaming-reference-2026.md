# Streaming-Media Engineering — 2026 Reference

> Dated reference for the `streaming-media-engineering` team: the codec/protocol/CDN/DRM/player landscape and the QoE targets agents reach for. The durable reasoning lives in [`streaming-decision-trees.md`](streaming-decision-trees.md); this file is the freshness-anchored "what the landscape and numbers are."
>
> **Engineering judgment, not legal/DRM-licensing advice.** The codec/protocol/CDN/DRM/player landscape moves fast. Every codec claim, protocol/packaging support statement, DRM detail, CDN feature, player-SDK version, and QoE target below is **volatile** and carries a **source placeholder + retrieval date + `[verify-at-use]`** — re-confirm against the spec/vendor/SDK docs before it drives a build commitment. Estimates are marked `[ESTIMATE]`. No PII.
>
> _Last reviewed: 2026-07-03 by `claude`. Treat every specific as `[verify-at-use]` unless re-confirmed this session._

---

## 1. Codec landscape

| Codec | Role | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| H.264 / AVC | Universal reach floor | Plays almost everywhere; least efficient; mature encoders (x264, NVENC) | _<codec/encoder docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| HEVC / H.265 | Efficiency tier | ~Meaningful bitrate savings vs H.264; strong Apple/TV support; royalty considerations | _<codec/encoder docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| AV1 | Efficiency tier | Royalty-free, best efficiency of the three; higher encode cost; decode support growing | _<aomedia / encoder docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| VP9 | Web efficiency tier | Widely supported on web/Android; between H.264 and AV1 | _<webm / encoder docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |

> Codec decode support, encode cost, and royalty terms change; confirm target-device decode support and the cost/royalty trade before committing a tier.

---

## 2. Protocol / packaging landscape

| Layer | What it is | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| HLS | Apple-originated adaptive streaming | Broadest reach, native on Apple; LL-HLS variant for low latency | _<HLS spec / vendor docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| MPEG-DASH | Open adaptive streaming standard | Flexible, non-Apple ecosystems; LL-DASH for low latency | _<DASH-IF docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| CMAF | Common media fragment format (fMP4) | Shared fragments serve HLS + DASH; the packaging hedge; CENC encryption | _<CMAF spec>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| LL-HLS / LL-DASH | Low-latency live variants | Chunked CMAF / partial segments; few-second latency at CDN scale | _<spec / vendor docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| WebRTC | Real-time transport | Sub-second, interactive; hardest to scale one-to-many | _<w3c WebRTC docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |

---

## 3. CDN & DRM landscape

| Item | What it is | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| Single-CDN | One delivery network | Simpler; concentrated failover risk | _<CDN vendor docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Multi-CDN | Multiple networks + steering | Resilience + negotiating leverage; complexity/cost | _<multi-CDN docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Widevine | Google DRM | Android, Chrome, many smart-TVs; security levels (L1/L3) | _<widevine docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| FairPlay | Apple DRM | Apple ecosystem (Safari, iOS, tvOS) | _<apple DRM docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| PlayReady | Microsoft DRM | Windows, Edge, Xbox, many smart-TVs | _<playready docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |

> The device/browser reach fixes the required multi-DRM matrix. Package once (CMAF/CENC) to serve Widevine + FairPlay + PlayReady; verify each system's reach and security-level requirement before committing.

---

## 4. Player-SDK landscape

| Player | Platform | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| hls.js | Web (MSE) | HLS in non-Apple browsers | _<hls.js docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| dash.js | Web (MSE) | Reference DASH player | _<dash.js docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| Shaka Player | Web (MSE) | HLS + DASH, DRM/EME support | _<shaka docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| ExoPlayer / Media3 | Android | HLS/DASH, Widevine | _<android media docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |
| AVPlayer | Apple (iOS/tvOS/macOS) | Native HLS, FairPlay | _<apple avfoundation docs>_ — retrieved 2026-07-03 | `[verify-at-use]` |

> Player-SDK APIs, ABR defaults, and DRM/CDM paths change release to release. Verify the SDK version's ABR knobs and DRM support before tuning or shipping.

---

## 5. QoE target ranges `[ESTIMATE]`

| Metric | What it measures | Note | Flag |
|---|---|---|---|
| Video-startup time | Time to first frame | Lower is better; device/network dependent | `[ESTIMATE]` `[verify-at-use]` |
| Rebuffer ratio | Rebuffer time / watch time | Target near zero in sustained playback | `[ESTIMATE]` `[verify-at-use]` |
| Average bitrate | Delivered quality | High but stable — no oscillation | `[ESTIMATE]` `[verify-at-use]` |
| Video-start-failures (VSF) | Sessions that never start | Target near zero | `[ESTIMATE]` `[verify-at-use]` |
| CDN cache-hit ratio | Segments served from edge | Higher = faster startup, lower egress | `[ESTIMATE]` `[verify-at-use]` |

> These are directional targets, not universal SLAs — the acceptable range depends on content type, audience devices, and network mix. Set concrete QoE targets from your own analytics baseline, and treat any specific number here as `[verify-at-use]`.

---

## 6. How to use this file

1. Find the codec/protocol/CDN/DRM/player/QoE item you need.
2. Read its retrieval date — if stale or unconfirmed this session, **re-verify** against the cited source type before quoting.
3. Quote it with its flag (`[ESTIMATE]` / `[verify-at-use]`) intact when it informs an architecture, encoding, or delivery commitment.
4. For anything that gates a build decision: confirm against the spec/vendor/SDK docs first.

---

## See also

- [`streaming-decision-trees.md`](streaming-decision-trees.md) — the durable VOD-vs-live / protocol / codec / low-latency trees.
- Deep profiling methodology: [`../../performance-engineering/CLAUDE.md`](../../performance-engineering/CLAUDE.md).
- Live-service SLOs & observability: [`../../observability-sre/CLAUDE.md`](../../observability-sre/CLAUDE.md).
