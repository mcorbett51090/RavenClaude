---
name: playback-qoe-and-delivery
description: "Deliver playback quality-of-experience: integrate the player (hls.js / dash.js / Shaka / ExoPlayer / AVPlayer) to the chosen protocol and DRM, tune the ABR algorithm (buffer- vs throughput-based, start bitrate, switch thresholds, caps) for stability, measure QoE by rebuffer ratio / startup time / average bitrate / VSF, and tune CDN/edge cache (cache-key, TTL, prefetch) — all instrumented with playback analytics. Player/CDN/QoE specifics verify-at-use."
---

# Playback QoE & Delivery

The discipline of making the stream start fast, play smooth, and hold the highest sustainable bitrate — on the long tail of real devices and networks, not the reference player on fast wifi. Playback is where the whole pipeline is judged.

> **Engineering judgment.** Player-SDK APIs, DRM CDM behavior, and CDN features move with versions — every SDK version, ABR knob, and QoE number here is `[verify-at-use]`. No PII: delivery metrics, not viewer identity.

## Workflow

1. **Instrument QoE first.** Ship analytics beacons for video-startup time, rebuffer ratio/count, average bitrate, and video-start-failures (VSF) before tuning — you can't tune what you can't measure.
2. **Integrate the player to protocol + DRM.** Native HLS/AVPlayer on Apple, MSE players (hls.js/dash.js/Shaka) on web, ExoPlayer on Android — each with its EME/CDM path for client DRM. Degrade gracefully when a codec/DRM is unsupported.
3. **Tune the ABR for the experience.** Buffer-based vs throughput-based, start bitrate, switch-up/down thresholds, and max/min caps trade startup against rebuffer against bitrate. Defaults are a starting point, not an answer.
4. **Tune CDN/edge for startup.** Cache-key design, TTLs, segment cacheability, and prefetch decide cache-hit ratio and startup latency. A cold cache starts slow regardless of the encode.
5. **Validate on the long tail.** Measure across mid-tier devices and throttled networks; optimize the experience (rebuffer + startup), not the headline bitrate.

## Metrics table

| Metric | Target/read | Flag |
|---|---|---|
| Video-startup time (s) | Low — first-frame fast | `[ESTIMATE]` `[verify-at-use]` |
| Rebuffer ratio (%) | Near zero in sustained playback | `[ESTIMATE]` `[verify-at-use]` |
| Average bitrate vs available bandwidth | High but stable, no oscillation | `[verify-at-use]` |
| Video-start-failures (VSF %) | Near zero | `[ESTIMATE]` |
| CDN cache-hit ratio | High — segments served from edge | `[verify-at-use]` per CDN |

## Anti-patterns

- Tuning ABR before shipping QoE analytics — guessing on anecdotes.
- Optimizing average bitrate at the cost of rebuffering.
- Testing only on the flagship device and office wifi.
- Ignoring cache-key/TTL design and blaming the encode for slow startup.

## See also

- Traverse the **low-latency approach** tree (client side) in [`../../knowledge/streaming-decision-trees.md`](../../knowledge/streaming-decision-trees.md).
- Dated player/CDN/QoE landscape: [`../../knowledge/streaming-reference-2026.md`](../../knowledge/streaming-reference-2026.md).
- Sibling skills: [`../transcoding-and-abr-ladder/SKILL.md`](../transcoding-and-abr-ladder/SKILL.md), [`../low-latency-live-streaming/SKILL.md`](../low-latency-live-streaming/SKILL.md).
- Best practices: [`../../best-practices/measure-qoe-rebuffer-and-startup-not-just-bitrate.md`](../../best-practices/measure-qoe-rebuffer-and-startup-not-just-bitrate.md), [`../../best-practices/test-across-devices-and-network-conditions.md`](../../best-practices/test-across-devices-and-network-conditions.md).
- Deep profiling methodology: [`../../../performance-engineering/CLAUDE.md`](../../../performance-engineering/CLAUDE.md).
