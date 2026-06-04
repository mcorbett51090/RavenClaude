# Changelog — api-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-06-04

Initial release. An API engineering specialist team for the full lifecycle of an API you **produce** — design, build, secure, test, operate — built from web-grounded research (RFC 9457, OWASP API Security Top 10 2023, OpenAPI 3.1/3.2, AsyncAPI 3.0, Arazzo, the IETF `RateLimit`/`Idempotency-Key` drafts).

- **5 agents:** `api-design-architect`, `api-implementation-engineer`, `api-security-engineer`, `api-testing-engineer`, `api-platform-engineer` — one per lifecycle stage (design → build → secure → test → operate).
- **3-doc knowledge bank** (retrieval-dated 2026-06-04) with 10 Mermaid decision trees (paradigm selection, versioning, pagination; OWASP API control map, OAuth2 grant, object-vs-function authZ, rate-limit/quota; test-type selection, mock-vs-stub-vs-virtualize, gateway build-vs-buy) + a dated 2026 spec capability map.
- **22 best-practices** across design / build / secure / test / operate, one named rule per file.
- **6 templates:** contract-first OpenAPI skeleton, AsyncAPI skeleton, Problem Details catalog, Spectral style-guide ruleset, API design-review checklist, deprecation/sunset plan.
- **6 commands:** `design-api`, `review-api-design`, `harden-api`, `scaffold-error-model`, `lint-api-spec`, `generate-contract-tests`.
- **1 advisory hook** (`check-api-anti-patterns.sh`, `APIENG_STRICT=1` to block): API key in query, HTTP Basic scheme, hardcoded token/secret, wildcard CORS + credentials, stale OpenAPI version.
- **12 house opinions.** Ships **no** security/architect clone — every authorization/exposure/scope verdict escalates to `ravenclaude-core/security-reviewer`.

### Seams shipped
Clearly bounded against `claude-app-engineering` (Claude API / MCP), `microsoft-graph` (consuming Graph), `azure-cloud/integration-engineer` (APIM host infra), `auth-identity` (end-user login UX), and `data-platform/connector-developer` (ELT connectors). The producer/consumer line and the design/infra line are stated in §0 of the team constitution.

### Deferred to a later version
- A `skills/` directory and a `scenarios/` bank when the first engagement scenario surfaces.
- Deeper GraphQL (federation, persisted queries) and gRPC (streaming, deadlines) reference docs if demand surfaces.
- First-class Postman MCP workflow recipes in `api-testing-engineer` once the collection/spec round-trip is exercised in a real engagement.
