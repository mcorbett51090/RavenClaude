# streaming-media-engineering plugin

> **Audio/video delivery engineering** for the RavenClaude marketplace: getting
> media from an encoder to a player at scale. It answers **"how do I package,
> protect, and deliver this stream — at what latency, to which devices, at what
> QoE and cost?"** — the delivery layer that `data-streaming-engineering`
> (Kafka/Flink *data*), `film-video-production` (content), and `frontend-engineering`
> (the player UI) do **not** own.

**Designed for:** an engineer building live or VOD streaming who needs the latency
tier, protocol, packaging, codec ladder, DRM, and CDN strategy right — and a
pipeline that plays smoothly (low rebuffering, fast startup) across devices without
egress cost blowing up.

## What this plugin gives you

- **The right latency tier + protocol** — an honest interrogation of the latency
  requirement (most "real-time" isn't), then the protocol: standard HLS/DASH
  (~10–30s, scales cheapest), LL-HLS/LL-DASH (~2–6s), or WebRTC (<1s, interactive).
- **Package once with CMAF** — one set of fragmented-MP4 segments serving both HLS
  and DASH, encrypted once with **CBCS** to drive Widevine + FairPlay + PlayReady —
  no parallel rendition trees, no triple encryption.
- **A codec ladder for reach vs cost** — H.264 baseline for universal reach, HEVC/AV1
  where the device base and egress savings justify them, with keyframes aligned
  across rungs so ABR switches cleanly.
- **QoE that's measured, not guessed** — startup time, rebuffer ratio, and error rate
  from player analytics, with a diagnosis chain from ladder/keyframes to
  segment-duration to cache-miss to ABR logic. Egress-cost-aware throughout.

## The two agents

| Agent | Owns |
|---|---|
| `streaming-media-architect` | The delivery design: live-vs-VOD, latency tier, protocol & packaging (HLS/LL-HLS/DASH/CMAF/WebRTC), codec ladder, DRM, CDN topology, and the QoE/cost plan. |
| `media-pipeline-engineer` | The build: the ffmpeg transcode/ABR ladder, CMAF packaging + HLS/DASH manifests, DRM integration, player/ABR wiring, CDN/origin config, and QoE diagnosis. |

## The three skills

| Skill | What's inside |
|---|---|
| `design-streaming-delivery` | Interrogate latency → tier → protocol/packaging → DRM → codec ladder → CDN/QoE/cost. The first step of any delivery build. |
| `build-transcode-ladder` | The ffmpeg ladder (rungs, codec, aligned GOPs), CMAF→HLS+DASH packaging, DRM, and manifest validation + per-platform playback tests. |
| `diagnose-playback-qoe` | Root-cause rebuffering / slow startup / ABR thrash / errors from player analytics, along the delivery chain. |

## When to use it

- You're building live or VOD streaming and need the latency tier, protocol,
  packaging, DRM, and CDN strategy decided before you build.
- You're setting up the transcode ladder and packaging and want ABR that switches
  cleanly (aligned keyframes) and multi-DRM done once (CBCS).
- Users are rebuffering or streams start slowly, and you need a root cause from the
  player metrics, not encoder guesses.

## When *not* to use it

- You're building Kafka/Flink/Kinesis *data* streams — that's
  `data-streaming-engineering`. The name collides; the domains don't.
- You're editing / color-grading / mastering the content — that's
  `film-video-production`. This plugin ships what production made.
- You're building the player *UI* (the app around the video element) — that's
  `frontend-engineering`. This plugin owns delivery + ABR/DRM wiring.

## Seams to neighbouring plugins

- **`data-streaming-engineering`** — Kafka/Flink *data* streams (a different domain).
- **`film-video-production`** — content creation/editing (upstream of delivery).
- **`frontend-engineering`** — the player UI around the video element.
- **`finops-cloud-cost`** — egress / CDN / encode cost modeling at scale.
- **`observability-sre`** — streaming-infra reliability and on-call.
- **`computer-vision-engineering`** — frame analysis (detection/OCR) on the stream.
- **`ravenclaude-core`** — the domain-neutral constitution + protocols.

## Requires

- `ravenclaude-core@>=0.7.0`.

See [`CLAUDE.md`](CLAUDE.md) for the team constitution and house opinions.
