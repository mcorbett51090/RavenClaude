# Simulate before you actuate

**Status:** Absolute rule
**Domain:** Testing / sim-to-real
**Applies to:** `robotics-autonomous-systems-engineering`

> Engineering rule. Simulator fidelity and the sim-to-real gap are measured, not assumed. No PII.

---

## Why this exists

A robot that actuates an unvalidated behavior can break itself, its environment, or a person. Simulation (Gazebo, Isaac Sim, or equivalent) is where a behavior earns its way onto hardware — nominal and failure cases both — at zero physical risk. The sim-to-real gap (unmodeled dynamics, sensor noise the sim doesn't reproduce, latency the sim doesn't have) is a **first-class, planned-for risk**, not a surprise you discover on the real robot. Skipping sim trades a cheap failure in software for an expensive one in the world.

## How to apply

- Run every new behavior in sim first, including the failure and edge cases, before it touches real actuators.
- Name the reality-gap sources up front: dynamics (friction/backlash/compliance), sensor noise, latency.
- Close the gap deliberately — improve the model where it matters, inject realistic sensor noise, and domain-randomize learned components.
- Measure the residual gap on a small, bounded on-robot test before scaling up.

**Do:** validate in sim; measure the gap on a bounded first run.
**Don't:** actuate a behavior that was never simulated; assume sim fidelity.

## Edge cases / when the rule does NOT apply

Pure teleoperation with a human continuously in the loop and hard actuation limits is a different risk profile — but any autonomous behavior still simulates first.

## See also

- [`../skills/sim-to-real-and-safety/SKILL.md`](../skills/sim-to-real-and-safety/SKILL.md), [`../skills/motion-planning-and-control/SKILL.md`](../skills/motion-planning-and-control/SKILL.md)
- Template: [`../templates/robot-system-architecture.md`](../templates/robot-system-architecture.md)

## Provenance

Codifies the team house opinion and the sim-to-real-and-safety skill. Simulator/landscape specifics: [`../knowledge/robotics-reference-2026.md`](../knowledge/robotics-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
