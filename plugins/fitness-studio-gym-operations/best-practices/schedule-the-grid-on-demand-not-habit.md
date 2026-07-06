# Schedule the grid on demand, not habit

**Status:** Pattern
**Domain:** Class scheduling / instructor ops
**Applies to:** `fitness-studio-gym-operations`

> Advisory operations rule. Fill targets and instructor-pay norms are `[verify-at-use]`. No member PII.

---

## Why this exists

Every class hour carries a fixed instructor pay and a fixed room cost, so a half-empty class burns the same money as a full one but earns less. Most grids accumulate slots by inertia — "it's always been Tuesday 6pm" — rather than by demand. A slot that persistently sits below its **break-even headcount** is a subsidy you're paying out of the full classes. Fill, measured against break-even and read by day-part and class type, is the whole game.

## How to apply

- Compute the **break-even headcount** for every slot: (instructor pay + allocated room cost) / contribution per attendee.
- Read fill by **slot and class type**; cut or merge slots persistently below break-even, re-time toward where waitlists form, add capacity only where a waitlist proves demand.
- Measure **attended, not booked** — a "full" class with three no-shows isn't full; use a no-show/late-cancel window + auto-promote waitlist to reclaim held seats.
- Match the **instructor pay model** (flat / per-head / base+per-head) to the slot's fill economics.

**Do:** defend a slot with its fill against break-even.
**Don't:** keep a slot because it's always been there, or report booked instead of attended.

## Edge cases / when the rule does NOT apply

A strategically-seeded new time (building a habit for a new day-part) may run under break-even for a defined ramp — hold it against a plan and a deadline, not indefinitely. A marquee draw-instructor slot may justify a subsidy for its acquisition halo.

## See also

- [`./ancillary-revenue-is-the-margin.md`](./ancillary-revenue-is-the-margin.md)
- [`../skills/class-schedule-and-instructor-utilization/SKILL.md`](../skills/class-schedule-and-instructor-utilization/SKILL.md)

## Provenance

Codifies `class-schedule-coach-ops` house opinions (#1, #3) and the class-grid + instructor-pay decision trees. Benchmarks: [`../knowledge/fitness-studio-reference-2026.md`](../knowledge/fitness-studio-reference-2026.md).

---

_Last reviewed: 2026-07-02 by `claude`_
