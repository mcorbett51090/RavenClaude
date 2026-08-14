# GraphRAG construction

**Last reviewed:** 2026-08-14

This file is **how to model and query a retrieval graph**. It does **not** decide whether a memory graph is the right paradigm.

**Mandatory first cite:** [`../../memory-engineering/knowledge/memory-engineering-paradigms.md`](../../memory-engineering/knowledge/memory-engineering-paradigms.md) — GraphRAG / HippoRAG v2 are paradigm **III.a** (structure-augmented extraction; large-batch **offline** indexing). BM25 was the highest-accuracy / lowest-cost system in that suite. If III.a has not beaten a no-memory baseline **and** a flat-retrieval baseline on *your* data, do not build a retrieval graph. Hand that decision to `memory-architect-lead`.

**Mandatory second cite:** `ai-rag-engineering` owns chunking, judgment sets, hybrid lexical/vector, recall@k, and token cost. This file does not re-teach those.

## Families (design intent, not a bake-off)

Author-reported numbers stay disclaimed. Do not rank these.

| Family | What it constructs | Search modes |
|---|---|---|
| **Microsoft GraphRAG** (C21) | Extract entities/edges from a corpus, cluster (Leiden) into communities, write community summaries | **Local** (entity neighborhood), **global** (community summaries), **DRIFT** (mixed) |
| **HippoRAG** (C22) | Knowledge graph + Personalized PageRank | Seed entities, then PPR over the graph |
| **LightRAG** (C23) | Dual-layer: knowledge graph **and** vectors | Graph hop + vector fallback |

Use the family that matches the *question shape*, not a leaderboard.

## When to reach for a retrieval graph

- The question is **multi-hop** across documents (“how is A connected to B through people or events?”).
- Or the question needs **corpus-level synthesis** (“what are the themes / communities?”).
- **And** BM25 / hybrid-vector has already lost on a named eval set.

Otherwise stay in `ai-rag-engineering`.

## Construction sequence

1. **Stop** if the humbling baseline has not lost. See [`../best-practices/graphrag-needs-a-humbling-baseline.md`](../best-practices/graphrag-needs-a-humbling-baseline.md).
2. **Extract** entities and typed relationships. Type the edges. Bound later hops.
3. **Index** — choose local (entity-centric), global (community summaries), or dual-layer. This is an offline bill (III.a).
4. **Search mode** — local / global / DRIFT / PPR. The query engineer writes the bounded traversal.
5. **Eval** — hand recall@k, faithfulness, and answer relevance to `ai-rag-engineering`. Do not invent a graph-only eval and call it done.

## Hard hand-offs

| Question | Owner |
|---|---|
| Should we pay for a **memory** graph at all? III.a vs BM25 vs no-memory? | `memory-engineering` / `memory-architect-lead` |
| Chunking, embeddings, hybrid lexical, recall@k, token budget | `ai-rag-engineering` / `rag-architect-lead`, `retrieval-eval-analyst` |
| Labels, edge types, supernodes in the extracted graph | `graph-data-modeler` (this plugin) |
| Bounded local/global query pattern | `graph-query-engineer` (this plugin) |

## See also

- [`../skills/construct-retrieval-graph/SKILL.md`](../skills/construct-retrieval-graph/SKILL.md)
- [`../templates/retrieval-graph-design.md`](../templates/retrieval-graph-design.md)

## Sources

- `plugins/memory-engineering/knowledge/memory-engineering-paradigms.md` (C06, III.a, BM25 baseline).
- Family descriptions C21–C23 in the 2026-08-14 FORGE claims table; metrics are author-reported.
