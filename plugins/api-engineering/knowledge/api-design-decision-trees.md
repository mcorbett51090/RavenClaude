# API Engineering — design decision trees & spec capability map

**Last reviewed:** 2026-06-04 · **Confidence:** medium-high (first-party specs + IETF datatracker, web-verified this date). Volatile facts (spec versions/features, IETF draft status) carry inline markers + per-tree `Last verified` dates; re-verify on the Researcher sweep before quoting.

> Canonical decision trees for the `api-design-architect` (and the pagination tree for `api-implementation-engineer`). Traverse the relevant tree top-to-bottom against the observable situation **before** choosing a method (per the pre-action-traversal prior in [`../CLAUDE.md`](../CLAUDE.md) §5). Default to the smaller-blast-radius leaf; escalate only when it demonstrably fails.

---

## Decision Tree: API paradigm selection (REST vs GraphQL vs gRPC vs webhooks/async)

**When this applies:** You are choosing the wire paradigm for a new API or service interface, before writing the contract.

**Last verified:** 2026-06-04 against the OpenAPI/AsyncAPI/gRPC project docs. `[verify-at-build]` — tooling maturity shifts.

```mermaid
flowchart TD
    START[New API surface to expose] --> Q1{Is the interaction request/response, or event/notification?}
    Q1 -->|Event - tell me when X happens| Q2{Do you push to the consumer or subscribe to a broker?}
    Q2 -->|Push HTTP callback to a registered URL| WEBHOOK[Webhooks - document with AsyncAPI 3.0]
    Q2 -->|Pub/sub over a broker - Kafka/AMQP/MQTT/WebSocket| ASYNC[Event-driven - describe with AsyncAPI 3.0]
    Q1 -->|Request/response| Q3{Primary consumer and network?}
    Q3 -->|Internal service-to-service, low latency, polyglot| Q4{Need browser/public reach or human-readable debugging?}
    Q4 -->|NO - internal mesh| GRPC[gRPC + Protobuf - typed, streaming, fast]
    Q4 -->|YES| REST1[REST/JSON - or gRPC + a REST/JSON transcoding gateway]
    Q3 -->|External/partner/public or mobile/web client| Q5{Do clients need to shape/aggregate reads to avoid over/under-fetching a nested graph?}
    Q5 -->|YES - varied client read shapes, deep nesting| GRAPHQL[GraphQL - accept the caching/complexity-limit cost]
    Q5 -->|NO - resource CRUD, cacheable, broad tooling| REST2[REST over HTTP + OpenAPI 3.1/3.2]
```

**Rationale per leaf:**
- _REST + OpenAPI_ — the default for external resource CRUD: cacheable (HTTP caching), broadest tooling, easiest to debug. Pay in over/under-fetching on deeply nested reads.
- _GraphQL_ — clients shape their own reads; great for varied mobile/web read shapes over a typed graph. Pay in HTTP-caching loss, mandatory query-complexity/depth limiting (a DoS surface — OWASP API4), and N+1 discipline.
- _gRPC + Protobuf_ — internal, low-latency, strongly-typed, streaming; weaker browser/public/debugging story (needs grpc-web or transcoding).
- _Webhooks_ — server pushes to a consumer-registered URL; document the event contract with AsyncAPI; the consumer must validate the sender and the handshake.
- _Event-driven over a broker_ — true pub/sub decoupling; describe channels/operations/messages with AsyncAPI 3.0.

**Tradeoffs summary:**

| Paradigm | Best for | Caching | Pay in |
|---|---|---|---|
| REST/OpenAPI | external resource CRUD | HTTP-native | over/under-fetch on nested reads |
| GraphQL | client-shaped reads, deep graphs | hard (POST) | complexity-limiting, N+1, no HTTP cache |
| gRPC | internal low-latency, streaming | n/a | browser/public reach, debuggability |
| Webhooks (AsyncAPI) | "notify me" push | n/a | sender validation, retries, ordering |
| Event-driven (AsyncAPI) | decoupled pub/sub | n/a | broker ops, delivery semantics |

---

## Decision Tree: API versioning — is it breaking, and how do you carry the version?

**When this applies:** You are changing an existing API and must decide whether to bump the version and where the version lives.

**Last verified:** 2026-06-04. The "additive is not breaking" rule is paradigm-independent.

