# A PRD Names the Constraint, Not Just the Problem

**Status:** Pattern
**Domain:** Product discovery / PRD writing
**Applies to:** `product-management`

---

## Why this exists

A PRD that states a problem and then leaves "how to solve it" entirely open is useful in principle but frustrating in practice when there are real constraints the engineering team cannot infer. Conversely, a PRD that details the solution fully removes the engineering team's ability to find a better one. The right balance is explicit: state the problem, state the desired outcome, and state the known constraints — technical, business, regulatory, time-horizon — so the engineering team can innovate within the right envelope. An unstated constraint discovered mid-sprint is a scope-change; a constraint documented in the PRD is a design parameter.

## How to apply

Include an explicit constraints section in every PRD or initiative brief.

```
PRD — Constraints Section (after problem and outcome, before solution hypothesis)
──────────────────────────────────────────────────────
MUST-NOT-VIOLATE (hard constraints — non-negotiable)
  Technical: e.g., "Must use the existing auth system; cannot require a new OAuth provider"
  Regulatory: e.g., "Must support right-to-erasure within 30 days (GDPR Art. 17)"
  Business: e.g., "Cannot require a Stripe account — must support manual invoicing"
  Time: e.g., "Must be shippable before the Oct 15 conference — hard deadline"

SHOULD-RESPECT (soft constraints — override requires a documented decision)
  e.g., "Prefer to use the existing notification infrastructure over a new one"
  e.g., "Prefer mobile-first — > 60% of target users are on iOS"

OUT-OF-SCOPE (explicit — document what the PRD does NOT cover to prevent scope creep)
  e.g., "This PRD does not cover the admin dashboard view"
  e.g., "Internationalization / localization is out of scope for v1"

OPEN QUESTIONS (engineering / design needs an answer to before starting)
  e.g., "Does the constraint on the notification system apply to in-app only or also email?"
  Owner + resolution date for each open question.
```

**Do:**
- Write constraints from the problem side, not the solution side — "must not require login" is a constraint; "use cookie-based auth" is a solution choice.
- Have the engineering lead review the constraints before the PRD is finalized — they often know technical constraints the PM doesn't.
- Review the constraints list at sprint planning; a constraint discovered after kickoff is a process failure.

**Don't:**
- Leave a hard constraint implicit because "everyone knows it" — the next engineer who picks up the PRD in 6 months doesn't know it.
- List so many soft constraints that the engineering team can't exercise judgment; the soft list should be a short guardrail, not a prescriptive design guide.
- Mark a business or strategic decision as a "constraint" to prevent it from being challenged — if it is a decision, call it a decision.

## Edge cases / when the rule does NOT apply

- **Exploratory spikes** (purely technical investigation, no user-facing output) — the PRD analogue is a spike brief; hard constraints are still relevant but the outcome section is a question to answer, not a metric to move.
- **One-off operational projects** (e.g., a one-time data migration) — the constraint section is especially important for operational projects, because technical and regulatory constraints often dominate.

## See also

- [`../agents/product-discovery-lead.md`](../agents/product-discovery-lead.md) — owns PRD writing and the problem/outcome framing.
- [`./write-the-success-metric-before-writing-the-spec.md`](./write-the-success-metric-before-writing-the-spec.md) — the success metric is the first section of the PRD; the constraints section comes after the problem and outcome sections.

## Provenance

Codifies the product-discovery-lead's PRD constraint discipline from the product-management plugin's CLAUDE.md §2 #1 (specs frame the problem and the desired outcome; the solution is a hypothesis) and §2 #2 (test assumptions before building). The constraints-section structure reflects standard product specification practice at Intercom, Basecamp, and other outcome-oriented PM cultures.

---

_Last reviewed: 2026-06-05 by `claude`_
