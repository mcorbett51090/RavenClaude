---
name: streaming-architecture-and-protocol-selection
description: "Choose VOD vs live and the streaming protocol (HLS / MPEG-DASH / CMAF / LL-HLS / WebRTC) on the use-case, latency target, and device/browser reach — then commit to a packaging format (CMAF hedge), an origin/edge design, a single-vs-multi-CDN strategy, and the multi-DRM matrix (Widevine / FairPlay / PlayReady) the reach implies. Protocol/DRM/CDN specifics verify-at-use."
---

# Streaming Architecture & Protocol Selection

The first and most expensive streaming decision: VOD vs live, the protocol, the packaging, the CDN, and the DRM. Everything downstream — the encoding ladder, the players, the latency the audience feels, the egress bill — is shaped by this choice, so make it deliberately.

> **Engineering judgment, protocol/DRM landscape is volatile.** Protocol support, DRM system reach, and CDN features change with browser, OS, and vendor releases. Every specific here is `[verify-at-use]` — confirm against the spec/vendor docs before it drives a build commitment. Not legal/DRM-licensing advice. No PII.

## Workflow

1. **State the use-case and the reach.** On-demand catalog, live linear, or interactive/real-time — and the device/browser matrix the audience actually uses. These fix the constraints.
2. **Decide VOD vs live, then the latency target.** For live, the required end-to-end latency (standard / low-latency / real-time) dominates the protocol choice more than anything else.
3. **Pick the protocol on latency + reach.** HLS (broadest reach, Apple-native), DASH (open, non-Apple), CMAF (shared-fragment hedge for both), LL-HLS/LL-DASH (few-second live), WebRTC (sub-second interactive). Name the trade.
4. **Decide DRM + packaging early.** Map reach to the multi-DRM matrix (Widevine / FairPlay / PlayReady) and package once (CMAF/CENC) to serve them. Retrofitting encryption is a rebuild.
5. **Design origin/edge and the CDN strategy.** Origin + mid-tier/shield + edge for cache-hit and cost; single-CDN (simple) vs multi-CDN (resilience/leverage at cost). Hand the ABR-ladder philosophy to `transcoding-and-abr-ladder`.

## Metrics table

| Decision input | What it tells you | Flag |
|---|---|---|
| Required end-to-end latency (s) | Standard vs low-latency vs real-time protocol | `[verify-at-use]` per protocol |
| Device/browser reach matrix | Which DRM systems + codecs are mandatory | `[verify-at-use]` |
| VOD vs live + concurrency | Origin/edge design and egress scale | `[verify-at-use]` |
| DRM reach (Widevine/FairPlay/PlayReady) | Packaging + key-delivery architecture | `[verify-at-use]` |
| CDN cache-hit ratio target | Single vs multi-CDN, shield tier, cost | `[ESTIMATE]` `[verify-at-use]` |

## Anti-patterns

- Choosing WebRTC for a one-way catalog because "it's lowest latency" — paying real-time cost for latency you don't need.
- Forking HLS and DASH packaging instead of hedging with CMAF.
- Deferring the DRM matrix until after packaging, then re-encrypting.
- Assuming single-CDN scales to launch concurrency without a failover plan.

## See also

- Traverse the **VOD vs live** and **protocol choice** trees in [`../../knowledge/streaming-decision-trees.md`](../../knowledge/streaming-decision-trees.md).
- Dated landscape: [`../../knowledge/streaming-reference-2026.md`](../../knowledge/streaming-reference-2026.md).
- Sibling skills: [`../transcoding-and-abr-ladder/SKILL.md`](../transcoding-and-abr-ladder/SKILL.md), [`../low-latency-live-streaming/SKILL.md`](../low-latency-live-streaming/SKILL.md).
- Best practices: [`../../best-practices/choose-the-protocol-from-latency-and-reach.md`](../../best-practices/choose-the-protocol-from-latency-and-reach.md), [`../../best-practices/drm-and-packaging-are-architecture-decide-early.md`](../../best-practices/drm-and-packaging-are-architecture-decide-early.md).
- Template: [`../../templates/streaming-architecture.md`](../../templates/streaming-architecture.md).
