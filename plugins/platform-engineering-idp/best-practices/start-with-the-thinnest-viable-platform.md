# Start with the thinnest viable platform

**Status:** Pattern
**Domain:** Platform strategy
**Applies to:** `platform-engineering-idp`

---

## Why this exists

Most platform initiatives over-build before they've earned the right to. They stand up a Backstage
mega-portal and model the whole org before a single golden path is worth paving — burning 6–18 months
on maintenance before delivering anything a developer wanted. The thinnest viable platform inverts
this: pave the one journey whose friction is real and recurring, win one team, and let demonstrated
value pull the next investment.

## How to apply

- Pick the single highest `frequency × pain × #teams` developer journey and pave just that.
- Defer the portal until you have multiple things worth surfacing.
- Below ~3 teams sharing the same friction, ship a repo template, not a platform team.

**Do:**

- Deliver one paved road one team loves before expanding.
- Let pull (other teams asking for it) drive the roadmap.
- Add portal/catalog when the catalog answers a question someone is actually asking.

**Don't:**

- Build the grand portal first.
- Model the entire software catalog up front.
- Staff a platform team before the recurring, cross-team friction exists.

## Edge cases / when the rule does NOT apply

A large org with obvious, well-understood, cross-cutting friction may justifiably start bigger — but
even then, sequence delivery so the first win lands in weeks, not quarters.

## See also

- [`./buy-or-adopt-before-you-build.md`](./buy-or-adopt-before-you-build.md)
- [`./reduce-cognitive-load-is-the-charter.md`](./reduce-cognitive-load-is-the-charter.md)

## Provenance

Codifies Team Topologies' "thinnest viable platform" and the platform-engineering anti-pattern
literature on premature portal-building.

---

_Last reviewed: 2026-06-08 by `claude`._
