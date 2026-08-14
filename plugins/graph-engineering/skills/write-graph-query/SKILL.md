---
name: write-graph-query
description: "Write a bounded, typed traversal. Cypher examples first, then ISO GQL, then Gremlin or SPARQL 1.1 stubs. Flag unbounded * and untyped -[]- as bugs. Includes GraphRAG local/global/DRIFT query patterns."
---

# Skill: write-graph-query

> **Invoked by:** `graph-query-engineer` (primary).
>
> **When to invoke:** "write this Cypher/GQL"; "why is this path slow?"; "local vs global GraphRAG search."
>
> **Output:** language pick + bounded pattern + index advice + lint result. Fill [`../../templates/query-language-decision.md`](../../templates/query-language-decision.md).

## Procedure

1. Pick the language from the **engine + model**, not the brand. Default teaching order: **Cypher first**, then GQL equivalent, then Gremlin / SPARQL 1.1 stubs. See [`../../knowledge/graph-languages-and-engines-2026.md`](../../knowledge/graph-languages-and-engines-2026.md).
2. **Type every relationship.** Bound every quantified path (`*1..N` or GQL `{1, N}`).
3. If the user pasted `-[*]->` or `-[]-`, rewrite it; do not “just add LIMIT.”
4. If the job is PageRank / community / global shortest-path over a projection, say **algorithm library** — do not invent `CALL algo.*`.
5. **GraphRAG query section** (only after a retrieval graph exists):
   - **Local** — bounded typed neighborhood of seed entities.
   - **Global** — read community summaries (not an unbounded walk).
   - **DRIFT** — local first, escalate to community text.
   Construction stays on `construct-retrieval-graph`.
6. Lint snippets with [`../../scripts/lint_graph_shape.py`](../../scripts/lint_graph_shape.py). Pre-GQL `*` in a `.gql` file is a WARNING.

## Guardrails

- Advisory only — the user runs the snippet. No driver.
- Not Neo4j-only. Not GraphQL (`.graphql` → `graphql-engineering`).
- Date any engine claim `[verify-at-use]`.
- SPARQL is 1.1 only.
