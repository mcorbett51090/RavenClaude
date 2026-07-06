# Changelog — streaming-media-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-03

Initial release.

### Added

- **3 agents** — `media-streaming-architect` (VOD vs live, protocol choice, packaging + origin/edge, single vs multi-CDN, DRM strategy, ABR-ladder philosophy, cost & scale), `transcoding-pipeline-engineer` (codec choice, FFmpeg pipelines, per-title & ABR-ladder encoding, GPU vs CPU, CMAF/fMP4 packaging, captions/subtitles, audio & loudness, transcode-farm scaling), `playback-and-delivery-engineer` (player integration, ABR tuning, QoE metrics, low-latency live, client DRM, CDN/edge cache tuning, playback analytics).
- **4 skills** — `streaming-architecture-and-protocol-selection`, `transcoding-and-abr-ladder`, `low-latency-live-streaming`, `playback-qoe-and-delivery`.
- **Knowledge bank** — `streaming-decision-trees.md` (4 Mermaid trees: VOD vs live, protocol choice, codec choice, low-latency approach) and `streaming-reference-2026.md` (dated reference: codec landscape, protocol/packaging landscape, CDN & DRM landscape, player-SDK landscape, QoE target ranges `[ESTIMATE]` — each with source placeholder + retrieval date + verify-at-use).
- **5 best-practices** — choose the protocol from latency and reach, design the ABR ladder per-title not fixed, measure QoE by rebuffer and startup not just bitrate, DRM and packaging are architecture decide early, test across devices and network conditions.
- **2 templates** — streaming-architecture, abr-ladder-plan.
- **2 commands** — `/choose-streaming-stack`, `/plan-abr-ladder`.

### Scope & verify-at-use

- **Engineering judgment, not legal, DRM-licensing, or content-rights advice.** The agents store no PII.
- The codec / protocol / CDN / DRM / player landscape is volatile — every codec/version claim, protocol/packaging support statement, DRM detail, CDN feature, player-SDK version, and QoE target in `streaming-reference-2026.md` carries a retrieval date + `[verify-at-use]`; re-confirm against the spec/vendor/SDK docs before quoting or committing.
- Distinct from `film-video-production` (creative-ops) and `data-streaming-engineering` (Kafka/event streams). Seams to `film-video-production`, `data-streaming-engineering`, `performance-engineering`, `aws-cloud`, and `observability-sre`.
