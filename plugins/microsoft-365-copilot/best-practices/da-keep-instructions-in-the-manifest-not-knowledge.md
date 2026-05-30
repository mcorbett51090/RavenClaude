# Keep declarative-agent instructions in the manifest — never offload them to a knowledge source

**Status:** Absolute rule — offloading instructions to a knowledge source is a runtime-integrity *and* security failure, not a budget workaround.

**Domain:** Agent design / declarative-agent instructions

**Applies to:** `microsoft-365-copilot`

---

## Why this exists

The declarative-agent `instructions` field is a hard **8,000-character** cap (verified against schema v1.7, [`../knowledge/declarative-agent-manifest-2026.md`](../knowledge/declarative-agent-manifest-2026.md)). The tempting hack when you blow it is to dump the overflow into a SharePoint doc or other knowledge source and tell the agent to "follow the instructions in document X." Microsoft explicitly warns against this: knowledge-source content is **not trusted maker-authored instruction content**. It is run through cross-prompt-injection (XPIA) classifiers, so directive language can be silently blocked, truncated, or sanitized at runtime — producing unpredictable behavior. Worse, it widens the attack surface: anyone with edit access to that document can change the agent's behavior at runtime, bypassing the manifest's authoring, versioning, and governance controls. Knowledge sources ground *facts*; they are not a system-prompt extension. The fix for an over-budget agent is to **shorten the instructions**, not to relocate them.

## How to apply

Treat 8,000 chars as a design constraint. Instructions hold role + scope + tone + refusal rules + step-by-step behavior; reference *data* lives in grounding and is referenced by property description, not copied into the prompt.

```jsonc
{
  "$schema": "https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.7/schema.json",
  "version": "v1.7",
  "name": "Contoso Policy Assistant",
  "description": "Answers HR-policy questions from the indexed policy library.",
  // ≤ 8,000 chars. Behavior only. NOT "see the rules in /sites/hr/agent-rules.docx".
  "instructions": "You are an HR-policy assistant. Answer only from the connected policy library. If a policy isn't found, say so and point to HR — never guess. Tone: concise, neutral...",
  "capabilities": [
    { "name": "GraphConnectors", "connections": [{ "connection_id": "contosoPolicies" }] }
  ]
}
```

**Do:**
- Keep all behavioral directives **inside** `instructions`, under 8,000 chars.
- When over budget, compress: remove redundancy, collapse examples, push factual reference into grounding (which the agent reads as data, not instructions).
- Give connector/knowledge **property descriptions** so the agent knows how to *use* the grounded data — that is the right place for "how to read this source."

**Don't:**
- Store or offload instructions in a SharePoint document or any knowledge source to dodge the 8,000-char cap — XPIA classifiers may block/sanitize it and anyone with edit access can hijack behavior.
- Treat a knowledge source as a system-prompt extension. It is not honored as instructions and there is no guarantee it will be.

## Edge cases / when the rule does NOT apply

`editorial_answers` (v1.7) are predefined question-answer pairs matched by semantic similarity — a *legitimate* manifest mechanism for canned responses, distinct from offloading free-form instructions. Property *descriptions* in a connector schema are encouraged to be surfaced to the agent so it understands the data — that is grounding metadata, not behavioral instructions, and is fine.

## See also

- [`./design-to-66-percent-of-the-declarative-agent-wall.md`](./design-to-66-percent-of-the-declarative-agent-wall.md) — the budget wall this rule sits inside
- [`../knowledge/declarative-agent-manifest-2026.md`](../knowledge/declarative-agent-manifest-2026.md) — schema v1.7 limits + capability map
- [`../agents/declarative-agent-engineer.md`](../agents/declarative-agent-engineer.md) — the agent that enforces the instruction budget
- [Write effective instructions for declarative agents](https://learn.microsoft.com/microsoft-365/copilot/extensibility/declarative-agent-instructions) — the explicit Microsoft warning against offloading

## Provenance

Grounded in the Microsoft Learn "Write effective instructions" page (the boxed XPIA warning) and the declarative-agent v1.7 schema (`instructions` ≤ 8,000 chars), both retrieved 2026-05-30. Extends house opinion #3 (the instructions budget) from [`../CLAUDE.md`](../CLAUDE.md).

---

_Last reviewed: 2026-05-30 by `claude`_
