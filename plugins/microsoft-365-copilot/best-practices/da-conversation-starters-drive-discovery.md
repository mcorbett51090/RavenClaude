# Write conversation starters that demonstrate the agent's unique value — not generic prompts

**Status:** Pattern
**Domain:** Declarative agent authoring
**Applies to:** `microsoft-365-copilot`

---

## Why this exists

Conversation starters are the first thing a user sees when they open a declarative agent. They are not labels — they are working prompts that Copilot executes immediately when clicked, providing the user's first live experience of the agent. Generic starters ("Tell me about your capabilities", "What can you do?") provide zero domain value, train users to ignore them, and fail to showcase the grounding sources the agent provides. Well-crafted starters that reflect a real user need (specific, actionable, domain-relevant) reduce time-to-value and differentiate the agent from a plain Copilot conversation.

## How to apply

Conversation starters live in the manifest under `conversationStarters`:

```json
{
  "conversationStarters": [
    {
      "text": "What is the current refund policy for digital products?"
    },
    {
      "text": "Summarize the top 3 open P1 incidents from this week's ServiceNow connector"
    },
    {
      "text": "What changed in our benefits package for the 2026 enrollment year?"
    },
    {
      "text": "Draft a response to a customer asking about our SLA for premium support"
    }
  ]
}
```

Quality checklist for each starter:
- [ ] **Specific** — names a real domain concept (policy, product, system) rather than describing the agent abstractly.
- [ ] **Actionable** — the user immediately gets a useful result, not a menu of options.
- [ ] **Grounded** — the starter is answerable from the agent's knowledge sources, not from Copilot's general knowledge.
- [ ] **Distinct** — each starter demonstrates a different capability or persona need.
- [ ] **Under ~100 characters** — longer starters are truncated in the UI `[verify-at-build]`.

**Do:**
- Test every starter in the Agents Toolkit Playground before publishing — it must return a grounded, non-hallucinated answer.
- Update starters when the agent's knowledge sources change — a starter that no longer returns a valid answer is a trust-eroding experience.
- Include at least one starter per major persona the agent serves (e.g., one for HR, one for IT, one for managers).

**Don't:**
- Use "Tell me about yourself" or "What can you help with?" as starters — they add no domain value.
- Write starters that require follow-up slot-filling to be useful — starters should be self-contained.
- Exceed 4 starters (the Copilot UI displays 4; additional starters may not surface `[verify-at-build]`).

## Edge cases / when the rule does NOT apply

For a prototype or pilot with a small internal audience briefed on the agent's purpose, generic starters are acceptable during the test phase. Replace them before broader rollout.

## See also

- [`../agents/declarative-agent-engineer.md`](../agents/declarative-agent-engineer.md) — owns manifest authoring including conversation starters
- [`./da-keep-instructions-in-the-manifest-not-knowledge.md`](./da-keep-instructions-in-the-manifest-not-knowledge.md) — the instructions budget that determines what the starters can trigger

## Provenance

Codifies the `declarative-agent-manifest-authoring` skill from CLAUDE.md §9 applied to the conversation starters field; Microsoft Learn declarative-agent manifest documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
