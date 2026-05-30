# Pin the plugin-manifest version and map each function's `name` to an OpenAPI `operationId` — verified both ways

**Status:** Absolute rule — the `name`↔`operationId` binding is the contract that lets Copilot invoke the API; a mismatch silently breaks invocation or fires the wrong operation.

**Domain:** Grounding / API plugins (actions)

**Applies to:** `microsoft-365-copilot`

---

## Why this exists

An API plugin is four files (app manifest + plugin manifest + OpenAPI spec + adaptive-card templates), and the load-bearing wiring is the binding between the **plugin manifest** and the **OpenAPI spec**. In the plugin manifest, each function's `name` is the function identifier; when that function is bound to an OpenAPI runtime, **`name` must exactly match an `operationId` in the OpenAPI description**, and it must satisfy `^[A-Za-z0-9_]+$`. If the names don't line up, Copilot either can't call the operation at all or — worse — binds to the wrong one and silently calls a different endpoint. The second failure source is the **version**: the plugin manifest is its own versioned schema (currently **v2.4**, separate from the DA manifest's v1.7), and v2.4 added MCP `RemoteMCPServer` runtime support and changed `isNonConsequential` behavior for GET actions — authoring against "latest" or an old version drifts your validation. Finally, each operation needs a clear, **model-readable `description`** because Copilot uses it to decide *whether and how* to call. Verify the mapping in both directions, pin the version, and write descriptions for the model. This is house opinion #2 (pin) plus the `operationId` contract.

## How to apply

Pin `schema_version`. For every plugin-manifest function, confirm a same-named `operationId` exists in the OpenAPI, and for every Copilot-reachable `operationId`, confirm a function references it. Give every operation a model-readable description.

```jsonc
// plugin manifest (ai-plugin.json) — PINNED version; function name == operationId
{
  "schema_version": "v2.4",
  "name_for_human": "Contoso Tickets",
  "functions": [
    {
      "name": "getTicketById",                 // <-- MUST equal an OpenAPI operationId; ^[A-Za-z0-9_]+$
      "description": "Retrieves a single support ticket by its numeric ID. Use when the user names a ticket number."
    }
  ],
  "runtimes": [
    {
      "type": "OpenApi",
      "spec": { "url": "apiSpec/openapi.yaml" },
      "run_for_functions": ["getTicketById"]    // <-- binds the function to the OpenAPI runtime
    }
  ]
}
```

```yaml
# openapi.yaml — operationId matches the function name exactly
paths:
  /tickets/{id}:
    get:
      operationId: getTicketById            # <-- exact match, both directions
      description: Retrieves a single support ticket by its numeric ID.
```

**Do:**
- Pin `schema_version` (currently **v2.4**, `[verify-at-build]`) — it is a *different* schema from the DA manifest.
- Verify **both directions**: every function `name` has a matching `operationId`, and every reachable `operationId` is referenced.
- Keep function `name` within `^[A-Za-z0-9_]+$` and give every operation a clear, model-readable `description`.
- Bind functions to runtimes explicitly (`run_for_functions`) so Copilot knows which runtime serves which function.

**Don't:**
- Leave the function `name` and `operationId` out of sync — Copilot can't (or wrongly does) invoke.
- Author against "latest" or an old plugin-manifest version — pin it and bump deliberately (#2).
- Ship operations with vague/absent descriptions — Copilot decides invocation from the description.

## Edge cases / when the rule does NOT apply

For an **MCP** runtime (`RemoteMCPServer`, added in v2.4) the binding is to MCP **tools**, not OpenAPI `operationId`s — the same "verify the mapping + pin the version" discipline applies but to the tool list, and the MCP server itself needs separate admin/tenant consent (see [`./gov-route-agents-and-mcp-tools-through-the-agent-registry.md`](./gov-route-agents-and-mcp-tools-through-the-agent-registry.md)). A **local Office Add-in** plugin (`LocalPlugin`, v2.3 preview) is dev-only, not for production. Plugins are only supported as **actions within declarative agents**, not standalone in Copilot.

## See also

- [`./apiplugin-choose-and-route-auth-never-embed-secrets.md`](./apiplugin-choose-and-route-auth-never-embed-secrets.md) — the auth half of the plugin
- [`./apiplugin-mark-consequential-actions-and-attest-security-info.md`](./apiplugin-mark-consequential-actions-and-attest-security-info.md) — confirmation + behavior attestation
- [`../knowledge/api-plugins-and-auth-2026.md`](../knowledge/api-plugins-and-auth-2026.md) · [`../agents/api-plugin-engineer.md`](../agents/api-plugin-engineer.md)
- [Plugin manifest schema 2.4](https://learn.microsoft.com/microsoft-365/copilot/extensibility/plugin-manifest-2.4) — the `name`↔`operationId` binding rule + MCP runtime

## Provenance

Codifies the `operationId`-contract discipline + house opinion #2 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in the Microsoft Learn plugin-manifest schema pages (v2.1–v2.4): the manifest `name` "must match an `operationId` value in the OpenAPI description" and "`^[A-Za-z0-9_]+$`" rule, and the v2.4 MCP `RemoteMCPServer` + `isNonConsequential` changes, retrieved 2026-05-30. Version is `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
