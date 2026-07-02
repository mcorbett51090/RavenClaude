# Staff-to-ratio is the cost model

**Status:** Absolute rule
**Domain:** Operations / finance
**Applies to:** `childcare-early-education`

> Advisory operations rule. Ratios are **state-specific** — `[verify-at-use, state-specific]`. Not financial advice. No child/family PII.

---

## Why this exists

Labor is the dominant cost in a childcare center, and it does **not scale smoothly with enrollment** — it steps up a **whole teacher** each time a room crosses a ratio boundary. Add the one child that pushes a room past its ratio, and you have added a full teacher's payroll, not a fraction of one. This is why a center can have empty seats and still lose money, and why a partly-filled room is often the least profitable state: the teacher is fixed the moment the room opens, while tuition revenue scales with each enrolled child. If you model labor as an average cost per child, you will misprice tuition and misjudge every add-a-room decision.

## How to apply

- Model each room's labor as a **step function**: teachers required = ceiling(enrolled ÷ ratio), and cost jumps a whole teacher at each boundary `[verify-at-use, state-specific]`.
- Compute **ratio-driven labor cost per room** and compare it to that room's tuition revenue at current enrollment — not a center-wide average.
- Identify rooms **just over a boundary** (one extra child forcing a second teacher) — fill them toward full or don't cross the boundary.
- Include **open/close/break coverage** in the labor model; it is real cost, not overhead.

**Do:** price tuition and evaluate growth against the whole-teacher step.
**Don't:** average labor across children; assume the next enrolled child is pure margin.

## Edge cases / when the rule does NOT apply

Floats shared across rooms and multi-age licensing can soften the step in specific configurations — but they change the shape of the step, not the fact that it is a step. Model the actual staffing the rule requires.

## See also

- [`../skills/staffing-to-ratio-scheduling/SKILL.md`](../skills/staffing-to-ratio-scheduling/SKILL.md), [`../templates/ratio-staffing-plan.md`](../templates/ratio-staffing-plan.md)
- Rule: [`ratios-are-a-floor-not-a-target.md`](./ratios-are-a-floor-not-a-target.md)

## Provenance

Codifies `childcare-center-lead` house opinion ("payroll steps, it doesn't slide") and the staff-a-room-to-ratio tree. Norms: [`../knowledge/childcare-reference-2026.md`](../knowledge/childcare-reference-2026.md) (verify-at-use, state-specific).

---

_Last reviewed: 2026-07-02 by `claude`_
