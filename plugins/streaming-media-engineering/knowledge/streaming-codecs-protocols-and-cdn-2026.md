# Streaming codecs, protocols, DRM & CDN — dated 2026 map

> **Retrieval date: 2026-07-06.** Device/browser codec support, DRM support, CDN
> features, and per-platform LL-HLS behavior are **volatile** and change over time.
> Treat every device-compatibility and feature claim here as `[verify-at-use]` and
> re-check before a client commitment. The **durable** content is the packaging
> strategy (CMAF package-once, CBCS multi-DRM), the codec trade-offs, and the QoE
> definitions; the *device-support specifics* are the perishable part.

## Packaging: package once, deliver many (durable)

| Choice | Do this | Why |
|---|---|---|
| Container | **CMAF fragmented-MP4** | One set of segments serves both HLS and DASH — no parallel TS-HLS + MP4-DASH trees. |
| Encryption mode | **CBCS** (AES-CBC subsample) | One encryption serves **Widevine + FairPlay + PlayReady**. CENC (CTR) historically didn't cover FairPlay cleanly — CBCS is the multi-DRM default. |
| Manifests | HLS `.m3u8` + DASH `.mpd` over the same CMAF segments | Reach Apple (HLS-first) and everything else (DASH) from one origin. |
| Low latency | Chunked CMAF / LL-HLS partial segments | Only when the latency tier requires it (see the decision tree). |

## DRM matrix (durable structure; device specifics dated)

| DRM system | Primary platforms | Notes |
|---|---|---|
| **Widevine** (L1/L3) | Chrome, Android, many smart TVs | L1 = hardware-backed (required for HD/UHD by many studios); L3 = software. |
| **FairPlay** | Safari, iOS/iPadOS, tvOS | Apple's system; HLS-native; needs its own key/license format. |
| **PlayReady** | Edge, Windows, Xbox, many TVs | Microsoft's system. |

**Rule (durable):** package **once** with CBCS and drive all three via a multi-DRM
license service — do **not** encrypt three times. Match DRM level to content value:
no DRM (open) → AES-128/clear-key (basic) → studio-grade multi-DRM with hardware L1
(premium/licensed). Studio-grade DRM adds a license server, key rotation, and
per-device testing — don't take it on by reflex.

## Codec ladder (durable trade-offs; support dated)

| Codec | Reach | Efficiency | Use when |
|---|---|---|---|
| **H.264 / AVC** | Universal | Baseline | The reach floor — always include unless you fully control the device base. |
| **HEVC / H.265** | Broad but licensing-encumbered | ~30–50% better than H.264 | Apple ecosystem, 4K; watch licensing. |
| **AV1** | Modern devices, growing | Best efficiency, royalty-free | High-volume VOD where encode cost + device base justify it; live AV1 is heavier. |

**Ladder rules (durable):**
- **H.264 as the reach baseline;** add HEVC/AV1 only where the device base supports
  them and bitrate savings (⇒ egress savings) justify the extra encode.
- **Per-title / context-aware ladders** beat a fixed ladder when volume justifies the
  analysis — simple content doesn't need the top rungs.
- **Align keyframes/IDR at segment boundaries across every rung** — this is what lets
  ABR switch without stalling. Misaligned GOPs are a top cause of rebuffering.
- Match audio codec (AAC universal; others where supported) and declare codec strings
  correctly in the manifest.

## Protocols quick-reference (durable roles)

| Protocol | Role | Latency | Scale |
|---|---|---|---|
| **HLS** | Apple-origin, now universal adaptive HTTP streaming | ~10–30s standard | Excellent (CDN). |
| **LL-HLS** | Low-latency HLS via partial segments | ~2–6s | Good; more origin/CDN complexity. |
| **MPEG-DASH** | Adaptive HTTP streaming (non-Apple) | ~10–30s / LL variants | Excellent (CDN). |
| **CMAF** | The fMP4 container both HLS & DASH share | — | Enables package-once. |
| **WebRTC (WHIP/WHEP)** | Interactive, two-way, sub-second | <1s | Needs SFU/media server; does NOT scale like HTTP streaming. |

## CDN / origin & QoE (durable)

- **Egress dominates the streaming bill.** Codec efficiency, ladder design, and
  cache-hit ratio are cost levers as much as quality levers — loop in
  `finops-cloud-cost` on any at-scale design.
- **Origin shield + good cache keys** keep the origin from melting; segments are
  highly cacheable if the cache key is right (watch query-string and byte-range
  handling). Set CORS for browser players.
- **Multi-CDN** buys resilience and per-region performance at added complexity — use
  it when a single CDN's reach/reliability is the binding constraint.
- **QoE is measured at the player (durable definitions):**
  - **Startup time** — join time from click to first frame.
  - **Rebuffer ratio** — fraction of session spent stalled (the churn driver).
  - **Average bitrate / VMAF-at-play** — delivered quality.
  - **Error/exit-before-video rate** — hard failures.
  Instrument these from player analytics; encoder-side metrics alone don't tell you
  if users can watch.

## Seams

- Egress / CDN / encode cost modeling → `finops-cloud-cost`.
- Player UI (React/mobile shell around the video element) → `frontend-engineering`.
- Streaming-infra reliability / on-call → `observability-sre`.
- Kafka/Flink *data* streams (not media) → `data-streaming-engineering`.
- Content production / editing → `film-video-production`.
- Frame analysis (detection/OCR on the stream) → `computer-vision-engineering`.
