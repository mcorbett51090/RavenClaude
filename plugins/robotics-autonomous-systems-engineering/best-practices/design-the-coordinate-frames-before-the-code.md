# Design the coordinate frames before the code

**Status:** Absolute rule
**Domain:** Architecture / motion
**Applies to:** `robotics-autonomous-systems-engineering`

> Engineering rule. Frame conventions (REP 103/105) are durable; confirm the exact semantics against the REP — `[verify-at-use]`. No PII.

---

## Why this exists

The TF tree is the contract every node plugs into. A sensor reading in the wrong frame, a transform with a stale timestamp, or an ambiguous `map` vs `odom` semantic makes every downstream result wrong — and the bug surfaces far from its cause, disguised as a "planner bug" or a "drifting estimate." Deciding the frames and conventions **first**, and writing them down, prevents a whole class of expensive, late, hard-to-localize failures.

## How to apply

- Adopt the standard conventions: REP 103 (SI units, right-handed axes) and REP 105 (`map` → `odom` → `base_link` semantics) — `[verify-at-use]` against the REP.
- Draw the TF tree explicitly: every frame, its parent, and who publishes the transform (static vs dynamic).
- Make timestamps first-class: every measurement is stamped and transformed at the right time, not the latest.
- When debugging, verify the TF tree and message timestamps **before** touching a planner or filter.

**Do:** write the frame tree into the architecture record; check TF first when a result looks wrong.
**Don't:** invent per-node frame conventions; debug the planner before the frames.

## Edge cases / when the rule does NOT apply

A trivial single-frame system (one fixed sensor, no motion) needs less ceremony — but the moment there are two moving frames, the tree is the contract.

## See also

- [`../skills/motion-planning-and-control/SKILL.md`](../skills/motion-planning-and-control/SKILL.md), [`../skills/perception-and-state-estimation/SKILL.md`](../skills/perception-and-state-estimation/SKILL.md)
- Template: [`../templates/ros2-node-graph-plan.md`](../templates/ros2-node-graph-plan.md)

## Provenance

Codifies the `robotics-architect-lead` and `ros-motion-planning-engineer` house opinion. Frame conventions: [`../knowledge/robotics-reference-2026.md`](../knowledge/robotics-reference-2026.md) (REP references, verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
