# robotics-autonomous-systems-engineering — best-practice docs

Named, citable rules for the `robotics-autonomous-systems-engineering` team's specialists. Each file is **one rule**. Engineering decision-support — not functional-safety certification or legal advice; standard/distro/sensor specifics are `[verify-at-use]`; no PII.

---

## Index

_5 rules across architecture, real-time, testing, perception, and safety._

| Doc | Status | Use when |
|---|---|---|
| [`design-the-coordinate-frames-before-the-code.md`](./design-the-coordinate-frames-before-the-code.md) | Absolute rule | Starting any robot — fix the TF tree and frame conventions before writing nodes. |
| [`real-time-is-an-architecture-decision-not-a-flag.md`](./real-time-is-an-architecture-decision-not-a-flag.md) | Absolute rule | Any deterministic loop (control, safety monitor) — decide and isolate real-time at design time. |
| [`simulate-before-you-actuate.md`](./simulate-before-you-actuate.md) | Absolute rule | Any new behavior — validate it in sim before it touches real actuators. |
| [`sensor-fusion-beats-a-better-sensor.md`](./sensor-fusion-beats-a-better-sensor.md) | Pattern | Perception/estimation gaps — fuse complementary modalities before buying a better sensor. |
| [`safety-is-a-system-property-not-an-estop.md`](./safety-is-a-system-property-not-an-estop.md) | Absolute rule | Any machine that can move — build the safety architecture in layers, not one e-stop. |

---

Each rule cites its provenance and carries a `Last reviewed` date. Volatile standard/distro/sensor specifics live (dated, verify-at-use) in [`../knowledge/robotics-reference-2026.md`](../knowledge/robotics-reference-2026.md).
