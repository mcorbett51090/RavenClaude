# api-engineering best-practice docs

Named, citable rules for engineering an API you produce — each file is one rule, grounded in this plugin's own [`knowledge/`](../knowledge/) decision trees and enforced by its [`agents/`](../agents/). Read and apply a doc as a whole.

For the cross-tool rule format and the marketplace-wide index, see [`docs/best-practices/_TEMPLATE.md`](../../../docs/best-practices/_TEMPLATE.md) and [`docs/best-practices/README.md`](../../../docs/best-practices/README.md). For the plugin's house opinions, see [`../CLAUDE.md`](../CLAUDE.md) §3–§4.

---

## Index

_22 rules across the lifecycle (design → build → secure → test → operate). Each file is one named, citable rule; read and apply it whole._

### Design

| Doc | Status | Use when |
|---|---|---|
| [`design-contract-first-not-code-first.md`](./design-contract-first-not-code-first.md) | Absolute rule | The spec is the source of truth — write and review it before the server. |
| [`design-pick-the-paradigm-by-interaction-shape.md`](./design-pick-the-paradigm-by-interaction-shape.md) | Absolute rule | REST / GraphQL / gRPC / async is a trade you name, not a fashion you follow. |
| [`design-model-resources-not-rpc-verbs.md`](./design-model-resources-not-rpc-verbs.md) | Absolute rule | The HTTP method is the verb; the path is a noun (REST). |
| [`design-version-only-for-breaking-changes.md`](./design-version-only-for-breaking-changes.md) | Absolute rule | Additive changes don't bump the version; breaking ones must, with a sunset plan. |
| [`design-lint-the-spec-as-governance.md`](./design-lint-the-spec-as-governance.md) | Pattern | A Spectral ruleset in CI is the style guide with teeth. |

### Build

| Doc | Status | Use when |
|---|---|---|
| [`build-one-error-model-rfc9457-problem-details.md`](./build-one-error-model-rfc9457-problem-details.md) | Absolute rule | One error model — `application/problem+json` (RFC 9457), not a bespoke shape per endpoint. |
| [`build-cursor-pagination-over-offset.md`](./build-cursor-pagination-over-offset.md) | Pattern | Cursor/keyset pagination by default; offset drifts and degrades on deep pages. |
| [`build-idempotency-keys-for-unsafe-retries.md`](./build-idempotency-keys-for-unsafe-retries.md) | Absolute rule | A money/order POST needs an `Idempotency-Key` so a retry doesn't act twice. |
| [`build-optimistic-concurrency-with-etags.md`](./build-optimistic-concurrency-with-etags.md) | Pattern | `ETag` + `If-Match` prevents the lost-update race; last-write-wins is data loss. |
| [`build-use-http-status-codes-and-methods-correctly.md`](./build-use-http-status-codes-and-methods-correctly.md) | Absolute rule | The status line is the contract — a 200 with an error inside lies to clients. |
| [`build-long-running-ops-with-202-and-polling.md`](./build-long-running-ops-with-202-and-polling.md) | Pattern | Accept long jobs with `202` + an operation resource to poll, not a held-open request. |

### Secure (every verdict escalates to `ravenclaude-core/security-reviewer`)

| Doc | Status | Use when |
|---|---|---|
| [`secure-authorize-every-object-bola.md`](./secure-authorize-every-object-bola.md) | Absolute rule | OWASP API1 — verify object ownership server-side on every request; the ID is attacker input. |
| [`secure-authorize-every-function-bfla.md`](./secure-authorize-every-function-bfla.md) | Absolute rule | OWASP API5 — gate privileged functions by role/scope; hiding a button is not authorization. |
| [`secure-validate-tokens-and-scopes-server-side.md`](./secure-validate-tokens-and-scopes-server-side.md) | Absolute rule | OWASP API2 — verify the JWT (signature/iss/aud/exp; reject `alg:none`) before trusting any claim. |
| [`secure-limit-resource-consumption.md`](./secure-limit-resource-consumption.md) | Absolute rule | OWASP API4 — bound page size, payload, query depth, rate, and quota; every unbounded input is a DoS. |
| [`secure-never-trust-upstream-apis.md`](./secure-never-trust-upstream-apis.md) | Absolute rule | OWASP API10 — validate, bound, and time out responses from APIs you call. |

### Test & govern

| Doc | Status | Use when |
|---|---|---|
| [`test-consumer-driven-contract-tests.md`](./test-consumer-driven-contract-tests.md) | Pattern | The consumer's expectations gate the provider's CI — proves you didn't break an integrator. |
| [`test-mock-from-the-contract.md`](./test-mock-from-the-contract.md) | Pattern | Generate the mock from the spec (Prism/Postman) so it can't drift; a hand stub is a lie. |
| [`test-load-test-to-an-slo.md`](./test-load-test-to-an-slo.md) | Pattern | Load-test (k6) against a stated p95/rps objective, not a vanity throughput number. |

### Operate

| Doc | Status | Use when |
|---|---|---|
| [`operate-deprecate-with-sunset-headers.md`](./operate-deprecate-with-sunset-headers.md) | Absolute rule | Retire a version with `Deprecation`/`Sunset` headers, a dated timeline, and drain monitoring. |
| [`operate-rate-limit-and-advertise-it.md`](./operate-rate-limit-and-advertise-it.md) | Pattern | Enforce a rate limit and advertise it with the `RateLimit` headers so clients self-throttle. |
| [`operate-ship-a-developer-portal-and-sdks.md`](./operate-ship-a-developer-portal-and-sdks.md) | Pattern | Generate docs + SDKs from the spec so they can't drift from the contract. |

---

## See also

- [`../knowledge/`](../knowledge/) — the decision trees these rules point to (paradigm, versioning, pagination, OWASP control map, OAuth2 grant, test-type, gateway).
- [`../CLAUDE.md`](../CLAUDE.md) — the team constitution (house opinions §3, anti-patterns §4).
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — the marketplace-wide best-practices index.
