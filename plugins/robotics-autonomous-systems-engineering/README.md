# robotics-autonomous-systems-engineering

A RavenClaude plugin: a **robotics & autonomous-systems engineering** specialist team for the three engines of a robot program — the system architecture, the motion stack, and the perception & autonomy stack.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Engineering decision-support — not legal, regulatory, or functional-safety-certification advice.** Functional-safety standard clauses (ISO 10218, ISO 13849, and related), the ROS 2 distro / DDS landscape, and sensor/compute specs are volatile and vendor-/version-specific: each carries a retrieval date + `[verify-at-use]` and must be confirmed against the standard, the datasheet, or a measurement on the target before it drives a safety argument, a bill of materials, or a real-time budget. A robot that can move can injure — the binding safety determination belongs to a qualified functional-safety engineer. This plugin stores no PII.

## What it's for

Getting a robot from a simulation and a whiteboard graph to a machine that senses, plans, and actuates safely: a clean ROS 2 computation graph on the right middleware and compute, a real-time split that isolates what must be deterministic, a motion stack (Nav2 / MoveIt) that plans smooth trajectories against a correct TF tree, a perception stack that fuses sensors into a stable state estimate, and a safety architecture that is a system property rather than a single e-stop.

## Agents

| Agent | Use for |
|---|---|
| **robotics-architect-lead** | System architecture: ROS 2 graph & DDS, compute/sensor selection, the real-time vs non-real-time split, safety architecture, sim-to-real strategy |
| **ros-motion-planning-engineer** | ROS 2 nodes/topics/actions, motion planning (MoveIt/Nav2), kinematics, control loops (PID/MPC), coordinate frames/TF |
| **perception-and-autonomy-engineer** | Perception (sensor fusion, SLAM, state estimation/EKF), object detection, localization, autonomy behavior (behavior trees / state machines) |

## What's inside

- **4 skills** — ros2-architecture-and-dds, motion-planning-and-control, perception-and-state-estimation, sim-to-real-and-safety.
- **Knowledge bank** — [`robotics-decision-trees.md`](knowledge/robotics-decision-trees.md) (4 Mermaid trees: middleware choice, motion-planner choice, localization-stack choice, real-time execution path) + [`robotics-reference-2026.md`](knowledge/robotics-reference-2026.md) (dated reference, verify-at-use).
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **2 templates** — robot system architecture, ROS 2 node-graph plan.
- **2 commands** — `/design-ros2-architecture`, `/plan-motion-stack`.

## Seams

Firmware / HAL / `micro-ROS` on a microcontroller → [`embedded-iot-engineering`](../embedded-iot-engineering/) · training the perception model itself → [`ml-engineering`](../ml-engineering/) · hot-path profiling & latency budgets → [`performance-engineering`](../performance-engineering/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install robotics-autonomous-systems-engineering@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for the engineering scope, routing rules, house opinions, and the output contract.
