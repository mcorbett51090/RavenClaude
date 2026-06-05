# Make every effectful tool idempotent

**Status:** Absolute rule
**Domain:** Tool use / reliability
**Applies to:** `claude-app-engineering`

---

## Why this exists

Claude can call the same tool more than once: the model retries on a failed result, the app retries a timed-out request, or the Agent SDK re-executes after a session resume. A non-idempotent tool that sends an email, charges a card, or posts a record will execute the side-effect multiple times — silently, from the model's perspective. The Messages-API loop has no built-in at-most-once guarantee; the contract must live in the tool itself.

## How to apply

Every tool that creates, updates, or destroys external state accepts (or generates) a caller-supplied idempotency key and is safe to call twice with the same key.

```python
@tool
def send_notification(user_id: str, message: str, idempotency_key: str) -> dict:
    """Send a notification to a user. Idempotent: duplicate keys are a no-op."""
    if notification_store.exists(idempotency_key):
        return {"status": "already_sent", "idempotency_key": idempotency_key}
    notification_store.send_and_record(user_id, message, idempotency_key)
    return {"status": "sent", "idempotency_key": idempotency_key}
```

Include the idempotency key in the tool's JSON schema so Claude can pass or generate it:

```json
{
  "name": "send_notification",
  "description": "Send a notification to a user. Pass a stable idempotency_key so retries are safe.",
  "input_schema": {
    "type": "object",
    "properties": {
      "user_id": {"type": "string"},
      "message": {"type": "string"},
      "idempotency_key": {"type": "string", "description": "Unique key for this send; reuse to deduplicate."}
    },
    "required": ["user_id", "message", "idempotency_key"]
  }
}
```

**Do:**
- Return a clear `already_done` / `no_op` status on a duplicate key — the model needs to know the action already occurred.
- Generate the key on the caller side (app layer) before the tool call, not inside the tool, so retries use the same key.
- Treat read-only tools (queries, lookups) as inherently idempotent — no extra work needed.

**Don't:**
- Design a tool that silently executes the effect again on a duplicate call.
- Use timestamps or random UUIDs generated *inside* the tool as the idempotency key — they differ on every call.
- Skip this for "rare" write tools; a retry scenario is exactly when "rare" tools fire.

## Edge cases / when the rule does NOT apply

Append operations that are semantically *meant* to stack (e.g., `append_log_entry`) are intentionally non-idempotent if duplicate entries are meaningful. Document that explicitly in the tool description and schema.

## See also

- [`../agents/agent-sdk-engineer.md`](../agents/agent-sdk-engineer.md) — owns the Messages-API loop and retry logic
- [`./tools-design-as-a-contract.md`](./tools-design-as-a-contract.md) — the tool schema and description are the full contract

## Provenance

Codifies `claude-app-engineering/CLAUDE.md` §3 opinion #9 (backoff + idempotency for effects) extended to the tool layer. Standard distributed-systems practice; applied to the LLM tool-use loop where the model — not a human — decides when to retry.

---

_Last reviewed: 2026-06-05 by `claude`_
