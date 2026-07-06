# Measure QoE at the player

**Rule.** Judge delivery by **player-side QoE** — startup time, rebuffer ratio,
average delivered bitrate, error/exit-before-video rate — from player analytics, not
by encoder-side quality metrics. Instrument these before diagnosing any playback problem.

**Why.** Encoder VMAF/PSNR tells you the file looks good; it doesn't tell you whether
users can watch it smoothly. Rebuffer ratio and startup time are what drive
engagement and churn.

**Smell.** "Quality is fine, VMAF is 95" as a response to a rebuffering complaint; no
player instrumentation, so QoE is guessed.

**Cite:** plugin §4.5; the QoE section in
`knowledge/streaming-codecs-protocols-and-cdn-2026.md`; the `diagnose-playback-qoe` skill.
