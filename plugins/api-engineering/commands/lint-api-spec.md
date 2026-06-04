---
description: Lint an OpenAPI/AsyncAPI spec against the house Spectral ruleset as a governance gate — security on every operation, RFC 9457 errors, cursor pagination, no API key in query, OpenAPI 3.1+ — and wire it into CI to fail the build on violations.
argument-hint: "[path to the spec, e.g. openapi.yaml]"
---

# Lint an API spec (governance gate)

You are running `/api-engineering:lint-api-spec`. Lint the spec at `$ARGUMENTS` against this plugin's house style guide, following `api-testing-engineer` discipline.

## When to use this

Gating an API design in CI, or checking a spec against house conventions. Pair with `/api-engineering:review-api-design` for the judgment-call review the linter can't do.

## Steps

1. **Apply the house ruleset** from [`../templates/spectral-ruleset.yaml`](../templates/spectral-ruleset.yaml) (extends `spectral:oas`): every operation has `security`; 4xx/5xx offer `application/problem+json`; no `offset`/`page` pagination params; no `apiKey` `in: query`; OpenAPI 3.1+. (`design-lint-the-spec-as-governance.md`)
2. **Run it** — `spectral lint <spec> --fail-severity=error` (verify the Spectral invocation against current docs, `[verify-at-build]`).
3. **Group findings by severity** (error vs warn) and map each to the house rule it violates, with the fix.
4. **Wire it into CI** — a required step that fails the build on `error`; for an existing spec, start strict rules at `warn` and ratchet to `error` as the team adopts.

## Guardrails

- A spec that fails the linter doesn't merge — that's the point; don't soften it to a no-op.
- Don't disable the linter to pass a hard case — add a documented, targeted rule exception instead.
- Spectral's built-in ruleset names are volatile across versions — verify before relying on a specific built-in rule (`[verify-at-build]`).
