# The platform is a product — adoption is earned, not mandated

**Status:** Absolute rule
**Domain:** Platform strategy
**Applies to:** `platform-engineering-idp`

---

## Why this exists

A platform mandated by decree hides whether it's any good. Teams comply on paper and route around it
in practice (shadow platforms), and you lose the single most valuable signal a platform team has:
voluntary adoption. When developers are customers who *could* leave, low adoption is honest product
feedback. When they're captives, you learn nothing until the platform has rotted.

## How to apply

- Treat the platform as a product with developers as paying customers (paying in adoption).
- Earn adoption by being the **easiest** path: dogfood it, land one happy team, let pull spread it.
- If adoption is low, fix the product or the positioning — investigate the friction; don't reach for a
  mandate.

**Do:**

- Run developer user research before building; ship the thinnest viable platform.
- Make voluntary adoption the headline success signal.
- Let an escape hatch exist so "adoption" means "chose this," not "had no choice."

**Don't:**

- Mandate the platform/portal "with no exceptions."
- Interpret low adoption as developer disobedience.
- Measure success by features shipped instead of teams who chose the path.

## Edge cases / when the rule does NOT apply

A genuine security or compliance control (e.g. all prod deploys go through the audited pipeline) *can*
be mandatory — but make that the narrow, justified exception, not the platform's default posture, and
make the mandated path the easy one too.

## See also

- [`./pave-the-80-keep-an-escape-hatch.md`](./pave-the-80-keep-an-escape-hatch.md)
- [`./measure-outcomes-not-output.md`](./measure-outcomes-not-output.md)

## Provenance

Codifies the Team Topologies "platform-as-a-product" thesis and the platform-engineering community
consensus (PlatformEngineering.org, Thoughtworks) that paved roads win by ergonomics, not decree.

---

_Last reviewed: 2026-06-08 by `claude`._
