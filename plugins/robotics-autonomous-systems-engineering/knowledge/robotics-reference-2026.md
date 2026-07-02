# Robotics & Autonomous Systems — 2026 Reference

> Dated reference for the `robotics-autonomous-systems-engineering` team: the landscape and specifics agents reach for. The durable reasoning lives in [`robotics-decision-trees.md`](robotics-decision-trees.md); this file is the freshness-anchored "what the versions, specs, and standards are."
>
> **Engineering, not functional-safety certification or legal advice.** Every ROS 2 distro/DDS detail, sensor/compute spec, and functional-safety standard clause below is **volatile and vendor-/version-specific**. Each row carries a **source placeholder + retrieval date + `[verify-at-use]`** — re-confirm against the vendor datasheet, the distro release notes, or the current standard text before it drives an architecture, a bill of materials, or a safety argument. Estimates are marked `[ESTIMATE]`. No PII.
>
> _Last reviewed: 2026-07-02 by `claude`. Treat every specific as `[verify-at-use]` unless re-confirmed this session._

---

## 1. ROS 2 distro & DDS/RMW landscape

| Item | Concept (durable) | Source / retrieved | Flag |
|---|---|---|---|
| ROS 2 distro to target | ROS 2 ships time-based releases with LTS distros on a published support window; pick a distro still in support for your platform | _<source placeholder — ROS 2 releases / REP-2000>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| ROS 1 status | ROS 1 is at end of life; new work targets ROS 2 | _<source placeholder — Open Robotics EOL notice>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| RMW / DDS vendors | Multiple DDS implementations back ROS 2 via the RMW layer; each has different QoS/discovery/perf tradeoffs and a default per distro | _<source placeholder — RMW vendor docs>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| QoS profiles | Reliability, durability, history/depth, deadline, liveliness; publisher/subscriber must be compatible or they don't connect | _<source placeholder — ROS 2 QoS docs>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| micro-ROS | Brings ROS 2 concepts to microcontrollers via a client library + agent; the MCU boundary of a ROS 2 graph | _<source placeholder — micro-ROS docs>_ — retrieved 2026-07-02 | `[verify-at-use]` |

> **Durable rule:** target a supported ROS 2 distro, choose the RMW/DDS on the QoS and platform needs, and treat every version-specific default as `[verify-at-use]`.

---

## 2. Frame conventions & standards references (REP)

| Item | Concept (durable) | Source / retrieved | Flag |
|---|---|---|---|
| REP 103 | Standard units (SI) and axis orientations (right-handed, x-forward/y-left/z-up) | _<source placeholder — REP 103>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| REP 105 | Coordinate-frame semantics: `map` → `odom` → `base_link` and the guarantees of each | _<source placeholder — REP 105>_ — retrieved 2026-07-02 | `[verify-at-use]` |

> Frame conventions rarely change, but confirm the exact semantics against the REP before treating them as contract.

---

## 3. Sensor & compute options `[ESTIMATE]`

| Class | Concept | Source / retrieved | Flag |
|---|---|---|---|
| Lidar | Geometry / range; 2D vs 3D, mechanical vs solid-state; range, resolution, rate vary widely by model | _<source placeholder — vendor datasheet>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| Camera / depth | Semantics + depth (stereo, structured-light, ToF); exposure, FOV, rolling shutter matter for perception | _<source placeholder — vendor datasheet>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| IMU | High-rate motion; bias/noise (bias-instability, random walk) drives estimator tuning | _<source placeholder — vendor datasheet>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| GNSS / RTK | Global position; RTK gives cm-class fix with a base/correction — availability/accuracy environment-dependent | _<source placeholder — vendor datasheet>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| Onboard compute | CPU for the graph + GPU/accelerator for perception; thermal and power budgets are real constraints | _<source placeholder — vendor spec>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |

> These are planning anchors, not quotable specs — confirm the exact model's numbers on the datasheet and, where it matters, measure on the target.

---

## 4. Functional-safety standard pointers

| Standard (pointer) | What it broadly covers (durable, non-authoritative) | Source / retrieved | Flag |
|---|---|---|---|
| ISO 12100 | General principles for design risk assessment and risk reduction of machinery | _<source placeholder — ISO 12100>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| ISO 13849 | Safety-related parts of control systems; performance levels (PL) and categories | _<source placeholder — ISO 13849>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| ISO 10218 (+ TS 15066) | Industrial robots and robot systems; collaborative-operation guidance | _<source placeholder — ISO 10218 / TS 15066>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Application/sector standards | Service robots, AGV/AMR, drones, and automotive (e.g. ISO-family functional safety) each have their own standards | _<source placeholder — sector standard>_ — retrieved 2026-07-02 | `[verify-at-use]` |

> **These pointers are orientation only — not the standard text and not certification.** The applicable standard, its current edition, and the required performance/integrity level for a given machine are **`[verify-at-use]`** against the standard and a qualified functional-safety engineer. A robot that can move can injure; do not quote a safety level from memory.

---

## 5. How to use this file

1. Find the distro/DDS detail, sensor/compute spec, or standard pointer you need.
2. Read its retrieval date — if stale or unconfirmed this session, **re-verify** against the cited source type before quoting.
3. Quote it with its flag (`[ESTIMATE]` / `[verify-at-use]`) intact when it informs an architecture, a BOM, or a safety argument.
4. For anything that drives a safety claim: confirm against the current standard and a qualified functional-safety engineer first.

---

## See also

- [`robotics-decision-trees.md`](robotics-decision-trees.md) — the durable middleware/planner/localization/real-time trees.
- Firmware/HAL seam: [`../../embedded-iot-engineering/CLAUDE.md`](../../embedded-iot-engineering/CLAUDE.md).
- Perception-model production seam: [`../../ml-engineering/CLAUDE.md`](../../ml-engineering/CLAUDE.md).
