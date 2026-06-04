# Lint the spec as governance — a Spectral ruleset is the style guide with teeth

**Status:** Pattern — strong default; a human style guide nobody can fail is decoration.

**Domain:** API design / governance

**Applies to:** `api-engineering`

---

## Why this exists

Every team writes an "API style guide" document. Almost none of them are followed consistently, because a document can't fail a PR. Encoding the house conventions as a **Spectral** ruleset (or an equivalent OpenAPI linter) turns the style guide into an automated gate: a spec that violates naming, omits the error model, leaves an operation unsecured, or ships without examples fails CI and doesn't merge. Governance you can't enforce is governance you don't have.

## How to apply

Author a ruleset, run it locally and in CI, fail the build on errors.

```yaml
# .spectral.yaml — extends the OAS ruleset, adds house rules
extends: ["spectral:oas"]
rules:
  operation-operationId: error          # every operation has an operationId
  operation-tag-defined: error
  oas3-valid-media-example: warn
  # house rules:
  problem-details-on-errors:            # 4xx/5xx must use application/problem+json
    given: $.paths[*][*].responses[?(@property >= '400')].content
    then: { field: "application/problem+json", function: truthy }
    severity: error
  security-on-every-operation:
    given: $.paths[*][*]
    then: { field: security, function: truthy }
    severity: error
```

```
# CI gate
spectral lint openapi.yaml --fail-severity=error
```

**Do:**
- Keep the ruleset in version control next to the spec; run it pre-commit and in CI.
- Start from `spectral:oas` and add house rules incrementally.

**Don't:**
- Ship a style guide as prose only; let a non-conforming spec merge.

## Edge cases / when the rule does NOT apply

A brand-new spec can start with rules at `warn` and ratchet to `error` as the team adopts them. Vendor-extension-heavy specs may need targeted rule exceptions — document them in the ruleset, don't disable the linter.

## See also

- [`../templates/spectral-ruleset.yaml`](../templates/spectral-ruleset.yaml)
- [`./design-contract-first-not-code-first.md`](./design-contract-first-not-code-first.md)
- [`../agents/api-testing-engineer.md`](../agents/api-testing-engineer.md)
- [Spectral](https://docs.stoplight.io/docs/spectral/) — authoritative `[verify-at-build]`

## Provenance

Codifies house opinion #11 (CLAUDE.md §3). Spectral feature set verified before quoting. Retrieved/verified 2026-06-04.

---

_Last reviewed: 2026-06-04 by `claude`_
