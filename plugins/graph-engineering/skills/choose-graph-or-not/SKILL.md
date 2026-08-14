---
name: choose-graph-or-not
description: "Walk the graph-vs-relational decision tree and return a one-screen verdict — LPG, RDF, stay relational, stay RAG, or stay KV — plus the neighbor hand-off. Reach for this before any labels or Cypher."
---

# Skill: choose-graph-or-not

> **Invoked by:** `graph-data-modeler` (primary).
>
> **When to invoke:** "should this be a graph?"; "do we need Neo4j?"; "LPG or RDF?"; any request to introduce a graph store.
>
> **Output:** one-screen verdict + the tree leaf + a neighbor hand-off if the answer is no.

## Procedure

1. **Read the workload.** What question is asked at read time? What is rolled back at write time?
2. **Traverse** [`../../knowledge/graph-vs-relational-decision-tree.md`](../../knowledge/graph-vs-relational-decision-tree.md). Start from the `database-engineering` “specialized engine” leaf. Do not skip to labels.
3. **If relational / KV / document / RAG:** stop. Name the owner (`database-engineering`, `ai-rag-engineering`, or stay put). Do not sketch an LPG “anyway.”
4. **If LPG:** proceed to [`../model-property-graph/SKILL.md`](../model-property-graph/SKILL.md).
5. **If RDF:** say SPARQL 1.1 + shared IRIs; do not invent SPARQL 1.2.
6. **If retrieval-graph:** stop unless a BM25 / no-graph baseline has lost. Hand III.a to `memory-architect-lead`. Then [`../construct-retrieval-graph/SKILL.md`](../construct-retrieval-graph/SKILL.md).

## Guardrails

- Multi-row transactions + ad-hoc SQL + known schema → not a graph.
- “We might want a graph later” is not a yes.
- GraphQL and Microsoft Graph API are **not** this tree.
