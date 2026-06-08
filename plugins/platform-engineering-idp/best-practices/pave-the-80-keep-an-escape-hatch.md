# Pave the 80% path — and keep an escape hatch for the 20%

**Status:** Absolute rule
**Domain:** Golden-path design
**Applies to:** `platform-engineering-idp`

---

## Why this exists

A golden path that covers every case becomes either impossibly complex or a cage. A cage drives the
genuine 20% to build shadow platforms you can't see, support, or secure. The right shape is a road
that makes the common case effortless and lets the uncommon case step off — allowed and unsupported —
without leaving the building.

## How to apply

- Identify the ~80% common service/workload shape and pave exactly that.
- Bake defaults in (CI, observability, security baseline, ownership) so the common case is free.
- Document the escape hatch: how to step off, and that off-road means no platform SLA.

**Do:**

- Scope the path to the common shape; resist paving the long tail.
- State explicitly that deviation is allowed (and unsupported).
- Watch for recurring escapes and pave them as new supported variants.

**Don't:**

- Forbid deviation (the cage anti-pattern).
- Try to make one path serve every team.
- Treat an escape as a violation instead of a signal.

## Edge cases / when the rule does NOT apply

Hard safety/compliance constraints (e.g. "secrets never in plaintext") have no escape hatch — those
are guardrails, not paved-road conveniences.

## See also

- [`./the-supported-way-must-be-the-easiest-way.md`](./the-supported-way-must-be-the-easiest-way.md)
- [`./a-recurring-escape-is-a-signal-to-pave-a-variant.md`](./a-recurring-escape-is-a-signal-to-pave-a-variant.md)

## Provenance

Codifies the "paved road" pattern (Netflix, Spotify golden paths) and the Team Topologies guidance on
thinnest-viable-platform with optional, not mandatory, consumption.

---

_Last reviewed: 2026-06-08 by `claude`._
