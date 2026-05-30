# Tool errors are prompts too — return what the model should do next

**Status:** Pattern — strong default; returning a raw stack trace or a bare `500` as a tool result wastes the model's chance to self-correct.

**Domain:** Tool use / structured output

**Applies to:** `claude-app-engineering`

---

## Why this exists

In the Messages-API loop a failed tool call comes back to Claude as a `tool_result` — and Claude reads it exactly like any other context. A raw `Traceback (most recent call last)...` or a bare `{"error": 500}` tells the model nothing it can act on, so it retries the same wrong call, gives up, or hallucinates a recovery. A *well-shaped* error result turns a failure into a recoverable step: state what went wrong **and what to do about it** in terms the model can execute (fix this argument, call this other tool, ask the user for this value). The error string is a micro-prompt — write it like one. This is the difference between an agent that recovers from a bad argument in one turn and one that burns turns (and your max-turn budget) flailing.

## How to apply

Return a structured, actionable error as the tool result — what failed, why, and the corrective action — and set `is_error` so the model knows it's a failure, not data.

```python
def call_tool(name, args):
    try:
        return {"ok": True, "data": TOOLS[name](**args)}
    except ValidationError as e:
        # Actionable: name the bad field + the fix, not a stack trace.
        return {"ok": False,
                "error": f"`{e.field}` was {e.got!r}; expected one of {e.allowed}. "
                         f"Retry with a valid `{e.field}`."}
    except NotFound as e:
        return {"ok": False,
                "error": f"No record for customer_id={args.get('customer_id')!r}. "
                         f"Confirm the UUID with the user, or call search_customer by email first."}

# Send it back with is_error so the model treats it as a failure to recover from:
tool_result = {"type": "tool_result", "tool_use_id": tu.id,
               "content": json.dumps(result), "is_error": not result["ok"]}
```

**Do:**
- Say **what failed and what to do next** — the missing/invalid field and the valid range, or the alternate tool to call, or the value to ask the user for.
- Set **`is_error: true`** on a failure `tool_result` so the model treats it as a failure to recover from, not as data to report.
- Keep the message **short and specific** — a precise one-liner beats a paragraph; it's tokens in the next turn.
- Mirror the schema's vocabulary (field names, enum values) so the corrective action maps directly onto a retry ([`tools-design-as-a-contract.md`](./tools-design-as-a-contract.md)).

**Don't:**
- Dump a raw stack trace, a bare HTTP status, or an internal error code the model can't interpret.
- Leak secrets, connection strings, internal hostnames, or PII into the error text — it's untrusted context the model may echo ([`untrusted-content-stays-untrusted.md`](./untrusted-content-stays-untrusted.md)).
- Let a tool *result* (success or error) escalate which tools are available or auto-approve a destructive retry (#7 — that's an injection surface; escalate to `ravenclaude-core/security-reviewer`).

## Edge cases / when the rule does NOT apply

- **Non-recoverable / terminal failures** (auth revoked, hard policy denial) should return a clear *stop* signal, not a "retry like this" — pair with a stop condition so the loop ends instead of looping ([`agent-guardrail-the-loop.md`](./agent-guardrail-the-loop.md)).
- **MCP-server tools** return errors through the protocol's error channel, but the same "actionable, no secrets" discipline applies to the message text ([`mcp-author-the-narrow-server.md`](./mcp-author-the-narrow-server.md)).
- **Truly opaque downstream errors** you can't classify: return a generic safe message *plus* a correlation id for your logs — don't invent a corrective action you can't back.

## See also

- [`../knowledge/tool-use-and-structured-output.md`](../knowledge/tool-use-and-structured-output.md) — the Messages-API loop, `tool_result`, untrusted results
- [`./tools-design-as-a-contract.md`](./tools-design-as-a-contract.md) — the schema whose vocabulary the error should mirror
- [`./agent-guardrail-the-loop.md`](./agent-guardrail-the-loop.md) — stop conditions for non-recoverable errors
- [`../agents/prompt-and-context-engineer.md`](../agents/prompt-and-context-engineer.md) · [`../agents/mcp-and-server-tools-engineer.md`](../agents/mcp-and-server-tools-engineer.md)

## Provenance

Extends house opinion #6 (tools are a contract) and #7 (untrusted results) from [`../CLAUDE.md`](../CLAUDE.md) §3 to the *error* surface of the tool loop. Grounded in [`../knowledge/tool-use-and-structured-output.md`](../knowledge/tool-use-and-structured-output.md) (the `tool_result` / `is_error` mechanics + untrusted-results posture, Anthropic tool-use docs, retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
