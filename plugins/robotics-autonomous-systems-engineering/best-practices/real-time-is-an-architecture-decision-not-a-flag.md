# Real-time is an architecture decision, not a flag

**Status:** Absolute rule
**Domain:** Architecture / real-time
**Applies to:** `robotics-autonomous-systems-engineering`

> Engineering rule. Kernel/timing specifics are `[verify-at-use]` against the target platform. No PII.

---

## Why this exists

Determinism cannot be added at the end. A control loop or safety monitor that shares a single-threaded executor with a heavy planner will jitter and miss deadlines no matter what kernel you install — and you cannot fix that by "turning on real-time." What must be deterministic has to be **decided at design time and isolated**: its own callback group/executor, real-time-safe code (no unbounded allocation, no blocking), the right priorities, and — only then — a `PREEMPT_RT` kernel or a push to a dedicated MCU. Getting this boundary wrong is one of the most expensive architectural mistakes on a robot.

## How to apply

- Enumerate what is truly hard real-time (control loop, safety monitor) vs best-effort (perception, planning, logging).
- Isolate the real-time work: dedicated executor/callback group, real-time-safe code, explicit priorities.
- Escalate the timing requirement into the architecture record with a jitter budget.
- If the stock kernel can't hold the budget, go `PREEMPT_RT` (`[verify-at-use]`); if it must be closest to the actuator, push it to an MCU (`micro-ROS` / firmware → embedded-iot-engineering).
- Traverse the **real-time execution path** decision tree before committing.

**Do:** decide and isolate real-time up front; measure jitter.
**Don't:** put the safety monitor on the planner's executor; expect a kernel flag to retrofit determinism.

## Edge cases / when the rule does NOT apply

A soft-real-time / best-effort robot (research, non-safety, slow) may legitimately run everything on a standard executor — but say so deliberately; don't back into it.

## See also

- [`../skills/ros2-architecture-and-dds/SKILL.md`](../skills/ros2-architecture-and-dds/SKILL.md), [`../skills/sim-to-real-and-safety/SKILL.md`](../skills/sim-to-real-and-safety/SKILL.md)
- Decision tree: [`../knowledge/robotics-decision-trees.md`](../knowledge/robotics-decision-trees.md)

## Provenance

Codifies the `robotics-architect-lead` house opinion and the real-time execution-path decision tree. Kernel/timing specifics: [`../knowledge/robotics-reference-2026.md`](../knowledge/robotics-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
