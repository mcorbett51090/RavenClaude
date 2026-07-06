# Treat egress as the bill

**Rule.** Model CDN egress cost on any at-scale streaming design, and treat codec
efficiency, ladder design, and cache-hit ratio as **cost** levers, not just quality
levers. Loop in `finops-cloud-cost` for at-scale delivery.

**Why.** CDN egress usually dominates the streaming bill. A more efficient codec
(HEVC/AV1), a tighter ladder, and a higher cache-hit ratio cut bytes served — often
a bigger lever than the encode cost they add.

**Smell.** An at-scale delivery design with no egress cost model; adding top-bitrate
rungs no one watches; a low cache-hit ratio hammering origin egress.

**Cite:** plugin §4.6; the CDN/cost section in
`knowledge/streaming-codecs-protocols-and-cdn-2026.md`.
