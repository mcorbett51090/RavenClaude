# Robotics & Autonomous Systems — Decision Trees

> Reference decision trees for the `robotics-autonomous-systems-engineering` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Engineering decision-support, not functional-safety certification or legal advice.** Anything touching a functional-safety standard clause, a DDS/distro detail, or a sensor/compute spec is `[verify-at-use]` — confirm against the standard, the vendor datasheet, or a measurement on the target before acting. No PII.
>
> _Last reviewed: 2026-07-02 by `claude`. Principles are durable; dated distro/DDS/sensor/standard specifics live in [`robotics-reference-2026.md`](robotics-reference-2026.md)._

---

## Decision Tree: ROS 2 vs ROS 1 vs custom middleware

```mermaid
flowchart TD
    A[New robot software stack] --> B{Greenfield or<br/>maintaining existing?}
    B -- "existing ROS 1 system<br/>at end of life" --> C{Migration budget?}
    C -- yes --> D[Migrate to ROS 2<br/>ROS 1 is EOL — verify-at-use]
    C -- no --> E[Maintain ROS 1 short-term,<br/>plan the ROS 2 migration]
    B -- greenfield --> F{Need the ROS ecosystem<br/>Nav2 / MoveIt / tooling?}
    F -- yes --> G{Hard real-time on an<br/>MCU in the loop?}
    G -- "yes, on the MCU" --> H[ROS 2 on the compute<br/>+ micro-ROS on the MCU]
    G -- no --> I[ROS 2 with DDS/RMW<br/>+ QoS per topic]
    F -- "no, tiny/closed embedded<br/>or extreme constraints" --> J[Custom / minimal middleware<br/>— justify vs ROS 2 cost]
```

**Rule:** default to **ROS 2** for anything that benefits from the ecosystem (Nav2, MoveIt, tooling) — reach for `micro-ROS` at the MCU boundary and a **custom** middleware only when an extreme constraint defeats DDS. ROS 1 is end-of-life; new work targets ROS 2. Distro/DDS specifics are `[verify-at-use]`.

---

## Decision Tree: motion-planner choice (Nav2 vs MoveIt vs custom)

```mermaid
flowchart TD
    A[Robot needs to move] --> B{What moves?}
    B -- "mobile base<br/>through an environment" --> C[Nav2: global planner +<br/>local controller + behavior tree]
    B -- "articulated arm /<br/>manipulator" --> D[MoveIt: OMPL/CHOMP/pilz<br/>+ collision checking]
    B -- "both<br/>(mobile manipulator)" --> E[Nav2 for the base,<br/>MoveIt for the arm,<br/>name the coordination boundary]
    C --> F{Stock planners meet<br/>the requirement?}
    D --> F
    E --> F
    F -- yes --> G[Configure the stock stack<br/>— TF tree first]
    F -- "no: unusual dynamics /<br/>constraints stock can't express" --> H[Custom planner<br/>— justify vs stock cost]
```

**Rule:** pick the planner to **what actually moves** — Nav2 for navigation, MoveIt for manipulation, both with a named coordination boundary for a mobile manipulator. Prefer a **well-configured stock stack** and earn a custom planner with a requirement the stock planners can't express. Verify the TF tree before blaming the planner.

---

## Decision Tree: localization-stack choice

```mermaid
flowchart TD
    A[Robot needs to know where it is] --> B{Is there a known map?}
    B -- "no map<br/>(explore / build it)" --> C{Environment allows<br/>loop closure?}
    C -- yes --> D[SLAM: build the map online<br/>with loop closure]
    C -- "no / degenerate<br/>(long corridor, open field)" --> E[Fuse odometry + IMU + GPS/RTK<br/>— SLAM will drift]
    B -- "yes, known map" --> F{Indoor structured<br/>or outdoor/global?}
    F -- indoor --> G[Map-based localization<br/>particle filter — AMCL-style]
    F -- "outdoor / global" --> H[GPS/RTK + IMU fusion<br/>in an EKF/UKF]
    D --> I[Feed pose + map to the planner]
    E --> I
    G --> I
    H --> I
```

**Rule:** decide on **whether a map exists and whether the environment supports loop closure**. Build a map online (SLAM) only when there's none and the scene allows it; localize against a known map when you have one — cheaper and more stable. Outdoors, lean on GPS/RTK + IMU fusion. Package choices are `[verify-at-use]` against your sensors and distro.

---

## Decision Tree: real-time execution path

```mermaid
flowchart TD
    A[A task with timing needs] --> B{Is it truly<br/>hard real-time?}
    B -- "no: best-effort<br/>(perception, planning, logging)" --> C[Standard executor,<br/>own callback group,<br/>QoS on the data]
    B -- "yes: control loop /<br/>safety monitor" --> D{Where must it run?}
    D -- "on the main compute" --> E{Jitter budget met on<br/>a stock kernel?}
    E -- yes --> F[Dedicated real-time executor +<br/>isolated callback group,<br/>real-time-safe code]
    E -- no --> G[PREEMPT_RT kernel +<br/>isolation + priorities<br/>— verify-at-use]
    D -- "closest to the actuator" --> H[Push to an MCU:<br/>micro-ROS / firmware<br/>-> embedded-iot-engineering]
```

**Rule:** decide the real-time need **at design time** and isolate what must be deterministic — most work is best-effort and lives on a standard executor; a control loop or safety monitor gets an isolated callback group/executor, then `PREEMPT_RT`, then a push to an MCU. Real-time is an architecture decision, not a runtime flag. Kernel/timing specifics are `[verify-at-use]`.

---

## See also

- [`robotics-reference-2026.md`](robotics-reference-2026.md) — dated distro/DDS/sensor/compute/standard specifics (verify-at-use).
- Skills: [`../skills/ros2-architecture-and-dds/SKILL.md`](../skills/ros2-architecture-and-dds/SKILL.md), [`../skills/motion-planning-and-control/SKILL.md`](../skills/motion-planning-and-control/SKILL.md), [`../skills/perception-and-state-estimation/SKILL.md`](../skills/perception-and-state-estimation/SKILL.md), [`../skills/sim-to-real-and-safety/SKILL.md`](../skills/sim-to-real-and-safety/SKILL.md).
