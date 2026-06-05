---
name: tool-schema-design
description: "Playbook for designing Claude tool definitions (name, description, JSON Schema input_schema) that maximise correct invocation, minimise hallucinated arguments, and produce clean structured output. Covers naming conventions, description prompting, schema constraints, required vs optional fields, and the forced-tool-call pattern."
---

# Tool Schema Design

## When to invoke

- Authoring a new tool or MCP tool definition.
- Claude is calling the tool with wrong / missing / hallucinated arguments.
- The tool description is duplicating logic that should be in the system prompt (or vice versa).
- You need strict structured output from Claude without using `tool_choice`.

## The three-field contract

Every tool is defined by exactly three things. All three are prompts.

| Field | Claude reads it as | Common mistake |
|---|---|---|
| `name` | The action token. Use a clear verb-noun form: `search_documents`, `create_calendar_event`. | `doThing`, `tool1` — meaningless to the model |
| `description` | The when-and-why. 2–5 sentences: what it does, when to call it, what NOT to call it for, and the side-effect (read vs write). | One sentence that restates the name; no boundary conditions |
| `input_schema` | The argument spec. Each property's `description` is also a prompt — it must say what the value means, its unit, and its format. | No property descriptions; `type: string` with no guidance |

## Step 1 — Write the description first

Before touching `input_schema`, answer these four questions in the description:

1. What does this tool do (one sentence)?
2. When should Claude choose this tool over alternatives?
3. What must NOT trigger this tool?
4. Does it have side-effects (writes, sends, deletes)?

Example:

```
"description": "Search the internal knowledge base for articles matching a query.
Use this tool when the user asks a question that may be answered by documented
policies or procedures. Do NOT use this tool for real-time data (prices, status) —
use get_live_status instead. Read-only; no side-effects."
```

## Step 2 — Design the input_schema

Rules in priority order:

1. **Every property has a `description`.** Even `id: string` needs: `"The UUID of the document, e.g. '3fa85f64-5717-4562-b3fc-2c963f66afa6'."` — the example anchors the format.
2. **Use `enum` for bounded sets** (status values, categories). Claude will pick from the list rather than invent strings.
3. **Mark only truly-required fields as `required`.** Over-requiring forces Claude to guess when the user hasn't provided a value.
4. **Avoid deep nesting** — prefer flat schemas with clear names over nested objects Claude may forget to populate.
5. **`default` values reduce hallucination** on optional numeric params.

```json
{
  "name": "search_documents",
  "description": "Search the knowledge base...",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The full-text search query. Use natural language, not keywords."
      },
      "max_results": {
        "type": "integer",
        "description": "Maximum number of results to return. Default 5; max 20.",
        "default": 5
      },
      "category": {
        "type": "string",
        "enum": ["policy", "procedure", "reference", "faq"],
        "description": "Filter results to a document category. Omit to search all categories."
      }
    },
    "required": ["query"]
  }
}
```

## Step 3 — Forced tool call for structured output

To extract a strict JSON structure from Claude without regex-parsing prose:

1. Define a tool whose name describes the output (e.g., `extract_invoice_fields`).
2. Set `tool_choice: {"type": "tool", "name": "extract_invoice_fields"}`.
3. The `input` of the returned `tool_use` block is your parsed struct — no JSON.loads of prose needed.

This is more reliable than asking Claude to "return JSON" in the system prompt.

## Tool-set discipline

| Rule | Why |
|---|---|
| Build the tools array once at startup — module-level constant | Mutating it per-request busts the prompt-cache breakpoint |
| Keep tool count ≤ 10 for complex tasks | More tools dilute each description's attention |
| Split read and write tools explicitly | Claude respects the boundary when you name it |
| Remove tools the current turn cannot use | Reduces hallucinated calls on irrelevant tools |

## Pitfalls

- A description that says "use this when the user says X" — description-as-trigger-string is fragile; describe the semantic intent, not the surface wording.
- Omitting side-effect disclosure — Claude over-calls write tools when it doesn't know they mutate state.
- Schema with `additionalProperties: true` on a forced-output tool — Claude invents keys the code doesn't expect.
- Putting the tool's business rules in the system prompt instead of the tool description — when tool set changes, the system prompt becomes stale.
