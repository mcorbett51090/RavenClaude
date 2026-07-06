# Align keyframes across the ladder

**Rule.** Every rung in the ABR ladder must have aligned IDR/keyframes at the segment
boundary, with fixed closed GOPs. Set this at encode time, matched to the segment
duration for the latency tier.

**Why.** Aligned keyframes are what let a player switch rungs cleanly. Misaligned
GOPs are a top cause of rebuffering and failed ABR switches — and they look like a
"player bug" until you check the encode.

**Smell.** Rungs encoded with different/variable GOPs; rebuffering at rung switches
blamed on the player before the encode settings are checked.

**Cite:** plugin §4.4; the ladder rules in
`knowledge/streaming-codecs-protocols-and-cdn-2026.md`; the `build-transcode-ladder` skill.
