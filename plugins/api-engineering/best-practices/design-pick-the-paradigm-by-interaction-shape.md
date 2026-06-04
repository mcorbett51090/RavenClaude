# Pick the paradigm by interaction shape, not fashion

**Status:** Absolute rule — name the trade; don't default to a paradigm because it's trendy.

**Domain:** API design

**Applies to:** `api-engineering`

---

## Why this exists

REST, GraphQL, gRPC, and event-driven (webhooks/AsyncAPI) each buy something and cost something. Choosing GraphQL because it's modern, or gRPC because it's fast, without matching it to how clients actually interact, ships an API that fights its consumers — a GraphQL API with no query-complexity limit is a DoS surface; a gRPC API for public browser clients needs a transcoding gateway nobody budgeted for; REST over a deeply-nested mobile read over-fetches on every screen.

## How to apply

Traverse the paradigm-selection tree in [`../knowledge/api-design-decision-trees.md`](../knowledge/api-design-decision-trees.md) and state the trade you accepted.

```
Request/response, resource CRUD, external/cacheable      -> REST + OpenAPI 3.1/3.2
Client-shaped reads over a deep typed graph              -> GraphQL (pay: caching, complexity limits, N+1)
Internal low-latency, polyglot, streaming                -> gRPC + Protobuf (pay: browser/debug reach)
"Tell me when X happens" (push)                          -> Webhooks (AsyncAPI)
Decoupled pub/sub over a broker                          -> Event-driven (AsyncAPI)
```

**Do:**
- Write down the trade ("GraphQL — accepting caching loss + mandatory depth limiting for client-shaped reads").
- Allow hybrids: REST for resources + webhooks for events is common and correct.

**Don't:**
- Pick GraphQL/gRPC as a default; pick it as a deliberate trade.
- Ship GraphQL without query depth/complexity limits (OWASP API4).

## Edge cases / when the rule does NOT apply

An existing org standard ("we're a gRPC shop internally") is a legitimate constraint — honor it, but still note where it costs (the one public endpoint that needs transcoding). A single tiny internal endpoint rarely needs a paradigm debate.

## See also

- [`../knowledge/api-design-decision-trees.md`](../knowledge/api-design-decision-trees.md)
- [`../agents/api-design-architect.md`](../agents/api-design-architect.md)
- [AsyncAPI](https://www.asyncapi.com/) · [gRPC](https://grpc.io/) — authoritative

## Provenance

Codifies house opinion #2 (CLAUDE.md §3). Retrieved/verified 2026-06-04 against the OpenAPI/AsyncAPI/gRPC project docs.

---

_Last reviewed: 2026-06-04 by `claude`_
