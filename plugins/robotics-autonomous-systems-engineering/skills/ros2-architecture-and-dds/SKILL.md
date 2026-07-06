---
name: ros2-architecture-and-dds
description: "Design the ROS 2 computation graph: nodes and their boundaries, topics/services/actions, the RMW/DDS layer and per-topic QoS, executors & callback groups, node composition, and the real-time vs non-real-time split. QoS and the real-time boundary are architecture decisions, not runtime flags. Distro/DDS specifics are verify-at-use."
---

# ROS 2 Architecture & DDS

The ROS 2 graph is a set of nodes exchanging messages over DDS. The architecture is the choice of *where the boundaries fall* and *what guarantees each edge carries*.

> **Engineering, not certification.** RMW/DDS vendor behavior and distro defaults change by version — treat distro/DDS specifics as `[verify-at-use]`. Safety-bearing limits are bounded by the safety architecture, not by a QoS setting alone.

## The workflow

1. **Draw the graph.** Nodes as responsibilities, edges as topics (streams), services (request/response), or actions (long-running with feedback/cancel). Decide the process/host boundaries.
2. **Choose the communication primitive per edge.** Stream of sensor data → topic; a quick query → service; a goto/pick that takes seconds and can be cancelled → action. See [`../motion-planning-and-control/SKILL.md`](../motion-planning-and-control/SKILL.md) for the action-heavy motion side.
3. **Set QoS per topic on the data's needs.** Reliability (reliable vs best-effort), durability (volatile vs transient-local for latched state), history/depth, and deadline. A publisher/subscriber QoS mismatch means no connection or silent loss — QoS is part of the interface.
4. **Pick executors & callback groups.** Isolate a deterministic callback (control loop, safety monitor) into its own callback group / executor so a slow callback can't starve it. This is the real-time split in practice.
5. **Decide node composition.** Compose nodes into one process for intra-process zero-copy where latency/CPU matters; keep separate processes for fault isolation. Trade cost vs isolation explicitly.
6. **Cross the middleware decision with the tree.** Traverse the **ROS 2 vs ROS 1 vs custom middleware** and **real-time execution path** trees in [`../../knowledge/robotics-decision-trees.md`](../../knowledge/robotics-decision-trees.md) before committing.

## Metrics

| Metric | Reads | Note |
|---|---|---|
| End-to-end topic latency | Time from publish to subscriber callback | High/variable → executor contention or QoS/transport issue |
| Control-loop jitter | Deviation from the nominal loop period | Nonzero jitter on a safety loop → isolate the callback group / go PREEMPT_RT |
| Dropped-message rate | Messages published vs received | Nonzero on a reliable topic → QoS mismatch or overrun |
| DDS discovery time | Time for the graph to fully connect | Large graphs / discovery storms → tune the discovery config `[verify-at-use]` |

## Anti-patterns

- Leaving QoS at defaults on a safety-critical or high-rate topic.
- Putting the safety monitor and the planner on the same single-threaded executor.
- Reaching for a custom middleware before the DDS/QoS budget is proven insufficient.

## See also

- [`../sim-to-real-and-safety/SKILL.md`](../sim-to-real-and-safety/SKILL.md) — the safety architecture the real-time split serves.
- Template: [`../../templates/ros2-node-graph-plan.md`](../../templates/ros2-node-graph-plan.md).
- Best practices: [`../../best-practices/real-time-is-an-architecture-decision-not-a-flag.md`](../../best-practices/real-time-is-an-architecture-decision-not-a-flag.md), [`../../best-practices/design-the-coordinate-frames-before-the-code.md`](../../best-practices/design-the-coordinate-frames-before-the-code.md).