```mermaid
flowchart TD
    START[Changing an existing API] --> Q1{Does the change remove/rename a field, tighten a type, change semantics, or make an optional input required?}
    Q1 -->|NO - adding an optional field, a new endpoint, a new enum value clients ignore| ADD[Additive - NO version bump. Ship it; document it.]
    Q1 -->|YES - it can break a conforming client| Q2{Can you support old + new behavior simultaneously for a transition window?}
    Q2 -->|NO| BREAK[New major version; deprecate the old with Deprecation+Sunset]
    Q2 -->|YES| Q3{Is the consumer base public/partner, or internal/coordinated?}
    Q3 -->|Public/partner - cannot coordinate a flag day| URIV[Version in the URI path - /v2 - most visible, cache-friendly]
    Q3 -->|Internal/coordinated| HDRV[Version via media type or a version header - cleaner URLs, needs discipline]
```

**Rationale per leaf:**
- _Additive → no bump_ — new optional fields, new endpoints, new enum members a tolerant client ignores. Don't version for these; versioning churn is its own cost. (Requires consumers follow the tolerant-reader / must-ignore-unknown-fields rule.)
- _URI versioning (`/v2`)_ — most visible and unambiguous, trivially cacheable and routable; the pragmatic default for public/partner APIs. Pay in URL churn and parallel maintenance.
- _Header/media-type versioning_ — keeps URLs stable and is "purer," but is easy to get wrong (caching, discoverability) and needs disciplined consumers; reserve for coordinated/internal consumers.
- _New major + deprecate_ — when old and new can't coexist, run the deprecation clock (see the operate-layer tree and `operate-deprecate-with-sunset-headers.md`).

---

## Decision Tree: pagination strategy (offset vs cursor/keyset)

**When this applies:** You are returning a collection and choosing how clients page through it. (Owned by `api-implementation-engineer`; lives here with the design trees.)

**Last verified:** 2026-06-04.

```mermaid
flowchart TD
    START[Returning a collection] --> Q1{Can the result set be large or grow, and is it ordered by a stable key?}
    Q1 -->|Large/growing, stable sort key available| CURSOR[Cursor/keyset pagination - opaque next cursor over the sort key]
    Q1 -->|Small, bounded, rarely changing| Q2{Do clients need random access to an arbitrary page number?}
    Q2 -->|YES - jump to page N, total count needed| OFFSET[Offset/limit - accept drift and deep-page cost; bound the max offset]
    Q2 -->|NO| CURSOR
```

**Rationale per leaf:**
- _Cursor/keyset (default)_ — stable under concurrent inserts/deletes and O(1)-ish on deep pages; return an opaque `next` cursor encoding the keyset position. The right default for anything large or live.
- _Offset/limit_ — only when clients genuinely need page-number random access or a total count on a small, stable set; it **drifts** (rows shift between pages as data changes) and **degrades** on deep pages (`OFFSET 100000` scans and discards). Always bound the max page size and the max offset (OWASP API4).

| Method | Stable under writes | Deep-page cost | Random page access | Use when |
|---|---|---|---|---|
| Cursor/keyset | yes | low | no | large/live collections (default) |
| Offset/limit | no (drifts) | high | yes | small stable sets needing page N |

---

## 2026 spec & standards capability map

**Last verified:** 2026-06-04 (web-verified — OpenAPI Initiative, AsyncAPI, IETF datatracker). Every row is volatile; re-verify before quoting a version/feature/status. `[verify-at-build]`

