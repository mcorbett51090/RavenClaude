# Self-service means no ticket for the common case

**Status:** Absolute rule
**Domain:** Self-service infrastructure
**Applies to:** `platform-engineering-idp`

---

## Why this exists

The unit of value a platform delivers is the *wait it removes*. If provisioning the common thing (a
database, a queue, a new environment) still requires filing a ticket and waiting for a human, you've
built a service desk with a nicer form — not a platform. "Self-service" that opens a ticket is the
most common way a platform initiative quietly fails to deliver its core promise.

## How to apply

- For frequent requests, make the common case a button/CLI that provisions without a human in the
  loop.
- Decide the boundary by `frequency × reversibility × blast radius` (traverse the self-service tree).
- Where blast radius is large, add guardrails (policy/quotas/defaults) — not a human gate on the happy
  path.

**Do:**

- Automate the request → provision → expose flow for the common case.
- Reserve tickets/human review for the rare, irreversible, or exceptional case (the escape hatch).
- Instrument self-service usage as an adoption signal.

**Don't:**

- Ship a "self-service" form that opens a Jira ticket for the common case.
- Put a human approver on the happy path because the action *could* be misused — guardrail it instead.
- Automate genuinely rare/one-off provisioning before it's worth it.

## Edge cases / when the rule does NOT apply

Truly rare, high-stakes, irreversible provisioning (e.g. a new production cloud account) may
legitimately stay ticket-driven; that's the long tail, not the common case.

## See also

- [`./guardrails-not-gates-on-the-happy-path.md`](./guardrails-not-gates-on-the-happy-path.md)
- [`../knowledge/platform-engineering-decision-trees.md`](../knowledge/platform-engineering-decision-trees.md)

## Provenance

Codifies the platform-engineering definition of self-service (CNCF platforms whitepaper; Humanitec /
PlatformEngineering.org) that the platform exists to remove golden-path wait states.

---

_Last reviewed: 2026-06-08 by `claude`._
