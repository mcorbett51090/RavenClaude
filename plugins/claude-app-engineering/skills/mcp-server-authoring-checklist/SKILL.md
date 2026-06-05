---
name: mcp-server-authoring-checklist
description: "Gate-by-gate checklist for shipping a production MCP server: transport selection, tool-schema quality, auth wiring, error-response contract, and the security hand-off items that must escalate to core/security-reviewer. Owned by mcp-and-server-tools-engineer."
---

# MCP Server Authoring Checklist

## When to invoke

- Authoring a new MCP server from scratch.
- Reviewing an existing MCP server before it is installed in a production Claude session.
- Debugging a server whose tools are being called incorrectly or not at all.

## Gate 1 — Transport selection

| Transport | Choose when | Avoid when |
|---|---|---|
| `stdio` | Local tool (CLI, dev machine, same process) | Multi-client or networked deployment |
| `SSE` (HTTP + Server-Sent Events) | Remote, multi-client, cloud-hosted | Environments that block long-lived HTTP connections |
| Streamable HTTP | High-throughput, resumable, new deployments (MCP 2025-11+) | Clients not yet upgraded to 2025-11 spec |

## Gate 2 — Tool definition quality

For each tool, verify:

- [ ] `name`: verb-noun, kebab-case, globally unique across the server (`search_documents` not `search`).
- [ ] `description`: 3–5 sentences covering what it does, when to call it, when NOT to call it, and whether it has side-effects (read vs write vs delete). This is a prompt — write it as one.
- [ ] `inputSchema.properties`: every property has a `description` with format hint and example value.
- [ ] `required`: only fields the tool cannot function without; optional fields have `default` values.
- [ ] No `additionalProperties: true` on write tools — prevents hallucinated keys.

## Gate 3 — Auth wiring

| Scenario | Recommended approach |
|---|---|
| Internal/local server | No auth (`stdio`) |
| OAuth user-delegated | MCP OAuth 2.1 flow; use PKCE; **do not pass tokens via tool arguments** |
| Service-to-service | Client credentials; use environment variable / secret manager injection at server startup |
| API keys for downstream services | Injected as env vars at server start; **never** in the tool schema or description |

Escalate to `ravenclaude-core/security-reviewer` if: the server handles user PII, calls a payment/healthcare API, or accepts tokens in tool arguments.

## Gate 4 — Error response contract

Every tool handler must return a structured error on failure — not an unhandled exception:

```json
{
  "isError": true,
  "content": [{"type": "text", "text": "Search failed: index unavailable (503). Retry in 30 s."}]
}
```

| Rule | Why |
|---|---|
| Return `isError: true` in the tool result, not an exception | The MCP runtime surfaces it to Claude; an exception terminates the session |
| Include a human-readable message and a retry hint | Claude can relay the hint to the user or decide to retry |
| Never include stack traces or internal paths in the error | Information disclosure |
| Log the full error server-side; return only the user-safe summary | Debugging without leaking internals |

## Gate 5 — Security hand-off checklist

These items **must** be reviewed by `ravenclaude-core/security-reviewer` before production install:

- [ ] Tool handlers sanitise all inputs before passing to shell / SQL / file system.
- [ ] No tool allows path traversal (`../../`) or shell injection.
- [ ] Tool results from user-controlled or web-fetched content are wrapped in an XML isolation tag before returning, to prevent prompt-injection escalation.
- [ ] Secrets (API keys, DB passwords) are injected via env at startup — not hardcoded, not in tool descriptions.
- [ ] Scopes exposed by the server are the minimum required — no catch-all tool that reads the whole file system.

## Gate 6 — Operational readiness

- [ ] `list_tools` is implemented and returns current schemas (no stale cached schema).
- [ ] Server handles graceful shutdown (`SIGTERM`/`SIGINT`) without dropping in-flight tool calls.
- [ ] Version is pinned in the server manifest (`version` field); bump on any schema change.
- [ ] Tested with the MCP Inspector (`npx @modelcontextprotocol/inspector`) before install.

## Pitfalls

- A `description` that mirrors the `name` with no boundary conditions — Claude over-calls tools when it can't distinguish them.
- Returning raw upstream API errors in tool results — stack traces and internal URLs are information disclosures and confuse the model.
- Installing the server with `*` scope on a production agent that has destructive tools — scope to the minimum tool set the agent needs.
- Changing a tool's `name` or `inputSchema` without bumping the server version — clients cache the old schema.
