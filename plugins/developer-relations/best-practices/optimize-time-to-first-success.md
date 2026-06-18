# Optimize time-to-first-success before anything else

**Status:** Strong default
**Domain:** Developer experience / onboarding
**Applies to:** `developer-relations`

---

## Why this exists

The path from "landed / signed up" to "saw the thing work" is the highest-leverage surface in DevRel.
Every step on it is a place to lose a developer, and most programs over-invest in top-of-funnel
awareness while this stage quietly leaks. Cutting time-to-first-success (TTFS) usually moves activation
more than any amount of new reach.

## How to apply

**Count, then cut:**
- **Steps to first success** — the count *is* the metric. Walk the golden path as a hostile
  first-timer on a clean machine and count every discrete action.
- **The first dead end** — find where a reasonable developer gets stuck with no next move. Fix this
  before anything downstream; nothing past it matters.
- **Friction per step** — unstated prerequisite, a key with no source, a snippet that doesn't run, an
  error with no recovery.

**Do:**
- Get the API key into running code as fast as possible — auth/setup is the top churn point.
- Provide one linear golden path; branch only *after* first success.
- End in a visible win (a response, a rendered result), not "you have configured the client."

**Don't:**
- Audit from memory of how it's supposed to work — the leaks only show on a clean walk.
- Fix cosmetic issues downstream of the first dead end before fixing the dead end.
- Require reading documentation elsewhere before the developer can act.

## Edge cases / when the rule does NOT apply

- A genuinely complex product may have an irreducibly long path — then **instrument and segment** it
  (where exactly do people stop?) rather than pretending a 2-minute quickstart exists.
- An advanced/enterprise integration legitimately needs setup; provide a *separate* fast path for
  evaluation so the first impression isn't the enterprise onboarding.

## See also

- [`../knowledge/developer-experience-and-onboarding.md`](../knowledge/developer-experience-and-onboarding.md) — the golden path + the TTFS audit
- [`../templates/developer-onboarding-audit.md`](../templates/developer-onboarding-audit.md) — the drop-off-map worksheet

## Provenance

Codifies developer-relations CLAUDE.md §3 house opinion #4 (time-to-first-success is the product).
The golden-path / TTFS framing is established developer-experience practice.

---

_Last reviewed: 2026-06-18 by `claude`_
