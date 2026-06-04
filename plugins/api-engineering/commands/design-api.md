---
description: Design an API contract-first — choose the paradigm (REST/GraphQL/gRPC/webhooks/async) by interaction shape, model resources not RPC verbs, author an OpenAPI 3.1/3.2 or AsyncAPI 3.0 skeleton with RFC 9457 errors + cursor pagination + security schemes, and set the versioning posture.
argument-hint: "[the capability, e.g. 'an orders API for partner integrations']"
---

# Design an API (contract-first)

You are running `/api-engineering:design-api`. Design the API for what the user described (`$ARGUMENTS`) following this plugin's `api-design-architect` discipline — paradigm first, contract before code.

## When to use this

You're starting a new API or service interface. For securing it, run `/api-engineering:harden-api`. For the error model specifically, `/api-engineering:scaffold-error-model`. To gate the resulting spec in CI, `/api-engineering:lint-api-spec`.

## Steps

1. **Pick the paradigm by interaction shape** — traverse the paradigm tree in [`../knowledge/api-design-decision-trees.md`](../knowledge/api-design-decision-trees.md). REST for resource CRUD, GraphQL for client-shaped reads over a deep graph (and name the caching/complexity cost), gRPC for internal low-latency, webhooks/AsyncAPI for "tell me when X happens." **State the trade.** (`design-pick-the-paradigm-by-interaction-shape.md`)
2. **Model resources, not RPC verbs** — plural noun collections, sub-resources for relationships, HTTP methods as the verbs; state transitions as fields or transition resources, never `/x/{id}/doThing`. (`design-model-resources-not-rpc-verbs.md`)
3. **Author the contract first** — produce an OpenAPI 3.1/3.2 (or AsyncAPI 3.0) skeleton from [`../templates/openapi-skeleton.yaml`](../templates/openapi-skeleton.yaml) / [`../templates/asyncapi-skeleton.yaml`](../templates/asyncapi-skeleton.yaml), baking in: RFC 9457 Problem Details errors, cursor pagination, an `Idempotency-Key` on unsafe writes, `ETag` on mutable resources, and an OAuth2 security scheme on every operation. (`design-contract-first-not-code-first.md`)
4. **Set the versioning posture** — URI vs header, and what counts as breaking vs additive; if changing an existing API, attach a deprecation plan. (`design-version-only-for-breaking-changes.md`)
5. **Make it governable** — emit a Spectral ruleset ([`../templates/spectral-ruleset.yaml`](../templates/spectral-ruleset.yaml)) so the spec is gated in CI. (`design-lint-the-spec-as-governance.md`)

## Guardrails

- Don't default to GraphQL/gRPC because they're modern — pick by interaction shape and name the cost.
- Don't generate the spec from code after the fact; the contract leads.
- Quote spec versions (OpenAPI 3.1/3.2, AsyncAPI 3.0, Arazzo) with a retrieval date; tag volatile facts `[verify-at-build]`.
- This plugin is advisory: emit the contract + the design rationale. Route the security model to `api-security-engineer` (verdict → `ravenclaude-core/security-reviewer`) and the build to `api-implementation-engineer`.
