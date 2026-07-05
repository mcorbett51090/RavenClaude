# graphql-engineering

A RavenClaude plugin: a **GraphQL engineering** specialist team for the three engines of a GraphQL surface — schema design & evolution, server & resolvers, and security & governance.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Engineering judgment — not a security certification or a spec recital.** The GraphQL library / federation / spec-feature landscape is volatile: every server-library version, federation/gateway detail, and spec feature (`@defer`/`@stream`, subscription transports, APQ) carries a retrieval date + `[verify-at-use]` and must be confirmed against the library/spec docs before it drives a commitment. A formal AppSec verdict routes to [`security-engineering`](../security-engineering/). The agents store no PII.

## What it's for

Building and operating a GraphQL API well: a schema shaped for clients (not your tables) that you can evolve without breaking anyone, resolvers that batch away the N+1 instead of firing hundreds of downstream calls, and a surface locked down so one arbitrarily-shaped query can't take down the backend or read data it shouldn't.

## Why it's distinct from `api-engineering`

`api-engineering` owns REST/OpenAPI, versioning, and general HTTP-API design. GraphQL inverts several of those intuitions — one endpoint exposes the whole graph, there is no URL versioning, and the N+1 is the default performance failure — so it gets its own team. Reach for `api-engineering` for REST and gateway/WAF concerns; reach here for schema shape, resolver performance, and query-cost/authz governance.

## Agents

| Agent | Use for |
|---|---|
| **graphql-schema-architect** | Type modeling for clients, nullability, Relay pagination, mutation/error shape, schema-first vs code-first, monolith vs federation vs stitching, non-breaking evolution |
| **graphql-server-engineer** | Resolvers, killing N+1 with DataLoader batching + per-request caching, selection-set-aware fetching, subscriptions, APQ/response caching |
| **graphql-security-governance-engineer** | Query cost/depth budgets before execution, field-level authorization, persisted/trusted operations, introspection hardening, rate/batch limits, error hygiene |

## What's inside

- **4 skills** — graphql-schema-design-and-evolution, graphql-federation-and-composition, resolver-performance-and-n-plus-one, graphql-security-and-governance.
- **Knowledge bank** — [`graphql-decision-trees.md`](knowledge/graphql-decision-trees.md) (4 Mermaid trees: schema-first vs code-first, monolith vs federation vs stitching, offset vs Relay-cursor pagination, top-level errors vs errors-as-data) + [`graphql-reference-2026.md`](knowledge/graphql-reference-2026.md) (dated server-library / federation / spec-feature / security-tooling landscape, verify-at-use).
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **2 templates** — GraphQL schema design doc, GraphQL schema & perf review.
- **2 commands** — `/design-schema`, `/review-schema-and-perf`.

## Seams

REST/OpenAPI & gateway → [`api-engineering`](../api-engineering/) · databases behind resolvers → [`database-engineering`](../database-engineering/) · services behind resolvers → [`backend-engineering`](../backend-engineering/) · AppSec verdict → [`security-engineering`](../security-engineering/) · end-user identity → [`auth-identity`](../auth-identity/) · client-side GraphQL → [`frontend-engineering`](../frontend-engineering/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install graphql-engineering@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for the scope, routing rules, house opinions, and the output contract.
