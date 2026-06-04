# api-engineering

A Claude Code plugin: a specialist **API engineering team** for the full lifecycle of an API **you produce** — design the contract, build the endpoints, secure the surface, test & govern it, and operate it.

## What's inside

- **5 agents** — `api-design-architect` (paradigm choice, contract-first OpenAPI/AsyncAPI, resource modeling, versioning & deprecation, Spectral governance), `api-implementation-engineer` (RFC 9457 Problem Details, cursor pagination, Idempotency-Key, ETag/concurrency, HTTP semantics, 202+polling, RateLimit headers), `api-security-engineer` (OWASP API Security Top 10 2023 — BOLA/BOPLA/BFLA, token/scope validation, resource-consumption limits, SSRF, unsafe consumption), `api-testing-engineer` (consumer-driven contract tests, Spectral lint in CI, mocking/virtualization, Newman + Postman MCP, k6 load), `api-platform-engineer` (gateway/management design, dev portal + SDK codegen DX, lifecycle/sunset rollout, observability).
- **knowledge/** — citation-grounded reference with Mermaid **decision trees** (paradigm selection, versioning, pagination, OAuth2 grant/auth-flow, OWASP control map, test-type selection, gateway build-vs-buy) and a dated **2026 spec capability map** (OpenAPI 3.1/3.2, AsyncAPI 3.0, Arazzo, JSON Schema, the IETF `RateLimit`/`Idempotency-Key` drafts).
- **best-practices/** — 22 named, citable rules across design / build / secure / test / operate, surfaced in the marketplace repo-guide + dashboard Guidance tab.
- **templates/** — contract-first OpenAPI & AsyncAPI skeletons, Problem Details catalog, Spectral style-guide ruleset, API design-review checklist, deprecation/sunset plan.
- **commands/** — `/api-engineering:design-api`, `:review-api-design`, `:harden-api`, `:scaffold-error-model`, `:lint-api-spec`, `:generate-contract-tests`.
- **1 advisory hook** (`check-api-anti-patterns.sh`, `APIENG_STRICT=1` to block): API key in query, HTTP Basic scheme, hardcoded token, wildcard CORS + credentials, stale OpenAPI version.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install api-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Boundaries (seams)

This plugin owns the API **you produce**. It cross-links — rather than duplicates — the surfaces below.

| Need | Goes to |
|---|---|
| An app on the **Claude API**, an **MCP server**, or the **Agent SDK** | `claude-app-engineering` |
| **Consuming Microsoft Graph** specifically | `microsoft-graph` |
| **Azure API Management** host/infra, the gateway *resource* | `azure-cloud/integration-engineer` |
| **End-user login UX** (social SSO, magic link, passkeys) | `auth-identity` |
| An **ELT / data connector** against a SaaS API | `data-platform/connector-developer` |
| Any **security/authorization/exposure verdict** | `ravenclaude-core/security-reviewer` |

The line with `auth-identity`: it **authenticates the person**; this plugin **secures the API surface** (token/scope validation, object & function authorization, consumption limits). The line with `azure-cloud`: the gateway *design* is here; the gateway *infrastructure* is there. See [`CLAUDE.md`](./CLAUDE.md) for the team constitution.

## Grounding

Volatile facts — spec versions (OpenAPI 3.1 vs 3.2, AsyncAPI 3.0, Arazzo), the IETF `RateLimit` and `Idempotency-Key` **drafts** (not yet RFCs as of 2026-06), OWASP edition specifics, and tool feature sets — carry retrieval dates in the knowledge bank and are re-verified before quoting. RFC 9457 (the Problem Details error model) obsoletes RFC 7807; the OWASP API Security Top 10 reference edition here is **2023**.
