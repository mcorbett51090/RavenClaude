# Changelog — graphql-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-05

Initial release.

### Added

- **3 agents** — `graphql-schema-architect` (client-driven type modeling, nullability, Relay pagination, mutation/error shape, schema-first vs code-first, monolith vs federation vs stitching, non-breaking evolution), `graphql-server-engineer` (resolvers, N+1/DataLoader batching + per-request caching, selection-set-aware fetching, subscriptions, APQ/response caching), `graphql-security-governance-engineer` (query cost/depth budgets before execution, field-level authorization, persisted/trusted operations, introspection hardening, rate/batch limits, error hygiene).
- **4 skills** — `graphql-schema-design-and-evolution`, `graphql-federation-and-composition`, `resolver-performance-and-n-plus-one`, `graphql-security-and-governance`.
- **Knowledge bank** — `graphql-decision-trees.md` (4 Mermaid trees: schema-first vs code-first, monolith vs federation vs stitching, offset vs Relay-cursor pagination, top-level errors vs errors-as-data) and `graphql-reference-2026.md` (dated reference: server libraries/frameworks, federation/gateway, spec features to check support for, security/governance tooling, observability — each with source placeholder + retrieval date + verify-at-use).
- **5 best-practices** — design the schema for clients not your database, kill the N+1 with batching, make schema changes additive and non-breaking, bound query cost before you accept it, authorize at the field not just the endpoint.
- **2 templates** — graphql-schema-design-doc, graphql-schema-and-perf-review.
- **2 commands** — `/design-schema`, `/review-schema-and-perf`.

### Scope & verify-at-use

- **Engineering judgment, not a security certification or a spec recital.** The agents store no PII; a formal AppSec verdict routes to `security-engineering`.
- The GraphQL library / federation / spec-feature landscape is volatile — every server-library version, federation/gateway detail, and spec feature (`@defer`/`@stream`, subscription transports, APQ) in `graphql-reference-2026.md` carries a retrieval date + `[verify-at-use]`; re-confirm against the library/spec docs before quoting or committing.
- Seams to `api-engineering` (REST/OpenAPI & gateway), `database-engineering` (databases behind resolvers), `backend-engineering` (services behind resolvers), `security-engineering` (AppSec verdict), `auth-identity` (request principal), and `frontend-engineering` (client-side GraphQL).
