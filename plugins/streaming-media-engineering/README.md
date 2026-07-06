# streaming-media-engineering

A RavenClaude plugin: a **streaming-media (video/audio) engineering** specialist team for the three engines of a streaming build — system architecture, transcoding, and playback & delivery.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Engineering judgment — not legal, DRM-licensing, or content-rights advice.** The codec / protocol / CDN / DRM / player landscape is volatile: every codec/version claim, protocol/packaging support statement, DRM detail, CDN feature, player-SDK version, and QoE target carries a retrieval date + `[verify-at-use]` and must be confirmed against the spec/vendor/SDK docs before it drives a build commitment. The agents store no PII.

## What it's for

Building streaming media well: choosing VOD vs live and the protocol you won't have to reverse (HLS / MPEG-DASH / CMAF / WebRTC / LL-HLS), designing an encoding ladder per-title so you don't waste bits, packaging and DRM decided early instead of retrofitted, a CDN strategy that holds at scale, and playback tuned for quality-of-experience — low startup time, low rebuffering, stable bitrate — across the long tail of devices and networks.

**Distinct from its neighbors:** `film-video-production` is the creative-ops plugin (camera, editorial, post); `data-streaming-engineering` is Kafka/event-stream data pipelines. This plugin is the *media delivery* engineering team — encoding, packaging, DRM, CDN, and playback QoE.

## Agents

| Agent | Use for |
|---|---|
| **media-streaming-architect** | VOD vs live, protocol choice (HLS / DASH / CMAF / WebRTC / LL-HLS), packaging + origin/edge, single vs multi-CDN, DRM strategy (Widevine / FairPlay / PlayReady), ABR-ladder philosophy, cost & scale |
| **transcoding-pipeline-engineer** | Codec choice (H.264 / HEVC / AV1 / VP9), FFmpeg pipelines, per-title & ABR-ladder encoding, GPU vs CPU, CMAF/fMP4 packaging, captions/subtitles, audio & loudness, transcode-farm scaling |
| **playback-and-delivery-engineer** | Player integration (hls.js / dash.js / Shaka / ExoPlayer / AVPlayer), ABR tuning, QoE metrics (rebuffer/startup/VSF), low-latency live, client DRM, CDN/edge cache tuning, playback analytics |

## What's inside

- **4 skills** — streaming-architecture-and-protocol-selection, transcoding-and-abr-ladder, low-latency-live-streaming, playback-qoe-and-delivery.
- **Knowledge bank** — [`streaming-decision-trees.md`](knowledge/streaming-decision-trees.md) (4 Mermaid trees: VOD vs live, protocol choice, codec choice, low-latency approach) + [`streaming-reference-2026.md`](knowledge/streaming-reference-2026.md) (dated codec/protocol/CDN/DRM/player landscape + QoE target ranges, verify-at-use).
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **2 templates** — streaming architecture, ABR-ladder plan.
- **2 commands** — `/choose-streaming-stack`, `/plan-abr-ladder`.

## Seams

Creative production → [`film-video-production`](../film-video-production/) · Kafka/event streams → [`data-streaming-engineering`](../data-streaming-engineering/) · deep profiling → [`performance-engineering`](../performance-engineering/) · cloud infra → [`aws-cloud`](../aws-cloud/) · SLOs/observability → [`observability-sre`](../observability-sre/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install streaming-media-engineering@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for the scope, routing rules, house opinions, and the output contract.
