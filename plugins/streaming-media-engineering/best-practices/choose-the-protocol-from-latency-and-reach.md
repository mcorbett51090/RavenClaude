# Choose the protocol from latency and reach

**Status:** Pattern
**Domain:** Architecture / protocol selection
**Applies to:** `streaming-media-engineering`

> Engineering rule. Protocol/DRM/CDN specifics are `[verify-at-use]`. No PII.

---

## Why this exists

The streaming protocol is one of the most expensive decisions to reverse, and it is routinely chosen on fashion ("everyone's doing low-latency") rather than requirements. Two things actually decide it: the **required end-to-end latency** and the **device/browser reach** you must serve. A one-way catalog on WebRTC pays real-time cost for latency it doesn't need; a low-latency live event on standard HLS misses its target. Get these two inputs right and the protocol nearly picks itself.

## How to apply

- Establish the required glass-to-glass latency first (standard / low-latency / real-time), then the device/browser reach matrix.
- Map: WebRTC for sub-second interactive, LL-HLS/LL-DASH for few-second live at scale, HLS/DASH for standard live and VOD.
- Reach for **CMAF** so one set of fragments serves both HLS and DASH — the cheap hedge against forking formats (`[verify-at-use]` support on target).
- Name the trade explicitly: lower latency costs scale, robustness, and complexity.

**Do:** let latency + reach pick the protocol; package CMAF once.
**Don't:** choose WebRTC for one-way-at-scale because it's "lowest latency"; fork HLS and DASH packaging when CMAF serves both.

## Edge cases / when the rule does NOT apply

A hard interactivity requirement (conferencing, betting, auctions) forces the real-time path regardless of scale cost — there the latency requirement is non-negotiable and the rule simply names the price you're paying.

## See also

- [`../skills/streaming-architecture-and-protocol-selection/SKILL.md`](../skills/streaming-architecture-and-protocol-selection/SKILL.md), [`../skills/low-latency-live-streaming/SKILL.md`](../skills/low-latency-live-streaming/SKILL.md)
- Template: [`../templates/streaming-architecture.md`](../templates/streaming-architecture.md)

## Provenance

Codifies `media-streaming-architect` house opinion and the VOD-vs-live + protocol-choice decision trees. Protocol/latency specifics: [`../knowledge/streaming-reference-2026.md`](../knowledge/streaming-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-03 by `claude`_
