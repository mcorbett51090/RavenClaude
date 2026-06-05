# Conform OpenAPI specs to Copilot's constraints — not every valid OpenAPI is a valid Copilot API plugin

**Status:** Absolute rule
**Domain:** API plugins
**Applies to:** `microsoft-365-copilot`

---

## Why this exists

Microsoft 365 Copilot uses a subset of the OpenAPI 3.0 specification for API plugins. Schemas, patterns, and features that are valid OpenAPI 3.0 are rejected by Copilot's plugin validator or cause silent misbehavior at runtime: unsupported response content types, missing `operationId`s, cyclic schema references, array-type request bodies without item schemas, and descriptions over the character limit all produce validation errors or degraded Copilot responses. An engineer who takes an existing production OpenAPI spec and points Copilot at it will encounter these constraints at sideload time — the failure messages are cryptic without a pre-check.

## How to apply

Copilot API plugin OpenAPI constraints (key subset; `[verify-at-build]` for the full list):

| Constraint | Valid OpenAPI? | Copilot behavior |
|---|---|---|
| `operationId` missing | Yes | Plugin validator rejects the spec |
| `description` missing on an operation | Yes | Copilot may not invoke the operation |
| Response content type not `application/json` | Yes | Copilot ignores non-JSON responses |
| Array request body without `items` schema | Yes | Validation error |
| Cyclic `$ref` in schema | Yes | Plugin validator rejects |
| `oneOf`/`anyOf`/`allOf` in request schema | Yes | Partially supported `[verify-at-build]` |
| `operationId` length > 64 characters | Yes | Validator rejects |
| Descriptions > 300 characters | Yes | Truncated; may mislead Copilot |

Pre-check script:
```bash
# Install the Teams App Validator or the Agents Toolkit CLI
npm install -g @microsoft/kiota
kiota validate --openapi ./my-api.yaml --manifest ./plugin-manifest.json
```

**Do:**
- Add a meaningful `description` (max ~300 chars) to every operation — Copilot uses the description to decide whether to invoke the operation.
- Keep `operationId`s to ≤ 64 characters, unique, and action-oriented (`GetOrderStatus`, not `Get`).
- Remove or inline cyclic `$ref`s before submitting to the validator.
- Limit response properties to the fields Copilot needs — large response payloads consume the agent's 45-second processing budget.

**Don't:**
- Point Copilot directly at a production API spec designed for developers — strip internal operations not intended for Copilot and reduce response schemas to what the agent actually uses.
- Use polymorphic response schemas (`oneOf`/`anyOf`) without testing end-to-end — Copilot's support varies `[verify-at-build]`.
- Assume that passing schema validation means the agent will correctly invoke the operation — behavioral testing with the regression set is required.

## Edge cases / when the rule does NOT apply

Federated (MCP) connectors use a different specification surface than API plugins — OpenAPI constraints for API plugins do not apply to MCP tool definitions. Verify the correct constraint set for the surface you are building.

## See also

- [`../agents/api-plugin-engineer.md`](../agents/api-plugin-engineer.md) — owns API plugin design and OpenAPI conformance
- [`./apiplugin-pin-plugin-manifest-and-map-operationid-both-ways.md`](./apiplugin-pin-plugin-manifest-and-map-operationid-both-ways.md) — the binding rule that depends on `operationId` being correct

## Provenance

Codifies CLAUDE.md §8 knowledge bank `api-plugins-and-auth-2026.md` OpenAPI-for-Copilot constraints section; Microsoft Learn Copilot API plugin OpenAPI constraints documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
