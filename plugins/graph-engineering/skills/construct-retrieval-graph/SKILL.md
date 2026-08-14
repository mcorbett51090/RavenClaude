---
name: construct-retrieval-graph
description: "Design a retrieval-graph (GraphRAG) extract-index-search architecture only after a BM25/no-graph baseline has lost. Hands paradigm III.a to memory-engineering and eval to ai-rag-engineering."
---

# Skill: construct-retrieval-graph

> **Invoked by:** `graph-data-modeler` (primary). Query patterns after construction go to `write-graph-query`.
>
> **When to invoke:** "stand up GraphRAG"; "multi-hop corpus synthesis"; "community summaries over this corpus."
>
> **Output:** a filled [`../../templates/retrieval-graph-design.md`](../../templates/retrieval-graph-design.md).

## Procedure

1. **STOP** if a no-graph baseline and a BM25 / hybrid-vector baseline have not lost on a named eval. Cite [`../../best-practices/graphrag-needs-a-humbling-baseline.md`](../../best-practices/graphrag-needs-a-humbling-baseline.md).
2. **STOP** if the real question is “should the *agent* remember in a graph?” That is paradigm III.a — hand to `memory-architect-lead`. Read [`../../knowledge/graphrag-construction.md`](../../knowledge/graphrag-construction.md).
3. Pick a **family** as design intent (Microsoft GraphRAG / HippoRAG / LightRAG) — not a bake-off winner. Author-reported metrics stay disclaimed.
4. **Extract** typed entities and typed relationships. Fill a supernode plan.
5. **Index** — local / global (communities) / dual-layer. Name the offline bill.
6. **Search mode** — local / global / DRIFT / PPR. Hand the actual pattern to `write-graph-query`.
7. **Eval** — `rag-architect-lead` / `retrieval-eval-analyst` (recall@k, faithfulness). Do not invent a graph-only eval and call it done.

## Guardrails

- Do not re-decide memory paradigm III.a.
- Do not skip the humbling baseline.
- Do not stand up a graph server from this skill.
- Chunking / embeddings / hybrid lexical stay in `ai-rag-engineering`.
