# Template — API plugin (plugin manifest + OpenAPI pair)

Copy + fill. Source of truth: [`../knowledge/api-plugins-and-auth-2026.md`](../knowledge/api-plugins-and-auth-2026.md). Verify `operationId` mapping both ways; no secrets in the files.

## 1. Plugin manifest (`ai-plugin.json`)

```jsonc
{
  "schema_version": "v2.3", // pin it [verify-at-build]
  "name_for_human": "<plugin name>",
  "description_for_human": "<what it does>",
  "namespace": "<namespace>",
  "functions": [
    {
      "name": "get<Thing>",
      // MODEL-READABLE — Copilot decides whether/how to call from this.
      "description": "Returns <thing> for <criteria>. Use when the user asks <...>.",
      "capabilities": {
        "response_semantics": {
          "data_path": "$.items",
          "properties": { "title": "$.name", "url": "$.link" },
          "static_template": { "file": "adaptive-card-get-thing.json" } // citation rendering
        }
      }
    }
  ],
  "runtimes": [
    {
      "type": "OpenApi",
      "auth": { "type": "OAuthPluginVault", "reference_id": "<connection-registration-id>" }, // or ApiKeyPluginVault / None
      "spec": { "url": "openapi.yaml" },
      // MAPS to OpenAPI operationId — verify both directions.
      "run_for_functions": ["get<Thing>"]
    }
  ]
}
```

## 2. OpenAPI spec (`openapi.yaml`) — Copilot-constrained subset

```yaml
openapi: 3.0.3
info: { title: <API>, version: 1.0.0 }
servers: [{ url: https://api.example.com }]
paths:
  /things:
    get:
      operationId: get<Thing> # MUST match run_for_functions above
      summary: Get <thing>
      description: Returns <thing> for the given criteria. # model-readable
      parameters:
        - { name: criteria, in: query, required: true, schema: { type: string }, description: <...> }
      responses:
        "200":
          description: <thing> list
          content:
            application/json:
              schema:
                type: object
                properties:
                  items:
                    type: array
                    items: { type: object, properties: { name: { type: string }, link: { type: string } } }
```

## Pre-ship checklist
- [ ] All four files present (app manifest + plugin manifest + OpenAPI + adaptive cards) and source-controlled.
- [ ] **`operationId` mapping verified both ways** (`run_for_functions` ↔ `operationId`).
- [ ] Operation + parameter **descriptions are model-readable**.
- [ ] OpenAPI within the Copilot-supported subset; responses within **~66%** of the 25-item/~4,096-token budget.
- [ ] Auth = Entra OAuth2 / API-key via a connection; **no secrets in the files**. App reg → `azure-cloud`; verdict → `security-reviewer`.
- [ ] GCC-High caveat surfaced if relevant.

**Licensing impact:** <Copilot seats; downstream API cost/quota; or "none">
