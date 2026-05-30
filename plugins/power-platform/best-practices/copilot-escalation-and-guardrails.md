# Make escalation-to-human a designed feature, with context handoff

**Status:** Pattern — strong default; an agent with no escalation path is a liability, not a product.

**Domain:** Copilot Studio / agent design

**Applies to:** `power-platform`

---

## Why this exists

A bot that **never escalates** is usually hallucinating instead of admitting it doesn't know. The `copilot-studio-bot-design` skill treats escalation-to-human as **a feature, not a failure**: the safe behavior on a low-confidence answer in a sensitive topic, or after N failed slot-fill attempts, is to hand off — not to guess. The second failure is a **context-less handoff**: the agent escalates but the human picks up cold, so the user re-explains everything. The skill is blunt: "a handoff with no context is worse than no bot." Escalation paired with a full context transfer (transcript + detected intent + collected slots + actions taken) turns the agent from a deflection layer into a genuine first line that respects the user's time.

## How to apply

Define explicit escalation triggers, pick one handoff channel and instrument it, and pass the full conversation context across:

```text
Escalation triggers (any → hand off):
  - user explicitly asks ("talk to a person", "agent", "representative")
  - N failed slot-fill attempts (default 3) on a required slot
  - generative answer below confidence threshold in a sensitive topic
  - any topic tagged "always escalate" (legal, complaints, billing disputes)

Handoff channel (pick ONE, instrument it):
  Teams channel | Dynamics Customer Service queue | third-party live chat | email-the-transcript

Context to carry across (NON-negotiable):
  - full conversation transcript
  - detected intent / topic
  - all collected slot values
  - any actions the bot already took (records created, flows called)

Guardrails (bot-level):
  - system prompt: voice + scope + refusal/redirection pattern (match org voice, not a tutorial)
  - content moderation ON; off-topic → redirect pattern, not an attempt
  - strict grounding + citations for generative answers
```

**Do:**
- Enumerate escalation triggers up front; make "always escalate" topics (legal, complaints, billing) explicit.
- Carry transcript + intent + slots + actions-taken into the handoff.
- Write a bot-level system prompt that states scope and a redirection pattern for off-topic asks.
- Track *appropriate* vs *failure* escalations separately — a high escalation rate isn't automatically bad.

**Don't:**
- Ship "the bot will figure it out" with no escalation path.
- Optimize blindly for **containment rate** — a bot that "contains" by hallucinating is worse than one that escalates.
- Hand off with no context and make the user start over.
- Copy a system prompt from a tutorial that doesn't match the org's voice or scope.

## Edge cases / when the rule does NOT apply

- A **purely informational** internal FAQ agent with no transactional actions may have a lighter escalation surface (still needs an "I don't know" path, but maybe not a live-agent queue).
- **Autonomous agents** (no user prompt) escalate to a human-in-the-loop **approval** rather than a live chat — the trigger/guardrail/escalation design still applies (`copilot-agents-2026.md`).
- The **right metric mix** is domain-specific — a transactional bot weights resolution rate; an informational one weights CSAT/accuracy.

## See also

- [`copilot-topic-vs-generative-routing.md`](./copilot-topic-vs-generative-routing.md) — "always escalate" topics are authored, not generative
- [`copilot-grounding-source-selection.md`](./copilot-grounding-source-selection.md) — low-confidence grounded answers should escalate
- [`../knowledge/bi-pages-copilot-decision-trees.md`](../knowledge/bi-pages-copilot-decision-trees.md) — `## Decision Tree: Copilot Studio — Topic vs generative answers`
- [`../skills/copilot-studio-bot-design/SKILL.md`](../skills/copilot-studio-bot-design/SKILL.md) — §6 guardrails, §7 escalation, §10 measurement
- [`../agents/copilot-studio-engineer.md`](../agents/copilot-studio-engineer.md) — owner

## Provenance

Grounded in [Transfer conversations to a live agent](https://learn.microsoft.com/microsoft-copilot-studio/advanced-hand-off), [Content moderation / guardrails](https://learn.microsoft.com/microsoft-copilot-studio/nlu-generative-answers), and the in-house [`copilot-studio-bot-design`](../skills/copilot-studio-bot-design/SKILL.md) skill §7 ("a handoff with no context is worse than no bot") (retrieved 2026-05-30).

---

_Last reviewed: 2026-05-30 by `claude`_
