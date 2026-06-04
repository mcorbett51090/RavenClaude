# Ship a developer portal and SDKs generated from the spec

**Status:** Pattern — docs and SDKs are build artifacts of the contract; hand-maintained ones drift.

**Domain:** API operations / developer experience

**Applies to:** `api-engineering`

---

## Why this exists

The best API is unusable if consumers can't find the docs, or if the docs and SDKs disagree with the running API. Because the OpenAPI/AsyncAPI document is the single source of truth, the documentation portal and the client SDKs should be **generated from it** — so they can never drift from the contract, and a spec change propagates to both automatically. Hand-written docs and hand-rolled clients are a maintenance debt that goes stale on the first change.

## How to apply

Render docs and generate SDKs from the same spec, in CI.

```
# Docs portal — rendered from the spec
redocly build-docs openapi.yaml          # or Scalar / Stoplight / Backstage TechDocs

# SDKs — generated from the spec, versioned + published
openapi-generator-cli generate -i openapi.yaml -g typescript-axios -o ./sdk/ts
# (or Speakeasy / Fern / Kiota for typed, idiomatic clients)
```

**Do:**
- Regenerate docs + SDKs from the spec on every release; version and publish SDKs alongside the API.
- Include runnable examples, auth setup, and error-model docs (the Problem Details catalog) in the portal.

**Don't:**
- Hand-maintain reference docs or client libraries that duplicate the contract; let the portal lag the spec.

## Edge cases / when the rule does NOT apply

Generated SDKs sometimes need a thin hand-written ergonomics layer (pagination iterators, retry helpers) on top of the generated core — that's fine as long as the core stays generated. A tiny internal API may need only the rendered spec, not full SDKs. Conceptual/onboarding docs (the "getting started" narrative) are written, not generated — pair them with the generated reference.

## See also

- [`./design-contract-first-not-code-first.md`](./design-contract-first-not-code-first.md)
- [`../templates/problem-details-catalog.md`](../templates/problem-details-catalog.md)
- [`../agents/api-platform-engineer.md`](../agents/api-platform-engineer.md)

## Provenance

Codifies the spec-as-source-of-truth DX practice (Redocly/Scalar docs; OpenAPI Generator / Speakeasy / Fern / Kiota codegen). Tool capabilities verified before quoting. Retrieved/verified 2026-06-04.

---

_Last reviewed: 2026-06-04 by `claude`_
