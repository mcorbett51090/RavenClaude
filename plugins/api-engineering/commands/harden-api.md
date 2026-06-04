---
description: Run an OWASP API Security Top 10 (2023) pass over an API or endpoint — object-level (BOLA) and function-level (BFLA) authorization, token/scope validation, property-level authorization (BOPLA), resource-consumption limits, SSRF, misconfiguration, inventory, and unsafe upstream consumption. Designs controls; routes the verdict to security-reviewer.
argument-hint: "[the API/endpoint to harden, or path to the spec]"
---

# Harden an API (OWASP API Top 10 2023)

You are running `/api-engineering:harden-api`. Secure what the user described (`$ARGUMENTS`) following this plugin's `api-security-engineer` discipline. **This designs controls — it does not issue the final sign-off; that routes to `ravenclaude-core/security-reviewer`.**

## When to use this

Securing an API surface, or running a security review. For the design review more broadly, `/api-engineering:review-api-design`.

## Steps — the OWASP API Security Top 10 (2023), in priority order

1. **API1 — BOLA:** every object access verifies ownership/tenancy server-side from the token, never a client-supplied ID. Add the explicit negative test (another tenant's ID → 403/404). (`secure-authorize-every-object-bola.md`)
2. **API2 — Authentication:** validate the token (signature against JWKS, `iss`/`aud`/`exp`/`nbf`, reject `alg:none`) before trusting any claim; least-privilege scopes; correct OAuth2 grant per client (grant tree). (`secure-validate-tokens-and-scopes-server-side.md`)
3. **API3 — BOPLA:** allow-list input properties (no mass-assignment to `role`) and output properties (no over-exposure).
4. **API4 — Consumption:** bound page size, payload, GraphQL depth/complexity, rate, and quota; advertise the `RateLimit` headers. (`secure-limit-resource-consumption.md`)
5. **API5 — BFLA:** gate every privileged function by role/scope server-side; default-deny new endpoints. (`secure-authorize-every-function-bfla.md`)
6. **API6–API8:** sensitive-business-flow friction; SSRF allow-listing of client-supplied URLs; misconfig (no wildcard CORS+credentials, no verbose errors, TLS + security headers).
7. **API9 — Inventory:** enumerate versions × environments; flag shadow/zombie endpoints (pairs with deprecation).
8. **API10 — Unsafe consumption:** validate, bound, and time out responses from upstream APIs. (`secure-never-trust-upstream-apis.md`)

## Guardrails

- Traverse the OWASP control map and grant-selection trees in [`../knowledge/api-security-decision-trees.md`](../knowledge/api-security-decision-trees.md) — don't keyword-match a concern to a control.
- Never embed a real secret/token in a sample; use a placeholder and say where it's injected.
- The OWASP reference edition here is **2023** — don't conflate with the OWASP Web Top 10; tag the edition / `[verify-at-build]`.
- **Output the control design + the gap list + the residual risk, and explicitly route the verdict to `ravenclaude-core/security-reviewer`.** The end-user login flow is `auth-identity`'s.
