# Generate API Reference from the Spec; Never Hand-Maintain It

**Status:** Absolute rule
**Domain:** Technical Writing — API reference
**Applies to:** `technical-writing-docs`

---

## Why this exists

A hand-maintained API reference document will always drift from the actual API. The moment the spec changes and the person who updates the code is not the person who updates the doc, the reference becomes a liability: it confidently states the wrong parameter name, the wrong response shape, or the wrong auth requirement. The reader follows the doc into an error and loses trust in the entire documentation site. When a machine-readable spec exists (OpenAPI, AsyncAPI, GraphQL schema), generating the reference from the spec is the only sustainable path.

## How to apply

**Decision by spec availability:**

| Source truth available | Action |
|---|---|
| OpenAPI spec | Generate with Redocly, Stoplight, or Mintlify; never duplicate by hand |
| AsyncAPI spec | Generate with AsyncAPI Generator |
| GraphQL schema | Generate with GraphQL Docs, Docusaurus graphql plugin, or similar |
| No spec exists | Generate the spec first; treat hand-written reference as a temporary stopgap and date it |

**CI enforcement:**
```yaml
# Example: verify the reference is current (OpenAPI → Redocly)
steps:
  - name: Lint OpenAPI spec
    run: npx @redocly/cli lint openapi.yaml
  - name: Build reference docs
    run: npx @redocly/cli build-docs openapi.yaml --output docs/reference/index.html
  - name: Fail if spec changed but reference not rebuilt
    run: git diff --exit-code docs/reference/
```

**Do:**
- Wire the reference-generation step into the CI pipeline and block merges that leave the reference out of date.
- Store the spec (`openapi.yaml` / `asyncapi.yaml`) in the same repository as the code it documents.
- Commit the generated reference to the docs site build, not to source control (or use a build artifact step).

**Don't:**
- Edit generated reference files by hand — all changes go through the spec.
- Accept a PR that updates an endpoint without simultaneously updating the spec.
- Use the spec as an internal-only artifact while maintaining a separate "public docs" copy.

## Edge cases / when the rule does NOT apply

- **Immature or unstable APIs in active development**: a generated reference from a draft spec is still correct — the argument for hand-maintained docs ("the spec keeps changing") is an argument for a better spec process, not for hand-maintenance.
- **Legacy APIs with no spec**: a hand-maintained reference is the only option; date every section explicitly and schedule a spec-authoring sprint as a debt item.

## See also

- [`../agents/api-reference-writer.md`](../agents/api-reference-writer.md) — the agent that owns the API reference
- [`./examples-must-run.md`](./examples-must-run.md) — companion rule: generated reference is not enough if the examples in it aren't tested

## Provenance

Codifies house opinion #2 ("Docs-as-code, versioned with the product") applied to API reference. Spec-driven reference is the current industry standard practice for REST/async APIs (Redocly docs, OpenAPI Initiative, Stoplight). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
