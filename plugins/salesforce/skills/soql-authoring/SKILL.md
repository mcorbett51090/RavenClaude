---
name: soql-authoring
description: Write selective, bulk-safe SOQL that binds its variables and avoids non-selective-query errors on large objects. Use when authoring or fixing a SOQL query, especially against high-volume objects.
---

# SOQL Authoring

Produce a SOQL query that is selective (index-friendly), bulk-safe, and injection-safe.

## When to use

Authoring a new query, fixing a non-selective-query error, or hardening dynamic SOQL.

## Steps

1. **Filter on an indexed field.** Prefer Id, Name, audit fields, lookups, external IDs, unique fields, or a custom index. Reject leading-`%` wildcards and negative operators on large objects. See `knowledge/large-data-volume-design.md`.
2. **Make the filter selective.** Confirm the predicate clears the optimizer threshold; add a bounded date/status filter if it doesn't.
3. **Bind every variable.** Use `:var` bind syntax — never string-concatenate user input. For dynamic SOQL, bind or `String.escapeSingleQuotes`. (House opinion #8; escalate injection findings to `ravenclaude-core/security-reviewer`.)
4. **Enforce FLS.** Add `WITH USER_MODE` for user-context queries. **At API v67.0+ (Summer '26) `WITH SECURITY_ENFORCED` is removed and does not compile** — use `WITH USER_MODE` (also supports polymorphic fields and returns the full set of access errors); on older API versions `WITH SECURITY_ENFORCED` still works. `[verify-at-build]`
5. **Stay bulk-safe.** Query once with `WHERE Id IN :ids`; never put the query in a loop.
6. **Limit the result.** Add `LIMIT` and select only the fields you use.

## Output

The query, the index it relies on, the bind variables, and a one-line note on selectivity and FLS.
