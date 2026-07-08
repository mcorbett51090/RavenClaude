---
name: low-latency-live-streaming
description: "Hit a live-streaming latency target: pick the approach (standard HLS/DASH, LL-HLS/LL-DASH with chunked CMAF, or WebRTC for sub-second/interactive) from the required end-to-end latency and scale, then budget latency across capture/encode, segment & part duration, chunked transfer, live origin, CDN, and the player live-edge buffer — trading latency against rebuffer risk deliberately. Protocol/latency specifics verify-at-use."
---

# Low-Latency Live Streaming

The discipline of hitting a live latency target without trading it for rebuffering. The required end-to-end latency and the concurrency you must serve pick the approach; the latency is then spent across the whole chain, not just the player.

> **Engineering judgment.** Protocol latency floors, chunked-transfer support, and player live-edge behavior move with spec and SDK versions — every latency number and support claim here is `[verify-at-use]`. No PII.

## Workflow

1. **State the required end-to-end latency and scale.** "Glass-to-glass" seconds and peak concurrency decide the approach; sub-second interactive is a different architecture from few-second live.
2. **Pick the approach.** Standard HLS/DASH (highest latency, cheapest at scale), LL-HLS / LL-DASH with chunked CMAF (few-second, CDN-scalable), or WebRTC (sub-second, interactive, harder to scale). Name the trade — lower latency costs scale and robustness.
3. **Budget latency across the chain.** Capture/encode, segment + part duration, chunked transfer, live origin/packager, CDN delivery, and the player's live-edge target buffer each add latency. Attack the biggest term, not the easiest.
4. **Tune the client and edge together.** A player chasing the live edge too hard trades latency for rebuffering; the edge must support chunked/partial-segment delivery. Tune both against the QoE targets from `playback-qoe-and-delivery`.
5. **Validate under real network + scale.** Low-latency live degrades fastest on poor networks and at peak concurrency — measure glass-to-glass and rebuffer together, not in isolation.

## Metrics table

| Metric | Target/read | Flag |
|---|---|---|
| Glass-to-glass latency (s) | Meets the stated target | `[verify-at-use]` per approach |
| Segment / part duration (s) | Small enough for the target, big enough for cache | `[verify-at-use]` |
| Live-edge rebuffer ratio | Low at target latency | `[ESTIMATE]` |
| CDN chunked-transfer support | Required for LL-HLS/LL-DASH | `[verify-at-use]` per CDN |
| Peak concurrency the approach holds | Within scale budget | `[verify-at-use]` |

## Anti-patterns

- Choosing WebRTC for one-way live at massive scale because it's lowest latency — paying interactive cost you don't need.
- Chasing the live edge so hard the player rebuffers on any jitter.
- Cutting segment duration without confirming CDN chunked-transfer support.
- Measuring latency on a perfect network and ignoring rebuffer at the edge.

## See also

- Traverse the **low-latency approach** tree in [`../../knowledge/streaming-decision-trees.md`](../../knowledge/streaming-decision-trees.md).
- Dated protocol/latency landscape: [`../../knowledge/streaming-reference-2026.md`](../../knowledge/streaming-reference-2026.md).
- Sibling skills: [`../streaming-architecture-and-protocol-selection/SKILL.md`](../streaming-architecture-and-protocol-selection/SKILL.md), [`../playback-qoe-and-delivery/SKILL.md`](../playback-qoe-and-delivery/SKILL.md).
- Best practices: [`../../best-practices/choose-the-protocol-from-latency-and-reach.md`](../../best-practices/choose-the-protocol-from-latency-and-reach.md), [`../../best-practices/measure-qoe-rebuffer-and-startup-not-just-bitrate.md`](../../best-practices/measure-qoe-rebuffer-and-startup-not-just-bitrate.md).
- Live-service SLOs & observability: [`../../../observability-sre/CLAUDE.md`](../../../observability-sre/CLAUDE.md).
