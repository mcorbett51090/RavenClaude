---
description: "Design a GraphRAG retrieval-graph architecture after a BM25/no-graph baseline has lost. Does not pick memory paradigm III.a."
argument-hint: "[the corpus and the multi-hop question]"
---

# Construct retrieval graph

You are running `/graph-engineering:construct-retrieval-graph` for `$ARGUMENTS`. Apply [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps

1. Demand no-graph + BM25/hybrid results. Stop if they have not lost.
2. If the question is agent memory, hand to `memory-architect-lead`.
3. Fill [`../templates/retrieval-graph-design.md`](../templates/retrieval-graph-design.md).
4. Extract typed edges; pick local/global/dual-layer; name search mode.
5. Hand eval to `ai-rag-engineering`. Hand query patterns to `/write-graph-query`.

## Guardrails

- Advisory only. No live database. No bake-off ranking from author-reported numbers.
- See [`../skills/construct-retrieval-graph/SKILL.md`](../skills/construct-retrieval-graph/SKILL.md).
