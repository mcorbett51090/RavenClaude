# Measure outcomes, not output

**Status:** Absolute rule
**Domain:** DevEx measurement
**Applies to:** `platform-engineering-idp`

---

## Why this exists

"Platform features shipped" feels like progress and measures nothing that matters. A platform team's
real product is *someone else's velocity and experience*. If the metric is output (features, commits,
LOC), the team optimizes for looking busy; if it's outcomes (adoption, time-to-prod, reported
friction), the team optimizes for actually helping. The KPI choice shapes the behavior.

## How to apply

- Make the platform's headline metrics outcome metrics: adoption (funnel), time-to-prod / time-to-
  first-PR, change-fail rate, and reported developer friction.
- Ship a **balanced** set so no single proxy gets gamed (a delivery metric + a perception metric + an
  adoption metric).
- Attach a decision to every metric; retire dashboards nobody acts on.

**Do:**

- Report platform success as developer outcomes.
- Pair every system metric with a perception signal.
- Treat low adoption as the truest outcome signal.

**Don't:**

- Use features-shipped, commits, or LOC as a platform KPI.
- Track deploy frequency alone (invites tiny pointless deploys).
- Collect a metric with no decision attached.

## Edge cases / when the rule does NOT apply

Output counts can be useful *operational* health checks (e.g. template runs as an adoption proxy) —
but as adoption signals, not as the success KPI.

## See also

- [`./never-measure-individual-developers.md`](./never-measure-individual-developers.md)
- [`./reduce-cognitive-load-is-the-charter.md`](./reduce-cognitive-load-is-the-charter.md)

## Provenance

Codifies DORA + SPACE + DevEx (DXI) guidance that balanced, outcome-oriented, system-level metrics
beat single output proxies.

---

_Last reviewed: 2026-06-08 by `claude`._
