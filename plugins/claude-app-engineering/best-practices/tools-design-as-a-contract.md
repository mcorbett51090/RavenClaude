# Tools are a contract — the description is the prompt, the schema is the guardrail

**Status:** Absolute rule — a thin tool description plus "the system prompt will fix it" is the named anti-pattern.

**Domain:** Tool use / structured output

**Applies to:** `claude-app-engineering`

---

## Why this exists

A tool is `{name, description, input_schema}`, and Claude decides *when* and *how* to call it almost entirely from those three fields — not from a system-prompt nudge bolted on afterward. The description **is** the prompt: it's the only place the model learns what the tool does, when to use it, and what each parameter means. A well-typed JSON Schema (`required`, types, `enum`, per-field descriptions) does more for call accuracy than any amount of surrounding instruction, because it constrains the model's output space directly. The recurring failure is a one-line description ("searches the DB") paired with a loose schema, then patching the resulting wrong/missing calls in the system prompt — which doesn't generalize and silently busts the cache every time it's re-tuned.

## How to apply

Write each tool description like you're briefing a new engineer; make the schema do the constraining. Build the tool list **once** and pass the identical object every call.

```python
TOOLS = [{
    "name": "search_orders",
    # Description = the prompt: what it does, WHEN to use it, params, edge cases.
    "description": (
        "Search a customer's orders by status and date range. "
        "Use when the user asks about order history or a specific order's state. "
        "Returns up to `limit` orders newest-first. "
        "Do NOT use for refunds (use issue_refund) or for shipment tracking (use track_shipment)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "customer_id": {"type": "string", "description": "The customer's UUID, not their email."},
            "status": {"type": "string", "enum": ["pending", "shipped", "delivered", "cancelled"],
                       "description": "Filter by order status; omit for all statuses."},
            "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 20},
        },
        "required": ["customer_id"],
    },
}]
# tool_choice stays stable across cached turns; changing it invalidates the message cache.
```

**Do:**
- Spend the description budget: what it does, **when to use it**, what each param means, and when *not* to use it (disambiguate from neighboring tools).
- Constrain in the **schema** — `required`, types, `enum`, `minimum`/`maximum`, per-field `description` — rather than in prose.
- Build the tool array once and pass the **same object** every call; keep `tool_choice` stable across cached turns ([`cache-the-static-prefix.md`](./cache-the-static-prefix.md)).
- Enable **parallel tool use** by default (Claude can emit multiple `tool_use` blocks; execute concurrently) unless your tools have ordering dependencies.

**Don't:**
- Ship a thin description and hope the system prompt fixes call accuracy — the named anti-pattern (#6).
- Regenerate or reorder tool definitions per request — busts every cache downstream ([`cache-the-static-prefix.md`](./cache-the-static-prefix.md)).
- Leave a free-form `string` where an `enum` is the truth — every unconstrained field is a place the model can drift.

## Edge cases / when the rule does NOT apply

- **A capability reused across apps/clients** is an MCP server, not an in-process tool — the contract discipline is identical but the home differs ([`mcp-vs-in-process-tool.md`](./mcp-vs-in-process-tool.md)).
- **Forced structured-output** uses the same tool shape but pins `tool_choice:{type:"tool",name:...}` — see [`output-structured-via-forced-tool.md`](./output-structured-via-forced-tool.md).
- **Genuinely ordered tools** (B must follow A) are the one case to disable parallel tool use.
- **Untrusted tool *results*** are a separate concern — never let a result escalate tool access ([`tools-actionable-error-messages.md`](./tools-actionable-error-messages.md) covers errors; injection → `ravenclaude-core/security-reviewer`).

## See also

- [`../knowledge/tool-use-and-structured-output.md`](../knowledge/tool-use-and-structured-output.md) — tools-as-contract, `tool_choice`, parallel tools, the Messages-API loop
- [`./output-structured-via-forced-tool.md`](./output-structured-via-forced-tool.md) — the forced-tool path for machine-readable output
- [`./mcp-vs-in-process-tool.md`](./mcp-vs-in-process-tool.md) — when the tool should be an MCP server instead
- [`../agents/prompt-and-context-engineer.md`](../agents/prompt-and-context-engineer.md) — owns in-app tool design + the loop

## Provenance

Codifies house opinion #6 from [`../CLAUDE.md`](../CLAUDE.md) §3 ("tools are a contract; the description is the prompt") and the §4 anti-pattern ("a thin tool description and hoping the system prompt fixes it"). Grounded in [`../knowledge/tool-use-and-structured-output.md`](../knowledge/tool-use-and-structured-output.md) (Anthropic tool-use docs, retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
