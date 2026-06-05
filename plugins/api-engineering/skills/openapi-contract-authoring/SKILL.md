---
name: openapi-contract-authoring
description: "Step-by-step playbook for writing a contract-first OpenAPI 3.1 document — from info block to path items, component reuse, and Spectral pre-flight. Covers resource modeling, status codes, error schema, and pagination shape."
---

# OpenAPI Contract Authoring

## When to Use This Skill

Invoke before writing any server code. The OpenAPI document is the source of truth; code follows the spec, never the reverse.

## 1. Document Skeleton (OpenAPI 3.1)

```yaml
openapi: "3.1.0"
info:
  title: Orders API
  version: "1.0.0"
  description: |
    Manages customer orders. Breaking changes bump the major version.
  contact:
    email: api-team@example.com
servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://api-staging.example.com/v1
    description: Staging
paths: {}
components:
  schemas: {}
  responses: {}
  parameters: {}
  securitySchemes: {}
security:
  - BearerAuth: []
```

## 2. Resource Modeling Checklist

| Decision | Rule |
|---|---|
| URL shape | Plural nouns: `/orders`, `/orders/{orderId}/items` |
| Verb in URL | Never. `POST /orders/{id}/cancel` → `POST /orders/{id}/cancellations` |
| ID type | `string` (UUID) — never expose sequential integers |
| Collections | Always paginated; never return an unbounded array at the root |
| Nested depth | Cap at two levels (`/parent/{id}/child`) — deeper → join via query |

## 3. Path Item Template

```yaml
/orders/{orderId}:
  parameters:
    - $ref: "#/components/parameters/OrderId"
  get:
    operationId: getOrder
    summary: Retrieve an order by ID
    tags: [orders]
    responses:
      "200":
        description: Order found
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Order"
      "404":
        $ref: "#/components/responses/NotFound"
      "401":
        $ref: "#/components/responses/Unauthorized"
```

## 4. Standard Responses (declare once in components)

```yaml
components:
  responses:
    NotFound:
      description: Resource not found
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/Problem"
    Unauthorized:
      description: Missing or invalid credentials
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/Problem"
  schemas:
    Problem:
      type: object
      required: [type, title, status]
      properties:
        type:
          type: string
          format: uri
        title:
          type: string
        status:
          type: integer
        detail:
          type: string
        instance:
          type: string
          format: uri
```

## 5. Pagination Shape

```yaml
schemas:
  OrderPage:
    type: object
    required: [items, cursor]
    properties:
      items:
        type: array
        items:
          $ref: "#/components/schemas/Order"
      cursor:
        type: string
        nullable: true
        description: Opaque next-page token; null when no more pages.
      pageSize:
        type: integer
```

## 6. Pre-Flight Checklist Before Committing

- [ ] Every `operationId` is unique and camelCase
- [ ] All `$ref` targets exist in `components`
- [ ] No inline schema with more than 3 properties — extract to `components/schemas`
- [ ] Every `POST`/`PUT`/`PATCH` has a `requestBody` with `required: true`
- [ ] At least `401`, `404`, and `422`/`400` responses declared on every protected operation
- [ ] `application/problem+json` used for all error responses (not `application/json`)
- [ ] `Spectral` lint passes (`npx @stoplight/spectral-cli lint openapi.yaml`)

## Pitfalls

- Writing the spec after the server ships — the contract is then a documentation artifact, not a design gate
- Using `additionalProperties: true` (the default in OpenAPI 3.0 semantics) on response schemas — strict schemas catch drift early
- Defining the same error shape inline per operation instead of `$ref`-ing `components/responses`
- Forgetting that OpenAPI 3.1 uses `type: [string, "null"]` for nullable (not `nullable: true`) — mixing conventions breaks tooling
- Omitting `servers` — clients and mock generators need the base URL

## See Also

- [`../../agents/api-design-architect.md`](../../agents/api-design-architect.md) — paradigm selection and contract-first design philosophy
- [`../../agents/api-testing-engineer.md`](../../agents/api-testing-engineer.md) — Spectral lint configuration in CI
- [`../../CLAUDE.md`](../../CLAUDE.md) — house opinions on contract-first and error model
