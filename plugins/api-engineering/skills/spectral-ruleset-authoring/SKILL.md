---
name: spectral-ruleset-authoring
description: "Playbook for writing and wiring a Spectral ruleset that enforces an API style guide in CI — covers rule anatomy, severity levels, custom functions, and the recommended core-rules baseline."
---

# Spectral Ruleset Authoring

## When to Use This Skill

Use when setting up spec-linting governance for a new API program, when migrating from an ad-hoc review checklist to automated enforcement, or when adding a custom rule to catch a project-specific violation.

## 1. Rule Anatomy

```yaml
rules:
  rule-id:
    message: "{{description}} — {{error}}"
    description: "Human-readable explanation of what the rule checks."
    severity: error        # error | warn | info | hint
    given: "$.paths.*.*.responses"     # JSONPath expression selecting nodes to check
    then:
      function: truthy     # built-in or custom function
```

| Severity | CI behaviour |
|---|---|
| `error` | Non-zero exit — blocks merge |
| `warn` | Logged, exit 0 — advisory |
| `info` | Informational only |

Use `error` only for violations that break consumers or contradict a hard house rule. Use `warn` for style preferences.

## 2. Recommended Baseline Ruleset

```yaml
extends: ["spectral:oas"]

rules:
  # Enforce RFC 9457 error media type
  problem-json-on-errors:
    message: "Error responses must use application/problem+json, not application/json."
    severity: error
    given: "$.paths.*.*.responses[?(@property >= '400')].content"
    then:
      function: schema
      functionOptions:
        schema:
          not:
            required: ["application/json"]

  # Require operationId on every operation
  operation-id-required:
    message: "Every operation must have an operationId."
    severity: error
    given: "$.paths.*[get,post,put,patch,delete,options,head]"
    then:
      field: operationId
      function: truthy

  # Reject RPC verbs in paths
  no-rpc-path-names:
    message: "Path segments should be nouns, not verbs (no get/create/update/delete prefixes)."
    severity: warn
    given: "$.paths"
    then:
      function: pattern
      functionOptions:
        notMatch: "/(get|create|update|delete|list|fetch|retrieve)[A-Z_]"

  # Require tags on every operation
  operation-tags-required:
    message: "Every operation must have at least one tag."
    severity: warn
    given: "$.paths.*[get,post,put,patch,delete]"
    then:
      field: tags
      function: truthy

  # Flag OpenAPI 3.0.x (prefer 3.1)
  prefer-openapi-31:
    message: "Prefer OpenAPI 3.1+ (JSON-Schema-aligned). [verify-at-build]"
    severity: warn
    given: "$"
    then:
      field: openapi
      function: pattern
      functionOptions:
        notMatch: "^3\\.0\\."
```

## 3. Custom JavaScript Function

When a built-in (`truthy`, `falsy`, `pattern`, `schema`, `enumeration`, `length`) is insufficient:

```js
// functions/cursor-pagination.js
export default function cursorPagination(targetVal, _opts, context) {
  const { path } = context;
  // targetVal is the schema object for a list-response
  if (!targetVal.properties?.cursor) {
    return [{ message: "List response schema must include a 'cursor' property for keyset pagination.", path }];
  }
  return [];
}
```

Reference it in the ruleset:

```yaml
functions: [cursor-pagination]

rules:
  list-response-has-cursor:
    message: "List response schemas must include a cursor property."
    severity: error
    given: "$.components.schemas[?(/Page$|Collection$/.test(@property))]"
    then:
      function: cursor-pagination
```

## 4. CI Integration

```yaml
# .github/workflows/lint-api-spec.yml
- name: Spectral lint
  run: npx --yes @stoplight/spectral-cli@latest lint openapi.yaml --ruleset .spectral.yaml --fail-severity error
```

Exit codes: `0` = no errors, `1` = parse error, `2` = lint errors at the fail-severity level.

## 5. Rule Development Workflow

1. Pick one violation from the anti-patterns list in `CLAUDE.md §4`.
2. Write the `given` JSONPath against the spec using the Spectral Playground (`stoplight.io/spectral`).
3. Add a test fixture: a minimal `openapi-bad.yaml` that triggers it + `openapi-good.yaml` that passes.
4. Set severity `warn` first; promote to `error` only after the team agrees it's a hard rule.
5. Document the rule's rationale in its `description` field — consumers filing a PR need to understand it.

## Pitfalls

- Setting everything to `error` — if CI blocks every commit, engineers disable the linter
- Using `given: "$"` (root) for rules that only apply to operations — overly broad paths slow the run and produce confusing error locations
- Writing rules that depend on a specific operation structure instead of OpenAPI semantics — test against multiple real specs before shipping
- Forgetting to pin the Spectral version in CI — Spectral minor updates occasionally add breaking rule changes to `spectral:oas`

## See Also

- [`../../agents/api-testing-engineer.md`](../../agents/api-testing-engineer.md) — wiring Spectral in CI, Newman, and contract testing
- [`../../agents/api-design-architect.md`](../../agents/api-design-architect.md) — API style guide governance
- [`../../CLAUDE.md`](../../CLAUDE.md) — house opinion: lint the spec as governance
