# Budget latency on the target hardware

**Rule.** Treat latency/frame-rate as a design-time constraint, and always measure
it on the **deployment hardware** (Jetson / CPU / phone / browser) — never quote a
dev-GPU number for an edge budget. Measure a *sustained* run, not a 10-second burst.

**Why.** A model that can't hit the frame rate on the target device is the wrong
model, however accurate. Dev-GPU latency is meaningless for edge; edge devices
thermally throttle, so burst frame rate overstates sustained performance.

**Smell.** "It runs at 60fps" (on a dev GPU) for an on-device target; a benchmark
that ran for seconds standing in for a production workload.

**Cite:** plugin §4.3; the cloud-vs-edge tree in
`knowledge/cv-inference-deployment-and-tooling-2026.md`; the `optimize-cv-inference` skill.
