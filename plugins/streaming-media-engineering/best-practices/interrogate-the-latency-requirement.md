# Interrogate the latency requirement

**Rule.** Pin the *real* latency need before choosing a protocol. Ask what breaks at
10–30s. Standard HLS/DASH (broadcast) → LL-HLS/LL-DASH (~2–6s) → WebRTC (<1s,
interactive) — each step down costs scale, cost, and complexity.

**Why.** Most "we need real-time" is really "a few seconds is fine". WebRTC needs an
SFU tier and doesn't scale or cost like HTTP streaming; using it for a one-way
broadcast pays an order-of-magnitude tax for latency nobody needed.

**Smell.** WebRTC chosen for a one-way live stream; "real-time" asserted without
anyone naming what breaks at 20s.

**Cite:** plugin §4.1; the latency-tier→protocol tree in
`knowledge/latency-tier-to-protocol-decision-tree.md`.
