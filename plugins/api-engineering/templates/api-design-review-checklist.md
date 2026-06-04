# API design review checklist — `<API name>` `<version>`

> Run this before an API contract merges. Pair it with the Spectral lint (automated) —
> this checklist covers the judgment calls Spectral can't. Reviewer: `<name>` · Date: `<YYYY-MM-DD>`.
> Owners: `api-design-architect` (design), `api-security-engineer` (security), `api-testing-engineer` (governance).

## 1. Paradigm & contract

- [ ] The paradigm (REST / GraphQL / gRPC / webhooks / async) is **chosen by interaction shape**, and the trade is written down.
- [ ] The contract is **OpenAPI 3.1/3.2 or AsyncAPI 3.0**, written **before** the server (contract-first), and committed to version control.
- [ ] The spec **passes the Spectral house ruleset** (`--fail-severity=error`).

## 2. Resource & operation modeling (REST)

- [ ] Paths are **nouns**, plural collections; **no RPC verbs in URLs** (`/getX`, `/x/{id}/doThing`).
- [ ] HTTP methods match semantics: `GET`/`HEAD` safe, `PUT`/`DELETE` idempotent, `POST` not.
- [ ] Status codes are correct (`201`+`Location` on create, `204` empty, `409`/`412`/`422`/`429` used deliberately).

## 3. Cross-cutting build conventions

- [ ] **Errors** use `application/problem+json` (RFC 9457) with stable `type` URIs from a catalog — no bespoke shapes, no stack traces, no 200-wrapped errors.
- [ ] **Collections** are **cursor-paginated** by default; page size is bounded server-side.
- [ ] **Unsafe retries** (money/orders) take an **`Idempotency-Key`**; the dedup window is defined.
- [ ] **Concurrency** on contended resources uses **`ETag` + `If-Match`** (no last-write-wins).
- [ ] **Long-running** operations use **`202` + an operation resource** to poll (no held-open requests).

## 4. Security (verdict → `ravenclaude-core/security-reviewer`)

- [ ] **Object-level authorization (BOLA/API1):** every object access checks ownership/tenancy server-side; client IDs are not trusted.
- [ ] **Function-level authorization (BFLA/API5):** every privileged function is role/scope-gated server-side.
- [ ] **Authentication (API2):** tokens are validated (signature/`iss`/`aud`/`exp`; `alg:none` rejected); scopes are least-privilege.
- [ ] **Property-level (BOPLA/API3):** input and output properties are allow-listed (no mass-assignment, no over-exposure).
- [ ] **Consumption (API4):** page size, payload, query depth/complexity, rate, and quota are all bounded.
- [ ] **Misconfig (API8):** no wildcard CORS with credentials; no verbose errors; security headers + TLS enforced.
- [ ] **SSRF (API7) / unsafe consumption (API10):** client-supplied URLs allow-listed; upstream responses validated/bounded.
- [ ] **Auth scheme:** no API key in the query string; no HTTP Basic; no hardcoded token/secret in spec or code.

## 5. Versioning & lifecycle

- [ ] The change is classified **additive vs breaking**; the version posture is set; additive changes don't bump.
- [ ] A breaking change has a **`Deprecation`/`Sunset`** plan with a dated timeline and migration guide.
- [ ] Every deployed version × environment is **inventoried** (no shadow/zombie APIs — API9).

## 6. Governance & testing

- [ ] A **contract test** (consumer-driven) or schema-validation gate exists for known consumers.
- [ ] A **mock** is generated from the spec for parallel consumer development.
- [ ] An **SLO** is stated and a load test asserts it.
- [ ] Docs + SDKs are **generated from the spec** (no hand-maintained drift).

## Verdict

- **Design:** `<pass / changes-requested>` — `<notes>`
- **Security:** `<routed to security-reviewer / residual risk>` — `<notes>`
- **Governance:** `<gates wired / gaps>` — `<notes>`
