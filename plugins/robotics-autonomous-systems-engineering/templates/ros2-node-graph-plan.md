# ROS 2 Node-Graph Plan — <subsystem / robot>

> Output template for the ROS 2 computation graph: nodes, the edges between them, QoS, TF frames, and executor/callback-group assignment. One per subsystem or robot. **Engineering, not certification.** Distro/DDS defaults are `[verify-at-use]`. No PII.

## Context
- **Subsystem / robot:** _____  · **Prepared:** 2026-__-__
- **ROS 2 distro (verify-at-use):** _____  · **RMW/DDS:** _____ `[verify-at-use]`

## 1. Nodes
| Node | Responsibility | Process (composed with…) | Real-time? |
|---|---|---|---|
| | | | ☐ hard ☐ best-effort |
| | | | ☐ hard ☐ best-effort |

## 2. Edges (topics / services / actions)
| Edge | Type (topic/service/action) | Publisher -> Subscriber | QoS (reliability/durability/history/deadline) |
|---|---|---|---|
| | topic | | |
| | action | | |
| | service | | |
- **Rule of thumb:** stream → topic; quick query → service; long-running + cancellable → action.
- **QoS is part of the interface** — set it per edge on the data's needs; a mismatch = no connection / silent loss.

## 3. TF frames the graph relies on
| Frame | Parent | Publisher | Notes |
|---|---|---|---|
| | | | |
- Conventions: REP 103 / REP 105 `[verify-at-use]`. Fix the frames before the code.

## 4. Executors & callback groups (the real-time split)
| Executor / callback group | Nodes/callbacks | Isolation reason |
|---|---|---|
| Real-time (control / safety monitor) | | isolate from best-effort |
| Best-effort (perception / planning / logging) | | |
- **Safety monitor and planner are NOT on the same executor.**

## 5. Verify-at-use flags
- _List every distro/DDS default and QoS assumption relied on — confirm against the distro/RMW docs._

## Headline + next steps
- **Headline:** _the defining graph decision (a boundary, a QoS, an isolation) and why_
- **Next action:** _owner — the sim test that proves the graph connects and holds its budget — by when_

---
_Plus the ravenclaude-core Structured Output block._
