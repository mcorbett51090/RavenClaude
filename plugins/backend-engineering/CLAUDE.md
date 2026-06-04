# Backend Engineering Plugin — Team Constitution

> Team constitution for the `backend-engineering` Claude Code plugin — **4** specialist agents for the application/service craft behind an API — domain modeling and service boundaries, business logic, caching, background jobs and messaging, the data-access layer, and backend reliability — distinct from the API contract and the database schema. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`backend-architect`](agents/backend-architect.md) | Service/application architecture: domain modeling, service boundaries (monolith vs microservices, where to split), inter-service communication (sync vs async), and the overall backend shape | "monolith or microservices?", "where should we split this service?", "design our backend architecture", "sync call or event?" |
| [`service-implementation-engineer`](agents/service-implementation-engineer.md) | Business-logic implementation: clean service/use-case layering, error handling and result modeling, validation, idempotency keys, and structuring code so logic is testable and the framework stays at the edges | "implement this business logic", "how should I structure this service?", "handle errors properly", "make this idempotent" |
| [`backend-data-access-engineer`](agents/backend-data-access-engineer.md) | The data-access layer: repository/data-mapper pattern, transaction boundaries, ORM use without N+1, the outbox pattern, caching (cache-aside, invalidation, stampede protection), and read/write separation in app code | "our ORM generates N+1 queries", "add caching to this", "where should the transaction boundary be?", "implement the outbox pattern" |
| [`backend-reliability-engineer`](agents/backend-reliability-engineer.md) | Backend resilience and async work: timeouts, retries with exponential backoff + jitter (idempotent only), circuit breakers, bulkheads, graceful degradation, and background-job/worker design (queues, DLQs, idempotent consumers) | "add retries and timeouts", "a slow dependency takes us down", "design our background jobs", "add a circuit breaker" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **A monolith until proven otherwise.** Start with a well-modularized monolith; split into services only when a real scaling, team-autonomy, or deploy-isolation need appears. Premature microservices buy distributed-systems pain for free.
2. **Model the domain, then the code.** Boundaries follow the business, not the database tables. A service/module that owns a coherent capability beats one that wraps a table.
3. **The data-access layer is owned, not sprinkled.** Queries live behind a repository/data layer with explicit transaction boundaries — not raw ORM calls scattered through controllers. This is where N+1 and accidental long transactions breed.
4. **Idempotency is mandatory for anything retried.** Every async worker, webhook handler, and retried call has a dedup key. Retries are guaranteed by the network; non-idempotent retries corrupt.
5. **Cache deliberately; invalidation is the hard part.** Decide what's cacheable, the TTL, the invalidation trigger, and the stampede protection up front. A cache without an invalidation story serves stale data as a feature.
6. **Fail fast and degrade gracefully.** Timeouts on every outbound call, retries with backoff+jitter (idempotent only), circuit breakers, and a defined degraded mode. A backend with no timeouts cascades one slow dependency into total failure.

## 3. Seams (the bridges to neighbouring plugins)

- **The API contract (paradigm, OpenAPI/AsyncAPI, versioning, pagination semantics)** → `api-engineering`; this team implements the service *behind* the contract.
- **The database schema, indexes, query plans, and migrations** → `database-engineering`; we own the data-access *code* and transaction boundaries, they own the schema and tuning (we flag ORM-generated N+1 to them).
- **Where the service runs, builds, and deploys** → `devops-cicd` + the cloud plugin + `cloud-native-kubernetes`.
- **Timeouts/retries/SLOs as an operational concern** → `observability-sre` (we implement the resilience patterns; they set the SLOs they protect).
- **Authentication of the caller and end-user identity** → `auth-identity`; authorization-in-the-service logic is ours, the identity is theirs.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.
