# Route high-stakes intents to authored topics, everything else to generative answers

**Status:** Pattern — strong default; the boundary test below decides each intent.

**Domain:** Copilot Studio / agent design

**Applies to:** `power-platform`

---

## Why this exists

A Copilot Studio agent answers an utterance one of two ways: an **authored topic** (deterministic — it says exactly what you wrote, with slot-filling and explicit branches) or **generative answers** (RAG over knowledge sources — an LLM composes a grounded but non-deterministic reply). Putting a regulated or high-blast-radius intent on generative answers means a customer can get a confidently-wrong response that nobody reviewed; putting a broad informational FAQ into authored topics means dozens of brittle hand-built branches that go stale. The `copilot-studio-bot-design` skill frames the line with one test: **"if a user gets a wrong answer here, who explains it to compliance/legal/the customer?"** If that's a real person, it's a topic. The cost of getting this wrong is asymmetric — a wrong FAQ answer is an annoyance; a wrong "how do I file an insurance claim" answer is a liability.

## How to apply

Classify each intent against the boundary, then author topics for the high-stakes set and let generative answers cover the long tail. Give topics a **range** of trigger phrases (8–15 distinct phrasings of the intent, not synonyms of one phrase):

```yaml
# Topic: "File a claim"  — high-stakes, slot-filled, deterministic  → AUTHORED TOPIC
trigger_phrases:        # range of intent, not 8 variants of one wording
  - "file a claim"
  - "I need to report damage"
  - "start an insurance claim"
  - "my car was in an accident"
  - "how do I get reimbursed"
slots:
  - { name: policyNumber, required: true,  validation: "^[A-Z]{3}-\\d{5}$", reprompt: "Format like ABC-12345" }
  - { name: incidentDate, required: true,  validation: date }
confirm_before_submit: true        # show collected values, ask "is this right?" before the irreversible action
on_max_attempts: escalate_to_human # after 3 failed slot attempts

# Everything else (product FAQ, hours, policy explanations) → GENERATIVE ANSWERS over curated knowledge sources
```

**Do:**
- Author a topic when content is **regulated**, the action is **high-blast-radius/irreversible**, the answer needs a **specific format**, or **slot-filling** is required.
- Use generative answers for broad, slow-changing informational Q&A over **curated** sources.
- Confirm collected values before any irreversible action; escalate to a human after N failed slot attempts.
- Re-run the regression test set (10–30 prompts) on **every** authoring change.

**Don't:**
- Build one mega-topic with 47 branches instead of decomposing into focused topics.
- Let generative answers field high-stakes/regulated intents because "the LLM probably knows."
- Ship trigger phrases that are all variants of one wording (narrow training data = brittle triggering).

## Edge cases / when the rule does NOT apply

- **Hybrid topics** are legitimate: an authored topic can *call* generative answers for a sub-question while keeping the surrounding flow deterministic.
- A **single-shot informational** intent with a compliance-sensitive answer can still warrant a topic even without slot-filling — the format/review requirement alone justifies it.
- For an internal, low-stakes, individual-scope agent, the whole topic-vs-generative tension may be moot — a declarative M365 Copilot agent may be the right tool entirely (see `copilot-agents-2026.md`).

## See also

- [`copilot-grounding-source-selection.md`](./copilot-grounding-source-selection.md) — generative answers are only as good as their knowledge sources
- [`copilot-escalation-and-guardrails.md`](./copilot-escalation-and-guardrails.md) — the escalation path that "always escalate" topics route to
- [`../knowledge/bi-pages-copilot-decision-trees.md`](../knowledge/bi-pages-copilot-decision-trees.md) — `## Decision Tree: Copilot Studio — Topic vs generative answers`
- [`../skills/copilot-studio-bot-design/SKILL.md`](../skills/copilot-studio-bot-design/SKILL.md) — §2 the boundary, §4 trigger phrases, §5 slot-filling
- [`../knowledge/copilot-agents-2026.md`](../knowledge/copilot-agents-2026.md) — which builder before which routing
- [`../agents/copilot-studio-engineer.md`](../agents/copilot-studio-engineer.md) — owner

## Provenance

Grounded in [Copilot Studio topics](https://learn.microsoft.com/microsoft-copilot-studio/authoring-create-edit-topics), [generative answers](https://learn.microsoft.com/microsoft-copilot-studio/nlu-boost-conversations), and the in-house [`copilot-studio-bot-design`](../skills/copilot-studio-bot-design/SKILL.md) skill §2 boundary test (retrieved 2026-05-30).

---

_Last reviewed: 2026-05-30 by `claude`_
