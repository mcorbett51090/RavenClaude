---
description: Scaffold a consistent RFC 9457 Problem Details (application/problem+json) error model for an API — a catalog of stable type URIs, validation-error mapping, and the response shape — replacing bespoke per-endpoint error shapes.
argument-hint: "[the API, or the error cases to model]"
---

# Scaffold an error model (RFC 9457 Problem Details)

You are running `/api-engineering:scaffold-error-model`. Build the standard error model for `$ARGUMENTS` following this plugin's `api-implementation-engineer` discipline and [`../templates/problem-details-catalog.md`](../templates/problem-details-catalog.md).

## When to use this

The API returns inconsistent error shapes, or you're defining errors for a new contract. Part of `/api-engineering:design-api`; standalone when retrofitting an existing API.

## Steps

1. **Adopt `application/problem+json` (RFC 9457)** as the one error content type — RFC 9457 obsoletes RFC 7807; same wire format (`type`/`title`/`status`/`detail`/`instance` + extensions). (`build-one-error-model-rfc9457-problem-details.md`)
2. **Build the `type` catalog** — a stable URI per error class (validation, unauthenticated, forbidden, not-found, conflict, precondition-failed, rate-limited, payload-too-large, internal-error). A `type` URI is a contract identifier; never repurpose one. Use the catalog template.
3. **Map validation errors** to a single `validation-error` type with an `errors[]` array (`pointer` + `detail`) rather than a different shape per field.
4. **Match `status` to the HTTP status line**; pick `422` for semantic vs `400` for syntactic; `409`/`412`/`429` for conflict/stale/throttle.
5. **Guarantee no leakage** — no stack traces, SQL, or internal hostnames in `detail`; use a `traceId` extension for correlation instead.

## Guardrails

- Never return `200` with an error inside; never invent a per-endpoint error shape.
- Keep the catalog in the developer portal so consumers can code against the `type` set.
- GraphQL and gRPC have native error models — Problem Details is for HTTP/REST; don't force it on them.
- `type: "about:blank"` is valid when the status code is the whole story.
