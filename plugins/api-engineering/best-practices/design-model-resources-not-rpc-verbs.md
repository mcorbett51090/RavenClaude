# Model resources and state, not RPC verbs in URLs

**Status:** Absolute rule (for REST) — the HTTP method is the verb; the path is a noun.

**Domain:** API design

**Applies to:** `api-engineering`

---

## Why this exists

`POST /users/{id}/deactivate`, `GET /getOrders`, `POST /createInvoice` are RPC tunneled through HTTP. They throw away HTTP's uniform interface (caching, idempotency semantics, conditional requests, intermediary understanding) and produce an unbounded, inconsistent verb vocabulary every consumer must learn endpoint-by-endpoint. Resources + methods give you a small, predictable surface: the same five methods mean the same thing everywhere.

## How to apply

Model nouns (plural collections), express the action with the HTTP method, and model state transitions as resources or fields.

```
Bad:  POST /users/{id}/deactivate
Good: PATCH /users/{id}   { "status": "inactive" }      # state is a field
 or:  POST  /users/{id}/deactivations                   # the transition is a resource

Bad:  GET /getUserOrders?userId=42
Good: GET /users/42/orders

Bad:  POST /searchProducts   { ... }
Good: GET /products?category=...&q=...                  # a search is a filtered collection read
```

**Do:**
- Plural collection nouns; sub-resources for relationships; query params for filter/sort/paginate.
- Map methods to semantics: `GET` safe, `PUT`/`DELETE` idempotent, `POST` creates/acts.

**Don't:**
- Put verbs in paths; return collections from `POST`; use `GET` for anything that mutates.

## Edge cases / when the rule does NOT apply

Some genuinely-RPC actions don't model cleanly as resources (`POST /rpc/recalculate`, a `POST /.../actions/cancel`); a small, documented set of action sub-resources is acceptable when a state field would be contrived. GraphQL and gRPC are *intentionally* RPC-shaped — this rule is about REST. A complex search with a large body legitimately uses `POST` (a "query" resource).

## See also

- [`./design-contract-first-not-code-first.md`](./design-contract-first-not-code-first.md)
- [`./build-use-http-status-codes-and-methods-correctly.md`](./build-use-http-status-codes-and-methods-correctly.md)
- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html) — authoritative

## Provenance

Codifies house opinion #3 (CLAUDE.md §3), grounded in RFC 9110 method semantics. Retrieved/verified 2026-06-04.

---

_Last reviewed: 2026-06-04 by `claude`_
