---
name: motion-planning-and-control
description: "Build the motion stack: Nav2 for mobile-base navigation vs MoveIt for manipulator planning, kinematics and the TF tree (REP 105), trajectory generation inside velocity/acceleration/jerk limits, ROS 2 actions for long-running motion, and control loops (PID vs MPC). Trust the frames before the planner. Safety-bearing limits are verify-at-use."
---

# Motion Planning & Control

A robot moves correctly only when the frames are right, the plan respects the limits, and the controller is stable. This skill sequences those three.

> **Engineering, not certification.** Any velocity/acceleration/force limit that bears on safety is bounded by the safety architecture — `[verify-at-use]` against the machine's safety requirements. Distro-specific planner/controller config names change by version.

## The workflow

1. **Verify the TF tree first.** Parenting, timestamps, and the `map` → `odom` → `base_link` chain (REP 105) must be correct before you debug a planner — a bad transform makes every plan wrong. See [`../../best-practices/design-the-coordinate-frames-before-the-code.md`](../../best-practices/design-the-coordinate-frames-before-the-code.md).
2. **Choose the planner to the task.** Traverse the **motion-planner choice** tree in [`../../knowledge/robotics-decision-trees.md`](../../knowledge/robotics-decision-trees.md): Nav2 (global planner + local controller + a behavior tree) for a mobile base; MoveIt (OMPL sampling, CHOMP/pilz optimization, collision checking) for a manipulator; name the boundary when the robot is both.
3. **Generate trajectories inside the limits.** Velocity, acceleration, and jerk limits are inputs — time-parameterize the path so motion is smooth and bounded, not clipped at execution.
4. **Wrap long motion in an action.** Goto / pick / place is a ROS 2 action: goal, feedback, result, and a correct preempt/cancel. Don't fire-and-forget on a topic.
5. **Design the control loop, then tune.** PID for simple SISO loops; MPC when a model and hard constraints earn the cost. Verify stability (gain/phase margin or the constrained equivalent) before chasing responsiveness. Hand the loop rate and its jitter budget to the architect.

## Metrics

| Metric | Reads | Note |
|---|---|---|
| Planning success rate | Plans found / requests | Low → collision geometry, planner params, or an unreachable goal |
| Trajectory tracking error | Commanded vs actual pose | High → controller tuning, limit violations, or latency |
| Path smoothness (jerk) | Rate-of-change of acceleration | Jerky → trajectory time-parameterization, not the planner |
| Control-loop margin | Stability margin | Thin margin → retune before increasing gain |

## Anti-patterns

- Debugging the planner before checking TF and message timestamps.
- Ignoring velocity/acceleration limits and clipping at the driver.
- Increasing controller gain to fix overshoot instead of retuning for stability.
- A custom planner where a well-configured Nav2/MoveIt would do.

## See also

- The state estimate/map this consumes: [`../perception-and-state-estimation/SKILL.md`](../perception-and-state-estimation/SKILL.md).
- The real-time budget a control loop needs: [`../ros2-architecture-and-dds/SKILL.md`](../ros2-architecture-and-dds/SKILL.md).
- Best practice: [`../../best-practices/simulate-before-you-actuate.md`](../../best-practices/simulate-before-you-actuate.md).