| Standard | Current | Status / notes |
|---|---|---|
| **OpenAPI** | **3.1.x** and **3.2.0** | 3.1 aligns with JSON Schema (2020-12); **3.2.0 released 2025-09** — hierarchical tags, first-class streaming (SSE/JSON-Lines/multipart), additional/custom HTTP methods, OAuth2 Device flow in-spec. Zero-breaking 3.1→3.2. Default to 3.1+; reach for 3.2 features deliberately. `[verify-at-build]` |
| **AsyncAPI** | **3.0.0** (2023-11) | Splits operations out of channels; the standard for event-driven/message + webhook contracts. `[verify-at-build]` |
| **Arazzo** | **1.0.1** (2025-01) | OpenAPI Initiative workflow-description spec (sequences of API calls); **v1.1 in progress adds AsyncAPI support**. Useful for AI-assisted / multi-step API consumption. `[verify-at-build]` |
| **JSON Schema** | **2020-12** | The schema dialect OpenAPI 3.1 adopts. |
| **RFC 9457 — Problem Details** | RFC (2023-07) | **Obsoletes RFC 7807**; same `application/problem+json` wire format; adds registry + multi-problem guidance. The error model. |
| **RFC 9110 — HTTP Semantics** | RFC (2022) | Authoritative status-code & method semantics. |
| **RFC 8594 — `Sunset` header** | RFC | Signals a resource's retirement time; pair with `Deprecation`. `[verify-at-build]` |
| **`Deprecation` header** | IETF track | Signals a resource is deprecated; verify RFC-vs-draft status before quoting. `[verify-at-build]` |
| **`RateLimit` / `RateLimit-Policy` headers** | **IETF draft** (draft-ietf-httpapi-ratelimit-headers, ~v11, 2026) | **Not yet an RFC** — implement to the current draft and say so. `[verify-at-build]` |
| **`Idempotency-Key` header** | **IETF draft** (draft-ietf-httpapi-idempotency-key-header, ~v07, 2025-10) | **Not yet an RFC** — the convention many APIs already ship; follow the draft. `[verify-at-build]` |
| **OWASP API Security Top 10** | **2023 edition** | BOLA #1; BOPLA, sensitive-business-flows, unsafe-consumption are 2023 framing. Distinct from the OWASP *Web* Top 10. `[verify-at-build]` |

---

## Decision Tree: Webhook or event broker — which push pattern?

**When this applies:** You need to notify external consumers when a resource changes and must decide between HTTP webhooks (push to a caller-registered URL) and a broker-based event stream (Kafka, AMQP, MQTT).

**Last verified:** 2026-06-05 against AsyncAPI 3.0 tooling and standard pub/sub patterns.

```mermaid
flowchart TD
    START[Push notifications to consumers] --> Q1{Is the consumer external - a third party or partner?}
    Q1 -->|Yes - external consumer registers an endpoint| WEBHOOK[HTTP Webhooks - HMAC-signed POST to registered URL]
    Q1 -->|No - internal service-to-service| Q2{More than one consumer for the same event?}
    Q2 -->|No - single consumer| QUEUE[Point-to-point queue - command to that consumer]
    Q2 -->|Yes - multiple or future consumers| Q3{Need replay / consumer-controlled offset?}
    Q3 -->|Yes - consumers need to replay from a position| KAFKA[Event broker - Kafka or similar - consumer manages offset]
    Q3 -->|No - fire and forget with delivery guarantee| AMQP[Message broker - RabbitMQ/AMQP - broker manages delivery]
    WEBHOOK --> SIGN[Sign payload - HMAC - plus retry with backoff]
    KAFKA --> ASYNCAPI[Document with AsyncAPI 3.0]
    AMQP --> ASYNCAPI
    QUEUE --> ASYNCAPI
```

**Rationale per leaf:**
- *Webhooks* — the right external push pattern; consumer controls the endpoint, you control the retry and signing. Document with AsyncAPI.
- *Point-to-point queue* — a command to one known consumer; use when the downstream is internal and unique.
- *Kafka / event log* — consumers replay from a committed offset; correct when consumers are varied, independent, or need replay.
- *AMQP broker* — broker-acknowledged delivery without consumer-controlled replay; simpler ops than Kafka for moderate scale.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| HTTP Webhook | Low | One endpoint failure | None | External partner consumption |
| Point-to-point queue | Low | One consumer | None | Single internal consumer |
| Kafka / log | High | Consumer-controlled | Broker team | Replay needed, multiple consumers |
| AMQP broker | Medium | Broker-managed | Broker team | Internal pub/sub, no replay needed |

## Decision Tree: GraphQL query complexity — rate limit or reject?

**When this applies:** You are designing a GraphQL API and must decide how to prevent resource exhaustion from deeply nested or large queries. OWASP API4 applies.

**Last verified:** 2026-06-05 against GraphQL specification and standard depth/complexity-limiting libraries.

