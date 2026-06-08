# AI deflection must know when to hand off

**Status:** Absolute rule
**Domain:** AI-deflection and bot design
**Applies to:** `customer-support-cx-operations`

---

## Why this exists

An AI agent that cannot escalate to a human when it reaches the edge of its confidence or when
the contact type requires human judgment is not a support tool — it is a support wall. The customer
is trapped in a loop, cannot reach a human, and eventually abandons or contacts via a different
channel with more frustration. This is worse than having no bot at all.

The handoff path is not an optional feature of an AI deflection flow. It is a non-negotiable
structural element. Every AI deflection deployment must define: when does the bot escalate?
What context does it pass to the human? How does the customer initiate the escalation?

## How to apply

**Define the intent taxonomy before deployment:**
- **Fully automatable:** high-volume, scripted, low-stakes (order status, password reset, account
  lookup, FAQ). Bot handles end-to-end. Escalation is available but not expected.
- **Semi-automatable:** requires disambiguation or data not available to the bot (billing dispute,
  subscription modification, service issue with account context). Bot gathers context, hands off
  to human with the context package.
- **Must-escalate:** sensitive, high-blast-radius, or confidence below threshold (legal,
  safety, account termination, a question the bot cannot answer). Bot acknowledges and routes
  immediately — no attempt to resolve.

**Define the handoff trigger criteria:**
- Confidence score below threshold (e.g., <0.7 for a specific intent classification).
- Customer explicitly requests a human agent.
- Customer frustration signals (repeated rephrasing, negative sentiment markers, profanity).
- Contact type is in the must-escalate list.
- N-th contact on the same issue within X days (repeat-contact escalation).

**Define the context handoff format:**
- What the customer asked (transcript or summary).
- What the bot attempted (resolution steps taken, information collected).
- Why the bot escalated (reason code — mirrors the agent escalation taxonomy).
- Customer-provided context (account ID, issue description, steps tried).
The receiving human agent must be able to continue the conversation without asking the customer
to repeat what they already told the bot.

**Do:**

- Write the handoff spec (intent taxonomy + trigger criteria + context format) before the bot is built.
  This is a design input for `claude-app-engineering`, not an afterthought.
- Surface the "talk to a person" option prominently and at every step — not hidden after three
  failed bot attempts.
- Monitor bot handoff rate by intent category. A handoff rate above 30% for a "fully automatable"
  intent is a signal that the intent is mis-classified or the KB quality is insufficient.

**Don't:**

- Deploy a bot that has no escalation path.
- Hide the human escalation behind multiple bot turns that must fail before the option appears.
- Measure bot success by containment rate alone — verify that contained contacts are resolved
  (post-self-service CSAT or follow-on contact rate within 24h).
- Let the bot attempt to resolve must-escalate intents (legal, safety, account termination) —
  even a well-intentioned attempt can create liability.

## Edge cases / when the rule does NOT apply

For a pure FAQ bot with no transactional capability (it can only answer questions, not take
actions on accounts), the blast radius of a wrong answer is lower — the worst outcome is a
follow-on contact. The rule still applies (a handoff path is still required), but the trigger
criteria can be simpler: confidence below threshold → display "I'm not sure — here's how to
reach our team."

## See also

- [`./deflect-with-answers-not-walls.md`](./deflect-with-answers-not-walls.md)
- [`../skills/deflection-and-knowledge-strategy/SKILL.md`](../skills/deflection-and-knowledge-strategy/SKILL.md) —
  intent taxonomy design step.
- [`../commands/plan-deflection.md`](../commands/plan-deflection.md) — produces the intent taxonomy
  and handoff spec as a design artifact for `claude-app-engineering`.

## Provenance

Reflects the CX industry consensus on AI-assisted support design (Gartner, Forrester, ICMI) and
the specific risk of "bot trapping" — a well-documented failure mode where customers cannot exit
a bot loop to reach a human. The handoff-spec-first discipline is aligned with responsible AI
deployment practice for high-stakes customer interactions.

---

_Last reviewed: 2026-06-08 by `claude`._
