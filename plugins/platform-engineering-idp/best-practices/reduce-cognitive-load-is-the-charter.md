# Reducing cognitive load is the charter — justify every feature by the load it removes

**Status:** Pattern
**Domain:** Platform strategy
**Applies to:** `platform-engineering-idp`

---

## Why this exists

Platform teams drift into building interesting infrastructure for its own sake. Team Topologies gives
the discipline that prevents this: a platform team exists to reduce the cognitive load of stream-
aligned teams. A feature that doesn't measurably take load off a delivery team is gold-plating, no
matter how elegant.

## How to apply

- For every proposed platform feature, name the specific cognitive load it removes from which teams.
- Prefer the feature that removes the highest `frequency × pain × #teams` load.
- Kill or deprioritize features that don't trace to a real, recurring developer burden.

**Do:**

- Write the "load removed" line in every paved-road RFC and roadmap item.
- Talk to stream-aligned teams to find the real load, not the assumed one.
- Retire platform features nobody adopts (they weren't removing real load).

**Don't:**

- Build capability because it's technically interesting.
- Justify features by platform-team output instead of consumer relief.
- Add abstraction that increases the load it claimed to reduce.

## Edge cases / when the rule does NOT apply

Foundational invisible work (security baseline, compliance) reduces load indirectly by removing
decisions teams shouldn't have to make — that still traces to load, just collectively.

## See also

- [`./measure-outcomes-not-output.md`](./measure-outcomes-not-output.md)
- [`./start-with-the-thinnest-viable-platform.md`](./start-with-the-thinnest-viable-platform.md)

## Provenance

Codifies Team Topologies (Skelton & Pais): platform teams reduce cognitive load for stream-aligned
teams; thinnest viable platform.

---

_Last reviewed: 2026-06-08 by `claude`._
