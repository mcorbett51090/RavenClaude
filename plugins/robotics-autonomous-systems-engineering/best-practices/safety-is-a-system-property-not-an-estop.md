# Safety is a system property, not an e-stop

**Status:** Absolute rule
**Domain:** Safety architecture
**Applies to:** `robotics-autonomous-systems-engineering`

> Engineering rule — **not functional-safety certification or legal advice.** Every standard clause (ISO 12100 / ISO 13849 / ISO 10218 and related) is `[verify-at-use]`; the binding safety determination belongs to a qualified functional-safety engineer. A robot that can move can injure. No PII.

---

## Why this exists

An e-stop is one layer of protection, not a safety architecture. Real safety is a **property of the whole system**: a monitored safe state that is independent of the main compute, actuation limits enforced below the planner, degraded-mode behavior when a sensor or estimate fails, and a documented risk assessment that drove the design. Treating "we added an e-stop" as the safety story leaves undefined behavior on every failure mode the e-stop doesn't cover — which is most of them. Safety has to be designed in layers, from the risk assessment down, not bolted on at the end.

## How to apply

- Do the risk assessment first (ISO 12100 style): identify hazards, estimate risk, reduce by design → safeguards → information — `[verify-at-use]` the applicable standard and its required performance/integrity level.
- Build layers: a monitored safe state (independent path), bounded actuation limits below the planner, explicit degraded modes, then the e-stop.
- Make the safety monitor a real-time citizen — isolate it (see the real-time rule); don't share its executor with the planner.
- Define behavior for every failure mode (sensor loss, estimate divergence, comms loss), not just the ones you expect.
- Never quote a functional-safety performance level from memory; confirm against the standard and a qualified engineer.

**Do:** design safety in layers from a risk assessment; isolate the safety monitor.
**Don't:** treat the e-stop as the plan; quote a safety level from training knowledge.

## Edge cases / when the rule does NOT apply

A robot that physically cannot exert harmful force/energy (intrinsically safe by construction) needs proportionate rigor — but confirm that "cannot" with the risk assessment, don't assume it.

## See also

- [`../skills/sim-to-real-and-safety/SKILL.md`](../skills/sim-to-real-and-safety/SKILL.md), [`../skills/ros2-architecture-and-dds/SKILL.md`](../skills/ros2-architecture-and-dds/SKILL.md)
- Template: [`../templates/robot-system-architecture.md`](../templates/robot-system-architecture.md)
- Standard pointers (dated, non-authoritative): [`../knowledge/robotics-reference-2026.md`](../knowledge/robotics-reference-2026.md)

## Provenance

Codifies the `robotics-architect-lead` house opinion and the sim-to-real-and-safety skill. Standard pointers are orientation only and `[verify-at-use]`.

---

_Last reviewed: 2026-07-02 by `claude`_
