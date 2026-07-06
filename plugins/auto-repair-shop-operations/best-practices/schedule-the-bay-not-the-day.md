# Schedule the bay, not the day

**Status:** Pattern
**Domain:** Scheduling / capacity
**Applies to:** `auto-repair-shop-operations`

> Advisory operations rule. Productivity/efficiency benchmarks are `[verify-at-use]`. No customer PII.

---

## Why this exists

An open calendar is not capacity. The shop's real capacity is **bays × productive hours × efficiency** — and booking work against a hopeful empty slot instead of against real bay-hours is how a shop ends up simultaneously "slammed" and unprofitable. Overbooking floods the bays with more work than the productive hours can clear, aging WIP and creating parts-holds; underbooking idles techs and craters productivity. Scheduling to actual bay-hour capacity — and matching the *type* of work booked to the skill available that day — is what keeps a full shop also a flowing one. A shop turning cars away may be losing productive hours, not out of bays.

## How to apply

- Book against **bay-hours** (bays × productive hours × efficiency), not an open calendar.
- Match the day's booked work to the skill mix on the floor (don't book three diagnostics into a one-A-tech day).
- Confirm parts availability before committing a job to a slot (staging prevents the parts-hold that blocks a bay).
- Read whether a "we're full" day is real capacity or lost productive hours before adding a bay or a tech.

**Do:** schedule to measured capacity; match work type to skill; confirm parts first.
**Don't:** treat an empty calendar as free capacity; add a bay to fix a productivity gap; book beyond productive hours.

## Edge cases / when the rule does NOT apply

Emergency / safety work (a vehicle unsafe to drive) is triaged in regardless of the schedule — the rule governs *planned* booking, not urgent triage.

## See also

- [`../skills/technician-productivity-and-efficiency/SKILL.md`](../skills/technician-productivity-and-efficiency/SKILL.md), [`../skills/ro-lifecycle-and-comeback-control/SKILL.md`](../skills/ro-lifecycle-and-comeback-control/SKILL.md)
- Template: [`../templates/shop-kpi-dashboard.md`](../templates/shop-kpi-dashboard.md)

## Provenance

Codifies `auto-repair-shop-lead` and `technician-workflow-manager` house opinions and the productivity dials. Benchmarks: [`../knowledge/auto-repair-shop-reference-2026.md`](../knowledge/auto-repair-shop-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
