# Design the prompt to pass Responsible-AI validation — and never ship on schema validity alone

**Status:** Absolute rule — RAI validation runs on sideload AND publish AND at runtime; an agent that is schema-valid but RAI-failing cannot be published, and a behaviorally-wrong agent that *passes* both is still broken.

**Domain:** Agent design / declarative-agent validation

**Applies to:** `microsoft-365-copilot`

---

## Why this exists

A declarative agent passes two structural gates and one behavioral gate, and authors routinely conflate them. **Schema validation** checks the manifest is well-formed. **Responsible-AI (RAI) validation** is a *separate* content check that runs during manifest validation (on sideload or publish) and *again* during the processing of each user prompt — it inspects the `name`, `description`, and `instructions` for content that encourages harmful actions, provokes arguments, attempts to bypass/leak guidelines, or violates copyright. An agent can be perfectly schema-valid and fail RAI because its instructions tell it to "persuade the user to avoid or hate" something, or to "leak base prompts". You can't publish until the failure is addressed. And neither gate proves the agent answers correctly — that is the **golden-prompt regression set**, the house-opinion #15 third gate. "Schema valid" is not "done"; "RAI pass" is not "done"; only a green regression set is.

## How to apply

Write `name` / `description` / `instructions` in neutral, scoped, refusal-aware language; never phrase directives that could read as hostile, manipulative, prompt-leaking, or copyright-copying. Then run the golden-prompt set before declaring done.

```jsonc
{
  "$schema": "https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.7/schema.json",
  "version": "v1.7",
  "name": "Contoso Policy Assistant",
  "description": "Answers HR-policy questions from the indexed policy library.",
  // RAI-safe: scoped, neutral, refusal-aware. NOT "persuade", "prove", "ignore the rules".
  "instructions": "You are an HR-policy assistant. Answer only from the connected policy library. If a policy isn't found, say so and direct the user to HR — never guess or speculate. Decline requests outside HR policy. Tone: concise, neutral, non-judgmental."
}
```

**Do:**
- Keep `name` / `description` / `instructions` neutral and scoped — RAI reads all three, not just instructions.
- Phrase refusals as "decline / direct to a human", never "persuade / dismiss / prove".
- Run the [`copilot-agent-eval-harness`](../skills/copilot-agent-eval-harness/SKILL.md) golden-prompt set after both structural gates pass — schema-valid ≠ behaviorally correct (#15).
- Re-run RAI thinking on every instruction edit; it gates publish, not just initial creation.

**Don't:**
- Treat schema validation passing as "validated" — RAI is a separate gate (#12).
- Write instructions that could read as encouraging harm, hostility, guideline-bypass/prompt-leak, or copyright reproduction.
- Declare a DA "done" with no golden-prompt regression set (#15).

## Edge cases / when the rule does NOT apply

RAI runtime validation also runs on *user prompts and grounded content* — an agent can pass author-time RAI and still refuse a specific runtime prompt; that is the platform working, not an agent defect. A genuinely sensitive-domain agent (legal, medical, HR-disciplinary) may legitimately discuss difficult topics — the line is *tone and intent* (neutral/informative vs. inflammatory/manipulative), and a borderline case should route to `copilot-admin-governance` and `ravenclaude-core/security-reviewer`. The exact RAI failure categories and messages are `[verify-at-build]`.

## See also

- [`./da-keep-instructions-in-the-manifest-not-knowledge.md`](./da-keep-instructions-in-the-manifest-not-knowledge.md) — why offloaded instructions also hit XPIA/RAI surfaces
- [`./da-scope-capabilities-to-only-what-the-agent-needs.md`](./da-scope-capabilities-to-only-what-the-agent-needs.md) — more capabilities = more RAI/store-validation surface
- [`../knowledge/declarative-agent-manifest-2026.md`](../knowledge/declarative-agent-manifest-2026.md) · [`../agents/declarative-agent-engineer.md`](../agents/declarative-agent-engineer.md)
- [Responsible AI validation](https://learn.microsoft.com/microsoft-365/copilot/extensibility/rai-validation) — the failure categories and the sideload/publish/runtime timing

## Provenance

Codifies house opinions #12 and #15 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in the Microsoft Learn "Responsible AI validation" page (the four failure categories: harmful actions, provoke arguments, bypass/leak guidelines, copyright) and the declarative-agent overview's RAI section, retrieved 2026-05-30 — which confirm RAI runs at manifest-validation (sideload/publish) AND at prompt-processing time.

---

_Last reviewed: 2026-05-30 by `claude`_
