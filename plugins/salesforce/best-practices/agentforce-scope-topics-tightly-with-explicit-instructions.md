# Scope each topic to one bounded job with explicit instructions — many narrow topics beat one do-everything agent

**Status:** Pattern — strong default; a sprawling, vaguely-instructed topic is a reliability and safety liability.

**Domain:** Agentforce / agent design

**Applies to:** `salesforce`

---

## Why this exists

The Atlas reasoning engine routes a user's request to a **topic** and then plans within that topic's instructions and action set. The breadth of a topic is therefore the breadth of the model's freedom: a wide "Customer Service" topic with twenty loosely-related actions and a paragraph of fuzzy instructions gives the planner room to mis-route, call the wrong action, or blend two jobs into an incoherent plan. Narrow, single-purpose topics ("Check Order Status", "Process Return", "Answer Billing Question") each with a tight action set and **explicit, testable instructions** ("Always confirm the order number before looking it up"; "Never quote a refund amount you have not retrieved from the charge record") shrink that freedom to exactly the job — which makes routing predictable, actions auditable, and the evaluation set tractable. The instructions are not decoration: they are the behavioral contract the model is steered by, and vague instructions ("be helpful") produce vague, unverifiable behavior. This is the design layer beneath house opinion #14's "tight topics, deterministic actions."

## How to apply

Decompose the agent's surface into bounded topics, give each one a minimal action set and explicit do/don't instructions, and write the instructions so an evaluation case can check them.

```
TOPIC = one bounded job. Split when a topic spans two distinct intents.

  Topic: "Check Order Status"
    Actions (minimal): GetOrder (grounded read), GetShipmentTracking (grounded read)
    Instructions (explicit, testable):
      - Always confirm the order number with the customer before looking it up.
      - Answer ONLY from the retrieved order/shipment record; if not found, say so — do not estimate.
      - Do NOT modify the order from this topic; route change requests to "Modify Order".

  Topic: "Process Return"           <- separate topic, NOT folded into the one above
    Actions: CreateReturn (guarded write, requires confirmation), CheckReturnEligibility (grounded read)
    Instructions:
      - Confirm the item and reason before creating a return.
      - Returns over policy limit require a human-approval step (see guardrails).
```

**Do:**
- Give each topic a single, nameable job; split a topic the moment it spans two distinct intents.
- Keep the action set per topic **minimal** — only the actions that job needs, so the planner can't wander.
- Write instructions as explicit, testable statements (confirm X before Y; answer only from retrieved data; never do Z).

**Don't:**
- Build one mega-topic with a grab-bag of actions and "be helpful" instructions — routing and audit both degrade.
- Leave instructions vague or aspirational; if an eval case can't check it, the model can't reliably follow it.
- Duplicate the same action across many topics without reason — it muddies which topic owns a side effect.

## Edge cases / when the rule does NOT apply

A genuinely **simple, single-purpose agent** may legitimately be one topic — the rule is "one topic per job", and a one-job agent has one topic; don't over-split for its own sake. Some Salesforce **standard/pre-built topics** ship with their own scope and instructions; tune within their intent rather than rebuilding them. Topic/action authoring surfaces and the instruction-vs-guardrail split are **fast-moving** in the Agentforce builder — verify the current model `[verify-at-build]`. Where a topic legitimately needs many actions, that is a signal to re-examine whether it's really one job or several wearing one name.

## See also

- [`agentforce-earns-its-non-determinism.md`](./agentforce-earns-its-non-determinism.md) — the placement decision that precedes topic design
- [`agentforce-action-grounding-and-guardrails.md`](./agentforce-action-grounding-and-guardrails.md) — how each topic's actions stay grounded and guarded
- [`agentforce-test-and-evaluate-before-and-after-ship.md`](./agentforce-test-and-evaluate-before-and-after-ship.md) — explicit instructions are what the eval set checks
- [`../knowledge/agentforce-determinism-and-trust.md`](../knowledge/agentforce-determinism-and-trust.md) — Atlas topic/action planning
- [`../agents/agentforce-architect.md`](../agents/agentforce-architect.md) — the agent that owns topic scoping

## Provenance

Codifies the `agentforce-architect`'s "scope the topic tightly — narrow scope beats a do-everything agent" discipline and house opinion #14. Grounded in [`../knowledge/agentforce-determinism-and-trust.md`](../knowledge/agentforce-determinism-and-trust.md), sourced from Salesforce's Atlas reasoning-engine and Agentforce builder (topics/actions/instructions) documentation. Builder specifics are fast-moving — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
