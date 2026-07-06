# Streaming-Media Engineering — Decision Trees

> Reference decision trees for the `streaming-media-engineering` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Engineering judgment, not legal/DRM-licensing advice.** Anything touching a codec/protocol version, DRM system, CDN feature, player SDK, or QoE number is `[verify-at-use]` — confirm against the spec/vendor/SDK docs before it drives a build commitment. No PII.
>
> _Last reviewed: 2026-07-03 by `claude`. Principles are durable; dated specifics live in [`streaming-reference-2026.md`](streaming-reference-2026.md)._

---

## Decision Tree: VOD or live?

```mermaid
flowchart TD
    A[New streaming build] --> B{Is the content on-demand<br/>or produced live?}
    B -- "on-demand catalog" --> C[VOD<br/>pre-encode ladder, cache-friendly, cheapest at scale]
    B -- "live" --> D{Does the viewer interact,<br/>or is it one-way?}
    D -- "one-way linear/event" --> E{Latency sensitive?<br/>betting, live sports}
    D -- "interactive / two-way" --> F[Real-time path<br/>WebRTC — sub-second, harder to scale]
    E -- "no — a few seconds OK" --> G[Standard live<br/>HLS/DASH segments]
    E -- "yes — sub-few-second" --> H[Low-latency live<br/>LL-HLS / LL-DASH, chunked CMAF]
    C --> I[Design the origin/edge<br/>+ ABR ladder for cache-hit and egress]
    G --> I
    H --> I
    F --> I
```

**Rule:** decide VOD vs live on how the content is produced, then — for live — let **interactivity and the latency target** pick the path. VOD is cheapest and most cache-friendly; real-time (WebRTC) costs the most to scale. All protocol/latency specifics `[verify-at-use]`.

---

## Decision Tree: which protocol / packaging?

```mermaid
flowchart TD
    A[VOD or live decided] --> B{Required end-to-end latency?}
    B -- "sub-second, interactive" --> C[WebRTC]
    B -- "few seconds, live" --> D[LL-HLS / LL-DASH<br/>chunked CMAF]
    B -- "standard live or VOD" --> E{Device/browser reach?}
    E -- "must include Apple/Safari<br/>+ broad devices" --> F[HLS<br/>broadest reach, Apple-native]
    E -- "non-Apple / open ecosystem" --> G[MPEG-DASH<br/>open, flexible]
    F --> H{Also need DASH targets?}
    G --> H
    H -- yes --> I[Package CMAF once<br/>— shared fragments serve HLS + DASH]
    H -- no --> J[Single-format packaging;<br/>still prefer CMAF fragments]
```

**Rule:** the **latency target first, then the device/browser reach** pick the protocol. Reach for **CMAF** so one set of fragments serves both HLS and DASH — the cheap hedge. Confirm protocol/codec/DRM support on the target reach `[verify-at-use]` before committing.

---

## Decision Tree: which codec(s)?

```mermaid
flowchart TD
    A[Building the ABR ladder] --> B[H.264/AVC as the reach floor<br/>— plays almost everywhere]
    B --> C{Need bitrate efficiency<br/>for cost or 4K/HDR?}
    C -- no --> D[H.264 only<br/>simplest, widest reach]
    C -- yes --> E{Target devices support<br/>HEVC or AV1? verify-at-use}
    E -- "Apple/TV ecosystem,<br/>HEVC broadly supported" --> F[Add HEVC tier<br/>royalty considerations]
    E -- "web/Android, AV1 decode<br/>available" --> G[Add AV1 tier<br/>royalty-free, best efficiency, higher encode cost]
    E -- "legacy web needing VP9" --> H[Add VP9 tier]
    F --> I[Encode per-title;<br/>reach tier + efficiency tier, aligned GOPs]
    G --> I
    H --> I
    D --> I
```

**Rule:** ship a **reach tier (H.264) plus an efficiency tier (HEVC / AV1 / VP9)** chosen on the target devices' decode support and the cost/royalty trade — don't pick one codec and either starve reach or overpay egress. Codec support + encode cost `[verify-at-use]`.

---

## Decision Tree: which low-latency approach?

```mermaid
flowchart TD
    A[Live, latency matters] --> B{How low, and interactive?}
    B -- "sub-second, two-way" --> C[WebRTC<br/>sub-second; hardest to scale]
    B -- "~2-5 s, one-way at scale" --> D[LL-HLS / LL-DASH<br/>chunked CMAF over CDN]
    B -- "~10-30 s acceptable" --> E[Standard HLS/DASH<br/>cheapest, most robust at scale]
    C --> F{Can the CDN + player<br/>support it at your concurrency?}
    D --> F
    F -- no --> G[Relax the latency target<br/>or add SFU/edge support first]
    F -- yes --> H[Budget latency across<br/>encode/segment/transfer/CDN/player buffer]
    E --> H
```

**Rule:** pick the low-latency approach on **how low the latency must be and whether it's interactive**, then confirm the CDN and player support it at your concurrency. Lower latency trades scale and robustness — budget latency across the whole chain, not just the player, and don't chase the edge into rebuffering. Latency floors `[verify-at-use]`.

---

## See also

- [`streaming-reference-2026.md`](streaming-reference-2026.md) — dated codec/protocol/CDN/DRM/player landscape + QoE target ranges (verify-at-use).
- Skills: [`../skills/streaming-architecture-and-protocol-selection/SKILL.md`](../skills/streaming-architecture-and-protocol-selection/SKILL.md), [`../skills/transcoding-and-abr-ladder/SKILL.md`](../skills/transcoding-and-abr-ladder/SKILL.md), [`../skills/low-latency-live-streaming/SKILL.md`](../skills/low-latency-live-streaming/SKILL.md), [`../skills/playback-qoe-and-delivery/SKILL.md`](../skills/playback-qoe-and-delivery/SKILL.md).
