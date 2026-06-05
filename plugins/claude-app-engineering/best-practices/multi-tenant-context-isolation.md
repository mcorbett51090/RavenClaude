# Isolate context and tool access per tenant, not per session

**Status:** Absolute rule
**Domain:** Multi-tenancy / security
**Applies to:** `claude-app-engineering`

---

## Why this exists

A multi-tenant Claude app that routes different customers through a shared
message history, shared tool set, or shared Files-API namespace is one missed
`tenant_id` filter away from a cross-tenant data leak. Because Claude reads every
token in the context window, any tenant's data present in another tenant's prompt
is a confidentiality breach — even if the model is "told" to ignore it. The
enforcement must be structural, not instructional.

## How to apply

1. **Scope the system prompt** — inject tenant-specific constraints at the
   system-prompt layer, not as user messages (user messages are untrusted input).
2. **Scope tool permissions** — resolve the permitted tool set per tenant before
   constructing the request; don't pass a super-set and rely on the model to
   restrict itself.
3. **Scope Files API files** — file IDs are global to the workspace by default;
   tag and filter by `tenant_id` in your metadata layer so `list_files` never
   returns another tenant's files.
4. **Never share session history** — start a clean session per tenant interaction;
   never re-use a session object across tenants.

```python
def build_request(tenant: Tenant, user_message: str):
    tools = tool_registry.resolve(tenant.permitted_tool_ids)
    system = (
        f"You assist {tenant.display_name}. "
        f"You may only access data in workspace {tenant.workspace_id}. "
        "Never reference data from other tenants."
    )
    messages = session_store.get_clean_session(tenant.id)
    messages.append({"role": "user", "content": user_message})
    return {"system": system, "tools": tools, "messages": messages}
```

**Do:**
- Enforce isolation structurally (session scoping, file-id filtering, tool
  allow-list resolution) before the API call.
- Treat the system prompt as the tenant boundary declaration.
- Audit-log tool calls with `tenant_id` so cross-tenant access attempts are
  detectable.

**Don't:**
- Pass a full tool set and instruct the model not to use certain tools for this
  tenant — the instruction can be overridden by injection.
- Share a Files-API namespace without explicit per-file tenant tagging.
- Carry session history across tenant boundaries even "for efficiency."

## Edge cases / when the rule does NOT apply

- Single-tenant deployments (one customer, one workspace): isolation is trivially
  satisfied but the structural patterns still prevent accidental data mixing
  across test/prod environments.
- Public-data-only tools (e.g. web search): no tenant data, so shared tool access
  is acceptable.

## See also

- [`../agents/agent-sdk-engineer.md`](../agents/agent-sdk-engineer.md) — session isolation in the Agent SDK
- [`./untrusted-content-stays-untrusted.md`](./untrusted-content-stays-untrusted.md) — injection is the complementary threat
- [`./agent-sdk-session-isolation.md`](./agent-sdk-session-isolation.md) — session-level isolation mechanics

## Provenance

Codifies the AI-app security section of
`knowledge/claude-app-finops-reliability-and-security.md` (retrieved 2026-05-28)
and standard multi-tenant SaaS isolation practice applied to LLM-backed apps.
Security verdict escalates to `ravenclaude-core/security-reviewer`.

---

_Last reviewed: 2026-06-05 by `claude`_
