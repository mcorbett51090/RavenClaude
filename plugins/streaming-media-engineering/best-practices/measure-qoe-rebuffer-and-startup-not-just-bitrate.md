# Measure QoE by rebuffer and startup, not just bitrate

**Status:** Absolute rule
**Domain:** Playback / QoE
**Applies to:** `streaming-media-engineering`

> Engineering rule. Player/CDN/QoE specifics are `[verify-at-use]`. No PII.

---

## Why this exists

Average bitrate is the metric that's easiest to report and most misleading to optimize. Viewers abandon on the spinner, not on slightly softer video — so a stream that maximizes bitrate while occasionally rebuffering delivers a *worse* experience than one that holds a slightly lower, stable bitrate. Quality-of-experience is dominated by **video-startup time**, **rebuffer ratio**, and **video-start-failures (VSF)**; average bitrate is a supporting metric, not the headline. Optimize the experience the viewer feels.

## How to apply

- Instrument QoE analytics (startup time, rebuffer ratio/count, average bitrate, VSF) **before** tuning — you can't tune what you don't measure.
- Tune the ABR algorithm for stability first: sensible start bitrate, switch thresholds that don't oscillate, caps matched to the audience.
- Treat rebuffering as the primary failure and startup as the primary friction; use bitrate as a tiebreaker, not the target.
- Set concrete QoE targets from your own analytics baseline (`[verify-at-use]` — ranges are directional, not universal SLAs).

**Do:** ship analytics first; optimize for low rebuffer + fast startup.
**Don't:** chase peak bitrate at the cost of rebuffering; tune ABR on anecdotes.

## Edge cases / when the rule does NOT apply

For a premium, controlled-network context (e.g. in-venue or managed devices) where rebuffering is effectively absent, pushing bitrate/fidelity harder is legitimate — but only once the QoE floor is measured and confirmed stable.

## See also

- [`../skills/playback-qoe-and-delivery/SKILL.md`](../skills/playback-qoe-and-delivery/SKILL.md), [`../skills/low-latency-live-streaming/SKILL.md`](../skills/low-latency-live-streaming/SKILL.md)
- Live-service SLOs & observability: [`../../observability-sre/CLAUDE.md`](../../observability-sre/CLAUDE.md)

## Provenance

Codifies `playback-and-delivery-engineer` house opinion. QoE target ranges: [`../knowledge/streaming-reference-2026.md`](../knowledge/streaming-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-03 by `claude`_
