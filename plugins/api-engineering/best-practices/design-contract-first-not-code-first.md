# Contract-first, not code-first — write the spec before the server

**Status:** Absolute rule — a generated-after-the-fact spec is documentation, not a contract.

**Domain:** API design

**Applies to:** `api-engineering`

---

## Why this exists

The OpenAPI/AsyncAPI document is the single source of truth that consumers, mock servers, SDK generators, contract tests, and the docs portal all derive from. When the spec is *generated from code annotations after shipping*, the code is the truth and the spec is a lagging shadow — it can't gate the design, can't be reviewed before effort is spent, and drifts the moment someone edits a handler. Design-time is the cheapest place to fix an API; once clients integrate, every change has a blast radius.

## How to apply

Write and review the spec **first**, lint it, then build the server to satisfy it. The spec is a reviewed artifact in the PR, not an export.

```
1. Draft openapi.yaml (resources, operations, schemas, error model, security schemes)
2. Lint it with Spectral (house ruleset) — must pass
3. Review the CONTRACT (paradigm, resources, versioning) before writing handlers
4. Generate the mock (Prism/Postman) so consumers start in parallel
5. Build the server to the spec; schema-validate responses against it in CI
```

**Do:**
- Keep the spec in version control and review changes to it like code.
- Generate mocks, SDKs, docs, and contract tests *from* the spec.

**Don't:**
- Treat a Swagger export from running code as "the contract."
- Let the implementation and the spec be edited independently with no CI check that they agree.

## Edge cases / when the rule does NOT apply

A throwaway internal spike with no external consumers can defer the formal spec — but the moment a second party integrates, the contract must lead. "Spec-augmented code-first" (annotations that *fail CI if they drift from a committed spec*) is an acceptable hybrid; uncontrolled generation is not.

## See also

- [`./design-lint-the-spec-as-governance.md`](./design-lint-the-spec-as-governance.md)
- [`./design-model-resources-not-rpc-verbs.md`](./design-model-resources-not-rpc-verbs.md)
- [`../agents/api-design-architect.md`](../agents/api-design-architect.md)
- [OpenAPI Specification](https://spec.openapis.org/) — authoritative

## Provenance

Codifies house opinion #1 (CLAUDE.md §3), grounded in the contract-first workflow the OpenAPI/AsyncAPI tooling ecosystem is built around. Retrieved/verified 2026-06-04.

---

_Last reviewed: 2026-06-04 by `claude`_
