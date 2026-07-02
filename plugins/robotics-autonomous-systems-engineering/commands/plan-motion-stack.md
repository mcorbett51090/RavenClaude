---
description: "Plan a robot's motion stack — Nav2 vs MoveIt vs custom, the TF tree, trajectory generation inside limits, ROS 2 action interfaces, and the control loop (PID vs MPC) — trusting the frames before the planner."
argument-hint: "[platform kinematics + motion task + actuators + TF tree + symptom]"
---

You are running `/robotics-autonomous-systems-engineering:plan-motion-stack`. Use `ros-motion-planning-engineer` + the `motion-planning-and-control` skill.

> Engineering, not certification. Any safety-bearing velocity/acceleration/force limit is bounded by the safety architecture and `[verify-at-use]`. No PII.

## Steps
1. Capture the platform (kinematics, actuators, the motion task, the TF tree) and any symptom.
2. **Verify the TF tree first** — parenting, timestamps, REP 105 `map`/`odom`/`base_link` — before touching a planner.
3. Traverse the **motion-planner choice (Nav2 vs MoveIt vs custom)** tree in `knowledge/robotics-decision-trees.md`.
4. Decide: the planner(s) and the coordination boundary for a mobile manipulator, the trajectory generation inside velocity/acceleration/jerk limits, the ROS 2 action interfaces for long-running motion, and the control loop (PID vs MPC) with its rate and stability check.
5. Hand the loop's real-time/compute budget to `robotics-architect-lead` and the pose/map it consumes to `perception-and-autonomy-engineer`.
6. Emit with the `motion-planning-and-control` workflow + the Structured Output block; name the sim test that proves the motion before actuation.
