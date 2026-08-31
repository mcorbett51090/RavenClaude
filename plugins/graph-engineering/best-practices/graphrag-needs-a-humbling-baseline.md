# GraphRAG needs a humbling baseline

**Status:** Pattern (strong default)
**Domain:** Retrieval-graph construction
**Applies to:** `graph-engineering`

---

## Why this exists

`memory-engineering` classifies GraphRAG / HippoRAG as paradigm III.a — large-batch **offline** extraction. In that literature BM25 was both more accurate and cheaper than the LLM-mediated graph systems on the published suite. Building a retrieval graph before a no-graph and a flat-retrieval baseline have lost is buying the most expensive construction path on faith.

## How to apply

1. Measure a **no-graph** answer (long context or nothing).
2. Measure **BM25 / hybrid vector** via `ai-rag-engineering`.
3. Only then construct a retrieval graph, and only for multi-hop or corpus-level synthesis.

Do **not** re-decide paradigm III.a here. Hand “should we pay for a memory graph?” to `memory-architect-lead`.

## Edge cases / when the rule does NOT apply

- The user already has a dated eval showing BM25 lost on *this* corpus. Cite it and proceed.
- A client who needs an LPG for operational traversals (fraud, BOM, IAM) is **not** doing GraphRAG — use `choose-graph-or-not`, not this card.

## See also

- [`../knowledge/graphrag-construction.md`](../knowledge/graphrag-construction.md)
- `plugins/memory-engineering/knowledge/memory-engineering-paradigms.md`

## Provenance

House opinion #7. C06, C21.

---

_Last reviewed: 2026-08-14_
