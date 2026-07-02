---
name: sim-to-real-and-safety
description: "Cross the sim-to-real gap and build the safety architecture: simulate every behavior before actuating, measure and close the reality gap (dynamics, sensor noise, latency, domain randomization), and make safety a system property — monitored safe state, bounded actuation, degraded modes, and a risk assessment. Functional-safety standard pointers (ISO 10218 / ISO 13849 / ISO 12100) are verify-at-use."
---

# Sim-to-Real & Safety

A robot earns its way onto hardware through simulation, and it stays safe because of its architecture — not because of one e-stop.

> **Engineering, not certification.** This skill helps you *design toward* a functional-safety standard; it does not certify a machine. Every standard clause (ISO 10218 for industrial/collaborative robots, ISO 13849 for safety-related control parts, ISO 12100 for risk assessment, and related) is `[verify-at-use]` against the current standard for the machine class, and the binding determination belongs to a qualified functional-safety engineer.

## The workflow

1. **Simulate before you actuate.** Every new behavior runs in sim (Gazebo, Isaac Sim, or equivalent) first — nominal and failure cases — before it touches real actuators ([`../../best-practices/simulate-before-you-actuate.md`](../../best-practices/simulate-before-you-actuate.md)).
2. **Name the reality gap.** The sim-to-real gap has sources: unmodeled dynamics (friction, backlash, compliance), sensor noise the sim doesn't reproduce, and latency the sim doesn't have. Enumerate them; don't discover them on the robot.
3. **Close the gap deliberately.** Improve the model where it matters, add realistic sensor noise, and use domain randomization for learned components so the policy doesn't overfit sim. Measure the residual gap on a small, bounded on-robot test.
4. **Design the safety architecture as layers.** A monitored safe state (independent of the main compute), bounded actuation limits enforced below the planner, degraded-mode behavior when a sensor/estimate fails, and the e-stop — the e-stop is the last layer, not the plan ([`../../best-practices/safety-is-a-system-property-not-an-estop.md`](../../best-practices/safety-is-a-system-property-not-an-estop.md)).
5. **Do the risk assessment.** Identify hazards (ISO 12100 style), estimate risk, and reduce it by design first, then by safeguards, then by information — `[verify-at-use]` the specific standard and its required performance/integrity level for the machine.
6. **Cross the real-time path with the tree.** The safety monitor is a real-time citizen — traverse the **real-time execution path** tree in [`../../knowledge/robotics-decision-trees.md`](../../knowledge/robotics-decision-trees.md).

## Metrics

| Metric | Reads | Note |
|---|---|---|
| Sim-to-real gap | Behavior delta sim vs first on-robot run | Large → model/noise/latency fidelity before you scale the test |
| Safe-stop latency | Time from trigger to bounded safe state | Must meet the standard's requirement `[verify-at-use]` |
| Degraded-mode coverage | Fraction of failure modes with a defined behavior | Gaps → undefined behavior on failure |
| Hazards with a mitigation | Risk-assessment closure | Open hazards → not ready to deploy |

## Anti-patterns

- Actuating a behavior that was never simulated.
- Treating the e-stop as the safety architecture.
- Quoting a functional-safety performance level from memory instead of the standard `[verify-at-use]`.
- Domain-randomizing nothing, then being surprised the learned policy fails on the real robot.

## See also

- The real-time split that isolates the safety monitor: [`../ros2-architecture-and-dds/SKILL.md`](../ros2-architecture-and-dds/SKILL.md).
- Template: [`../../templates/robot-system-architecture.md`](../../templates/robot-system-architecture.md).
- Reference (standard pointers, dated): [`../../knowledge/robotics-reference-2026.md`](../../knowledge/robotics-reference-2026.md).
