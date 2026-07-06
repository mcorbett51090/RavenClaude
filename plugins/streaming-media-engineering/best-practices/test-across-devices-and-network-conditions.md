# Test across devices and network conditions

**Status:** Absolute rule
**Domain:** Playback / delivery / QA
**Applies to:** `streaming-media-engineering`

> Engineering rule. Player/CDN/device specifics are `[verify-at-use]`. No PII.

---

## Why this exists

The reference player on a flagship phone over office wifi is a comforting lie. Real audiences watch on mid-tier and old devices, on smart TVs with weak decoders, and over throttled, jittery, high-latency networks — and that is exactly where ABR misbehaves, codecs fall back, DRM fails, and startup drags. A build validated only on the happy path ships rebuffering and playback failures to the majority of its viewers. Coverage across the **device matrix and network conditions** is where playback quality is actually proven.

## How to apply

- Test the real device matrix: OS/browser versions, smart TVs, old and mid-tier hardware — not just the newest flagship (`[verify-at-use]` per player/SDK).
- Test throttled, lossy, and high-latency networks, and network *transitions* (wifi↔cellular), not just fast wifi.
- Verify codec and DRM fallbacks actually trigger and degrade gracefully on unsupported devices.
- Measure QoE (rebuffer, startup, VSF) per device/network segment, and gate release on the long-tail numbers, not the aggregate.

**Do:** validate on the long tail; test network transitions and DRM/codec fallback.
**Don't:** sign off on the reference player + office wifi; report only aggregate QoE that hides the tail.

## Edge cases / when the rule does NOT apply

A fully managed device fleet on a known network (kiosks, in-venue, set-top boxes you control) narrows the matrix legitimately — but you still test the *actual* devices and network in the field, not a developer laptop standing in for them.

## See also

- [`../skills/playback-qoe-and-delivery/SKILL.md`](../skills/playback-qoe-and-delivery/SKILL.md), [`../skills/transcoding-and-abr-ladder/SKILL.md`](../skills/transcoding-and-abr-ladder/SKILL.md)
- Deep profiling methodology: [`../../performance-engineering/CLAUDE.md`](../../performance-engineering/CLAUDE.md)

## Provenance

Codifies `playback-and-delivery-engineer` house opinion. Device/player specifics: [`../knowledge/streaming-reference-2026.md`](../knowledge/streaming-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-03 by `claude`_
