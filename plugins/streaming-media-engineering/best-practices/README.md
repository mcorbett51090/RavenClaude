# streaming-media-engineering — best-practice docs

Named, citable rules for the `streaming-media-engineering` team's specialists. Each file is **one rule**. Engineering judgment, not legal/DRM-licensing advice; codec/protocol/CDN/DRM/player specifics are `[verify-at-use]`; no PII.

---

## Index

_5 rules across protocol selection, the encoding ladder, QoE measurement, DRM/packaging architecture, and cross-device testing._

| Doc | Status | Use when |
|---|---|---|
| [`choose-the-protocol-from-latency-and-reach.md`](./choose-the-protocol-from-latency-and-reach.md) | Pattern | Architecture — the latency target and device/browser reach pick the protocol; CMAF is the hedge. |
| [`design-the-abr-ladder-per-title-not-fixed.md`](./design-the-abr-ladder-per-title-not-fixed.md) | Absolute rule | Encoding — set bitrates from content complexity, not a copied fixed table. |
| [`measure-qoe-rebuffer-and-startup-not-just-bitrate.md`](./measure-qoe-rebuffer-and-startup-not-just-bitrate.md) | Absolute rule | Playback — judge quality-of-experience by rebuffer and startup, not the headline bitrate. |
| [`drm-and-packaging-are-architecture-decide-early.md`](./drm-and-packaging-are-architecture-decide-early.md) | Absolute rule | Architecture — decide the multi-DRM matrix and packaging format early; retrofitting is a rebuild. |
| [`test-across-devices-and-network-conditions.md`](./test-across-devices-and-network-conditions.md) | Absolute rule | Any streaming build — validate on the long tail of devices and throttled networks, not the reference player. |

---

Each rule cites its provenance and carries a `Last reviewed` date. Volatile codec/protocol/CDN/DRM/player/QoE specifics live (dated, verify-at-use) in [`../knowledge/streaming-reference-2026.md`](../knowledge/streaming-reference-2026.md).
