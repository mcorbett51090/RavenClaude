---
description: "Write a bounded, typed Cypher / ISO GQL / Gremlin / SPARQL traversal. Cypher first. Not /write-gql."
argument-hint: "[the question or pasted query to rewrite]"
---

# Write graph query

You are running `/graph-engineering:write-graph-query` for `$ARGUMENTS`. Apply [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps

1. Pick Cypher (default teaching), GQL, Gremlin, or SPARQL 1.1 from engine + model.
2. Type every relationship. Bound every quantified path.
3. Rewrite unbounded `*` and untyped `-[]-`.
4. GraphRAG local/global/DRIFT is a query-pattern section, not construction.
5. Lint snippets. Fill [`../templates/query-language-decision.md`](../templates/query-language-decision.md).

## Guardrails

- Advisory only. No live database. Not GraphQL.
- See [`../skills/write-graph-query/SKILL.md`](../skills/write-graph-query/SKILL.md).
