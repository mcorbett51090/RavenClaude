# Robot System Architecture — <robot / program>

> Output template for a whole-robot architecture record. One per robot/program (revise as it evolves). **Engineering decision-support, not functional-safety certification.** Every standard clause, distro/DDS detail, and sensor/compute spec is `[verify-at-use]`. No PII.

## Context
- **Robot / program:** _____  · **Prepared:** 2026-__-__
- **Task & environment:** _what it does, where, around whom_
- **Safety class / applicable standard (verify-at-use):** _____ `[verify-at-use]`

## 1. Coordinate frames (first)
| Frame | Parent | Published by | Static/dynamic |
|---|---|---|---|
| `base_link` | | | |
| `odom` | | | |
| `map` | | | |
| _sensor frames…_ | | | |
- **Conventions:** REP 103 (units/axes), REP 105 (frame semantics) — `[verify-at-use]`

## 2. Compute & sensors
| Component | Choice | Why | Spec source (verify-at-use) |
|---|---|---|---|
| Main compute (CPU) | | | |
| Accelerator (GPU/other) | | | |
| Lidar / range | | | |
| Camera / depth | | | |
| IMU | | | |
| GNSS / RTK | | | |
| Actuator/MCU boundary | | | |

## 3. ROS 2 middleware & the real-time split
- **Distro (verify-at-use):** _____  · **RMW/DDS:** _____ `[verify-at-use]`
- **Hard real-time (deterministic):** _control loop / safety monitor — isolation + kernel/MCU_
- **Best-effort:** _perception / planning / logging_
- **Node composition:** _which nodes share a process (intra-process) vs isolated_

## 4. Safety architecture (layers, not one e-stop)
- **Risk assessment (ISO 12100 style) done?** ☐  · **Applicable standard + required PL/level (verify-at-use):** _____
- **Monitored safe state (independent path):** _____
- **Bounded actuation limits (below the planner):** _____
- **Degraded modes (per failure: sensor loss / estimate divergence / comms loss):** _____
- **E-stop (last layer):** _____

## 5. Sim-to-real plan
- **Simulator:** _____  · **Validated in sim before actuation:** _behaviors + failure cases_
- **Reality-gap sources:** _dynamics / sensor noise / latency_ · **How measured/closed:** _____

## 6. Verify-at-use flags
- _List every standard clause, distro/DDS default, and sensor/compute spec relied on — each re-confirmed against the standard, datasheet, or a measurement._

## Headline + next steps
- **Headline:** _the defining architectural decision and why_
- **Top 2 actions:** _action — owner — the sim/on-robot test that proves it — by when_

---
_Plus the ravenclaude-core Structured Output block. Safety determinations belong to a qualified functional-safety engineer._
