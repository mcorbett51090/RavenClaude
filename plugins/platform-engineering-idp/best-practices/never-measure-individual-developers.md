# Never measure individual developers

**Status:** Absolute rule
**Domain:** DevEx measurement
**Applies to:** `platform-engineering-idp`

---

## Why this exists

The moment a DevEx metric is attributed to an individual, two things happen: trust collapses (people
feel surveilled) and the signal corrupts (people game the proxy). Productivity is a team-and-system
property; individual "productivity" leaderboards (commits per dev, PRs per dev, lines per dev) measure
nothing real and poison the very experience you're trying to improve.

## How to apply

- Aggregate every DevEx metric to the team/system level; never to a person.
- Use surveys and system telemetry to describe the *system's* friction, not a person's worth.
- Refuse requests to rank or evaluate individuals from platform/DevEx data — escalate the framing.

**Do:**

- Report at team/org/platform-cohort granularity.
- Make survey responses anonymous or aggregated.
- State the no-individual-surveillance rule explicitly in any measurement design.

**Don't:**

- Build per-developer dashboards of commits/PRs/LOC.
- Feed DevEx metrics into individual performance reviews.
- Let "we just want visibility" become individual tracking.

## Edge cases / when the rule does NOT apply

A developer looking at *their own* private inner-loop metrics (their build times) is fine — the rule is
against *others* measuring individuals for evaluation/comparison.

## See also

- [`./measure-outcomes-not-output.md`](./measure-outcomes-not-output.md)
- [`../skills/devex-measurement/SKILL.md`](../skills/devex-measurement/SKILL.md)

## Provenance

Codifies the SPACE framework's explicit warning against single/individual productivity metrics and the
DevEx research consensus that measurement must be system-level.

---

_Last reviewed: 2026-06-08 by `claude`._
