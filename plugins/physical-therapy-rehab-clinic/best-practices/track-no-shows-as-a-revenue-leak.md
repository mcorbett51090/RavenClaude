# Track no-shows as a revenue leak

**Status:** Pattern
**Domain:** Operations / capacity
**Applies to:** `physical-therapy-rehab-clinic`

> Advisory only. Cancellation/missed-visit fee rules are `[verify-at-use]` per payor.

---

## Why this exists

A no-show is an empty chair that was committed capacity — lost-visit revenue that compounds across a week. Treated as an annoyance it stays invisible; quantified as a leak it gets fixed. It also breaks the plan-of-care cadence, which is a clinical and a recert risk.

## How to apply

1. Measure the **no-show + late-cancel rate by slot**, not blanket.
2. Quantify: lost visits × net rate/visit = the leak.
3. Attack with reminders, an enforced cancellation policy, re-book-at-the-desk, and **data-sized** overbooking.

## Edge cases / when the rule does NOT apply

Some payors prohibit billing a patient for a missed visit; **`[verify-at-use]` before charging a missed-visit fee.**

## See also

- [`../skills/schedule-and-capacity-planning/SKILL.md`](../skills/schedule-and-capacity-planning/SKILL.md)
- [`../knowledge/pt-clinic-decision-trees.md`](../knowledge/pt-clinic-decision-trees.md)

## Provenance

Codifies `clinic-operations-lead` house opinion. Operational pattern; clinic-specific baselines.

---

_Last reviewed: 2026-06-22 by `claude`_
