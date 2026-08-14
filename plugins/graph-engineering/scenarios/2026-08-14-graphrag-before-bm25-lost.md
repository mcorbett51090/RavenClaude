# GraphRAG before BM25 lost

**Date:** 2026-08-14
**Tags:** graphrag, baseline
**Unverified** — teaching scenario.

A team stood up entity extraction + a community graph because “GraphRAG is SOTA.” No BM25 or hybrid-vector number existed. Construction ran overnight; answers were worse and slower than `grep`.

**Fix:** run the no-graph and BM25 / hybrid baselines via `ai-rag-engineering`. Hand “is III.a worth it?” to `memory-architect-lead`. Only then use `construct-retrieval-graph`.

See [`../best-practices/graphrag-needs-a-humbling-baseline.md`](../best-practices/graphrag-needs-a-humbling-baseline.md).