```mermaid
flowchart TD
    START[GraphQL API with public or partner access] --> Q1{Can the client construct arbitrarily deep nested queries?}
    Q1 -->|No - schema is shallow, max 2-3 levels| Q2{Can the client request many fields in one query?}
    Q2 -->|No - few selectable fields| RATELIMIT[Token-bucket rate limit per caller is sufficient]
    Q2 -->|Yes - many fields| COMPLEXITY[Add query complexity analysis - reject above a threshold]
    Q1 -->|Yes - deep nesting possible| DEPTH[Add depth limiting - reject queries deeper than N levels]
    DEPTH --> COMPLEXITY
    COMPLEXITY --> Q3{Do you need to allow some high-complexity queries for legitimate use?}
    Q3 -->|Yes - power users| QUOTAPOOL[Separate complexity quota pool per caller tier]
    Q3 -->|No - one limit fits all| REJECT[Hard reject - return 400 with complexity and limit in error]
    RATELIMIT --> PERSIST[Persist complexity budget across requests within a time window]
```

**Rationale per leaf:**
- *Rate limit only* — shallow schemas with few fields are low-risk; a token bucket is the right lever.
- *Depth limiting* — the simplest protection against deeply nested N+1 attacks; implement as middleware.
- *Complexity analysis* — each field/resolver is assigned a cost; a query's total cost is compared to a per-request budget. Most flexible.
- *Quota pool per tier* — legitimate power-user clients (reporting tools, sync agents) need a higher complexity budget; tiering by caller scope is the right mechanism.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Rate limit only | Low | Blocks burst | None | Shallow schema, few fields |
| Depth limit | Low-medium | Rejects deep queries | None | Deep nesting possible |
| Complexity analysis | Medium | Blocks expensive queries | Schema design | Varied field costs, power users |
| Tiered quota | High | Per-tier enforcement | Product agreement | Mixed access tiers |

## Decision Tree: API key — rotate, revoke, or short-lived token?

**When this applies:** A consumer needs to authenticate with the API and you must decide what credential type to issue. The choice affects rotation burden, revocation latency, and blast radius.

**Last verified:** 2026-06-05 against OAuth 2.0 RFC 6749 and API key management practices.

```mermaid
flowchart TD
    START[Consumer needs API credentials] --> Q1{Is the consumer a human end-user logging into an app?}
    Q1 -->|Yes| OAUTH[OAuth2 authorization code + PKCE - short-lived access token + refresh]
    Q1 -->|No - M2M service or automation| Q2{Does the consumer have a secure secrets store?}
    Q2 -->|Yes - Vault, AWS Secrets Manager, managed identity| Q3{Does your platform support client credentials flow?}
    Q3 -->|Yes| CLIENTCRED[OAuth2 client credentials - short-lived access token, rotate client secret periodically]
    Q3 -->|No| APIKEY[Long-lived API key - scoped, stored in secrets manager, rotatable]
    Q2 -->|No - third-party integration, no secrets infra| APIKEY
    APIKEY --> SCOPE[Issue least-privilege scope per key - never a wildcard]
    CLIENTCRED --> SCOPE
    OAUTH --> SCOPE
    SCOPE --> AUDIT[Log every issuance and revocation in the audit trail]
```

**Rationale per leaf:**
- *OAuth2 authorization code + PKCE* — the correct pattern for human interactive auth; short-lived tokens limit blast radius.
- *OAuth2 client credentials* — M2M short-lived tokens; the client secret is rotated, not the access token.
- *API key* — valid for M2M integrations without OAuth2 infra, but requires a rotation policy and a revocation mechanism.
- *Least-privilege scope on every leaf* — regardless of credential type, the scope is the blast-radius control.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| OAuth2 code + PKCE | High setup | Minimal - short TTL | Auth team | Human user sessions |
| Client credentials | Medium | Limited - short TTL | Auth team | M2M with OAuth2 infra |
| API key | Low | Key lifetime (days-months) | None | M2M, no OAuth2 infra |

## See also

- [`api-security-decision-trees.md`](./api-security-decision-trees.md) — OWASP control map, OAuth2 grant selection, object-vs-function authZ.
- [`api-testing-governance-decision-trees.md`](./api-testing-governance-decision-trees.md) — test-type selection, gateway build-vs-buy.
- [`../best-practices/`](../best-practices/) — the named rules these trees point to.

## Provenance

Synthesized 2026-06-04 from the OpenAPI Initiative (spec.openapis.org), AsyncAPI (asyncapi.com), the IETF HTTPAPI working group datatracker, and the OWASP API Security project. Spec versions and IETF draft statuses are version-sensitive — `[verify-at-build]`.

---

_Last reviewed: 2026-06-05 by `claude`_
