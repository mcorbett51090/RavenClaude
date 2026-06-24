# Structured output via a schema-constrained path — not a regex over prose

**Status:** Absolute rule — the output must be **schema-constrained**; parsing JSON out of prose (or asking for "JSON only" and hoping) is the named anti-pattern (#5).

> **2026-06 update — two GA schema-constrained paths.** Native **Structured Outputs** (`output_config.format` for JSON-schema-constrained responses; `strict:true` for strict tool *inputs*) is now GA on the Claude API and is the **preferred** path where the target model supports it (availability varies by platform — see the [capability map](../knowledge/model-selection-and-2026-capability-map.md); `[verify-at-use]`). The **forced tool call** below remains fully valid and is the right choice when the same call must also invoke a side-effecting tool, when you want schema-validated tool *inputs*, or on a runtime/model without native Structured Outputs. The discipline is identical: **the schema is the contract** — choose the path, don't `json.loads` over prose.

**Domain:** Tool use / structured output

**Applies to:** `claude-app-engineering`

---

## Why this exists

When an app needs machine-readable output, the unreliable path is to ask Claude to "respond in JSON" and then parse the result with a regex or `json.loads` over free text. It works until it doesn't: a stray sentence of preamble, a trailing markdown fence, a hallucinated field, and the parse throws in production. House opinion #5 makes the schema the constraint: either let native Structured Outputs grammar-constrain the response (`output_config.format`), or define a **tool whose `input_schema` is your target shape** and force it with `tool_choice:{type:"tool",name:...}`. Either way Claude fills the schema, you read the typed result — the structure is constrained by the schema, not coaxed by prose. (The forced-tool path is exactly the mechanism RavenClaude's own Structured Output Protocol uses for agent handoffs — a worked example in this repo.)

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
- Ask for "JSON only" and `json.loads` the text — the named anti-pattern (#5); a schema-constrained path (native Structured Outputs or a forced tool call) is the reliable one.
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

Codifies house opinion #5 from [`../CLAUDE.md`](../CLAUDE.md) §3 (the "structured output via a schema-constrained path, not regex" opinion — reworded 2026-06-24 from the original "via tools, not regex" when native Structured Outputs went GA) and the §4 anti-pattern ("parsing JSON out of prose instead of a schema-constrained path"). Grounded in [`../knowledge/tool-use-and-structured-output.md`](../knowledge/tool-use-and-structured-output.md) (Anthropic tool-use + structured-outputs docs, retrieved 2026-05-28 / 2026-06-24).

---

_Last reviewed: 2026-05-30 by `claude`_
