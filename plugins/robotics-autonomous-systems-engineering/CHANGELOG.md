# Changelog — robotics-autonomous-systems-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-02

Initial release.

### Added

- **3 agents** — `robotics-architect-lead` (system architecture: ROS 2 graph & DDS, compute/sensor selection, the real-time vs non-real-time split, safety architecture, sim-to-real strategy), `ros-motion-planning-engineer` (ROS 2 nodes/topics/actions, MoveIt/Nav2 motion planning, kinematics, PID/MPC control loops, coordinate frames/TF), `perception-and-autonomy-engineer` (sensor fusion, SLAM, EKF state estimation, object detection, localization, behavior-tree / state-machine autonomy).
- **4 skills** — `ros2-architecture-and-dds`, `motion-planning-and-control`, `perception-and-state-estimation`, `sim-to-real-and-safety`.
- **Knowledge bank** — `robotics-decision-trees.md` (4 Mermaid trees: ROS 2 vs ROS 1 vs custom middleware, motion-planner choice Nav2 vs MoveIt vs custom, localization-stack choice, real-time execution path) and `robotics-reference-2026.md` (dated reference: ROS 2 distro/DDS landscape, sensor/compute options, functional-safety standard pointers ISO 10218 / ISO 13849 — each with source placeholder + retrieval date + verify-at-use; estimates marked `[ESTIMATE]`).
- **5 best-practices** — design the coordinate frames before the code, real-time is an architecture decision not a flag, simulate before you actuate, sensor fusion beats a better sensor, safety is a system property not an e-stop.
- **2 templates** — robot-system-architecture, ros2-node-graph-plan.
- **2 commands** — `/design-ros2-architecture`, `/plan-motion-stack`.

### Scope & verify-at-use

- **Engineering decision-support, not legal, regulatory, or functional-safety-certification advice.** A robot that can move can injure — the binding safety determination belongs to a qualified functional-safety engineer / notified body. This plugin stores no PII.
- All functional-safety standard clauses (ISO 10218, ISO 13849, ISO 12100, and related), ROS 2 distro/DDS details, and sensor/compute specs in `robotics-reference-2026.md` are volatile and vendor-/version-specific — each carries a retrieval date + `[verify-at-use]`; re-confirm against the standard, the datasheet, or a measurement on the target before quoting or acting.
- Seams to `embedded-iot-engineering` (firmware/HAL/micro-ROS), `ml-engineering` (perception model production), and `performance-engineering` (hot-path optimization).
