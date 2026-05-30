# Structured output via a forced tool call — not a regex over prose

**Status:** Absolute rule — parsing JSON out of prose (or asking for "JSON only" and hoping) is the named anti-pattern (#5).

**Domain:** Tool use / structured output

**Applies to:** `claude-app-engineering`

---

## Why this exists

When an app needs machine-readable output, the unreliable path is to ask Claude to "respond in JSON" and then parse the result with a regex or `json.loads` over free text. It works until it doesn't: a stray sentence of preamble, a trailing markdown fence, a hallucinated field, and the parse throws in production. House opinion #5 makes the reliable path the only path: define a **tool whose `input_schema` is your target shape** and force it with `tool_choice:{type:"tool",name:...}`. Claude fills the schema, you read `tool_use.input` — the structure is constrained by the schema, not coaxed by prose. (This is exactly the mechanism RavenClaude's own Structured Output Protocol uses for agent handoffs — a worked example in this repo.)

## How to apply

Make the schema the contract, force the one tool, and read `tool_use.input`. The schema does the constraining — `required`, types, `enum`, per-field descriptions.

```python
EXTRACT = [{
    "name": "emit_invoice",
    "description": "Emit the parsed invoice. Always call this; never answer in prose.",
    "input_schema": {
        "type": "object",
        "properties": {
            "invoice_number": {"type": "string"},
            "total_cents":    {"type": "integer", "minimum": 0},
            "currency":       {"type": "string", "enum": ["USD", "EUR", "GBP"]},
            "line_items":     {"type": "array", "items": {"type": "object",
                                 "properties": {"sku": {"type": "string"},
                                                "qty": {"type": "integer", "minimum": 1}},
                                 "required": ["sku", "qty"]}},
        },
        "required": ["invoice_number", "total_cents", "currency", "line_items"],
    },
}]
resp = client.messages.create(
    model="claude-haiku-4-5", max_tokens=1024,          # extraction right-sizes to Haiku
    tools=EXTRACT,
    tool_choice={"type": "tool", "name": "emit_invoice"},  # FORCE the one tool
    messages=[{"role": "user", "content": f"<doc>{raw}</doc>"}],
)
data = next(b.input for b in resp.content if b.type == "tool_use")  # already-typed dict
```

**Do:**
- Define the target shape as a tool `input_schema` and force it with `tool_choice:{type:"tool",name:...}`; read `tool_use.input`.
- Put the constraints **in the schema** (`required`, `enum`, `minimum`/`maximum`, per-field `description`) — that's where they bind ([`tools-design-as-a-contract.md`](./tools-design-as-a-contract.md)).
- Keep `tool_choice` **stable** across cached turns — changing it invalidates the message cache ([`cache-the-static-prefix.md`](./cache-the-static-prefix.md)).
- Right-size extraction to a cheap model — schema-constrained extraction is usually a **Haiku** job ([`right-size-with-a-routing-ladder.md`](./right-size-with-a-routing-ladder.md)).

**Don't:**
- Ask for "JSON only" and `json.loads` the text — the named anti-pattern (#5); a forced tool call is the reliable path.
- Leave a free-form `string` where an `enum` is the truth — every unconstrained field is a place the output can drift.
- Forget the schema is still **untrusted input** to your system downstream — validate ranges/identity before acting on it ([`untrusted-content-stays-untrusted.md`](./untrusted-content-stays-untrusted.md)).

## Edge cases / when the rule does NOT apply

- **Prose output** (a summary, an email) is not structured output — specify the shape (headings, length, audience) and prefill, don't force a tool ([`prompt-climb-the-leverage-ladder.md`](./prompt-climb-the-leverage-ladder.md)).
- **A light, low-stakes shape** can use the prefill-`{` fallback to skip preamble — cheaper than a tool, but weaker; the forced tool is the default for anything that must parse.
- **Extended/adaptive thinking** changes prefill availability but not the forced-tool path — the tool route still works with thinking on.
- The tool here exists only to **shape output**, not to call an external system — that's still a tool contract ([`tools-design-as-a-contract.md`](./tools-design-as-a-contract.md)).

## See also

- [`../knowledge/tool-use-and-structured-output.md`](../knowledge/tool-use-and-structured-output.md) — structured output via tools, `tool_choice`, the Messages-API loop
- [`./tools-design-as-a-contract.md`](./tools-design-as-a-contract.md) — the schema discipline this rule depends on
- [`../../ravenclaude-core/skills/structured-output/SKILL.md`](../../ravenclaude-core/skills/structured-output/SKILL.md) — the in-repo worked example of forced-tool output for handoffs
- [`../agents/prompt-and-context-engineer.md`](../agents/prompt-and-context-engineer.md) — owns structured output design

## Provenance

Codifies house opinion #5 from [`../CLAUDE.md`](../CLAUDE.md) §3 ("structured output via tools, not regex") and the §4 anti-pattern ("parsing JSON out of prose instead of a forced tool call"). Grounded in [`../knowledge/tool-use-and-structured-output.md`](../knowledge/tool-use-and-structured-output.md) (Anthropic tool-use docs, retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
