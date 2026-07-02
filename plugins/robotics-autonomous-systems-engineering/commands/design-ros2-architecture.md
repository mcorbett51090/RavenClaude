---
description: "Design a robot's ROS 2 system architecture — the computation graph, DDS/RMW & QoS, compute/sensor topology, the real-time split, and the safety architecture — with every distro/standard specific flagged verify-at-use."
argument-hint: "[robot task + kinematics + sensors + compute + environment + safety class]"
---

You are running `/robotics-autonomous-systems-engineering:design-ros2-architecture`. Use `robotics-architect-lead` + the `ros2-architecture-and-dds` and `sim-to-real-and-safety` skills.

> Engineering decision-support, not functional-safety certification. Every standard clause, distro/DDS detail, and sensor/compute spec is `[verify-at-use]`. No PII.

## Steps
1. Capture the robot: task, kinematics, sensors, compute, environment, and safety class.
2. **Fix the coordinate frames first** — the TF tree and REP 103/105 conventions (`[verify-at-use]`).
3. Traverse the **ROS 2 vs ROS 1 vs custom middleware** and **real-time execution path** trees in `knowledge/robotics-decision-trees.md`.
4. Decide: the node graph and its boundaries, the RMW/DDS + per-topic QoS, the compute/sensor topology, the real-time split (what is deterministic and how it's isolated), and the safety architecture in layers — each vendor/distro/standard specific flagged `[verify-at-use]`.
5. Name the sim-to-real plan (simulator, what's validated before actuation, how the gap is measured).
6. Emit using `templates/robot-system-architecture.md` (and `templates/ros2-node-graph-plan.md` for the graph detail) + the Structured Output block.
