# Backend Engineering

The **backend-engineering** plugin — the application/service craft behind an API — domain modeling and service boundaries, business logic, caching, background jobs and messaging, the data-access layer, and backend reliability — distinct from the API contract and the database schema.

## Agents

- **`backend-architect`** — Service/application architecture: domain modeling, service boundaries (monolith vs microservices, where to split), inter-service communication (sync vs async), and the overall backend shape
- **`service-implementation-engineer`** — Business-logic implementation: clean service/use-case layering, error handling and result modeling, validation, idempotency keys, and structuring code so logic is testable and the framework stays at the edges
- **`backend-data-access-engineer`** — The data-access layer: repository/data-mapper pattern, transaction boundaries, ORM use without N+1, the outbox pattern, caching (cache-aside, invalidation, stampede protection), and read/write separation in app code
- **`backend-reliability-engineer`** — Backend resilience and async work: timeouts, retries with exponential backoff + jitter (idempotent only), circuit breakers, bulkheads, graceful degradation, and background-job/worker design (queues, DLQs, idempotent consumers)

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install backend-engineering@ravenclaude
```

## Seams

- **The API contract (paradigm, OpenAPI/AsyncAPI, versioning, pagination semantics)** → `api-engineering`; this team implements the service *behind* the contract.
- **The database schema, indexes, query plans, and migrations** → `database-engineering`; we own the data-access *code* and transaction boundaries, they own the schema and tuning (we flag ORM-generated N+1 to them).
- **Where the service runs, builds, and deploys** → `devops-cicd` + the cloud plugin + `cloud-native-kubernetes`.
- **Timeouts/retries/SLOs as an operational concern** → `observability-sre` (we implement the resilience patterns; they set the SLOs they protect).
- **Authentication of the caller and end-user identity** → `auth-identity`; authorization-in-the-service logic is ours, the identity is theirs.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.
