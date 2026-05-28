# Retrieval & RAG with Claude (2026)

**Last reviewed:** 2026-05-28 · **Confidence:** high (Anthropic Contextual Retrieval + cookbook, retrieved 2026-05-28). Re-verify embedding/rerank model names on the Researcher sweep.
**Owner:** `prompt-and-context-engineer` (retrieval design) + `mcp-and-server-tools-engineer` (retrieval-as-a-tool/MCP). Pairs with [`context-engineering-2026.md`](context-engineering-2026.md) (the long-context alternative) and [`prompt-caching-playbook.md`](prompt-caching-playbook.md) (caching the corpus).

## The first decision: do you even need RAG?
```mermaid
flowchart TD
    A[Need Claude to answer over a corpus] --> Q{Corpus size?}
    Q -->|< ~200K tokens (~500 pages), fairly static| LC[Long context + prompt caching<br/>put the whole corpus in the prompt — faster, simpler, often cheaper]
    Q -->|Large / dynamic / per-user / must cite sources| R[Retrieval / RAG]
    R --> F{A handful of known files per request?}
    F -->|Yes| FILES[Files API — upload once, reference by id]
    F -->|No, search a big/growing KB| RAG[Contextual Retrieval pipeline]
```
- **Long context first.** If the knowledge base fits under ~200K tokens and is reasonably static, **skip RAG** — put it in the prompt and cache the prefix (cache read = 0.1× input). Simpler, faster, fewer moving parts.
- **Files API** when it's a known small set of documents per request (upload once, reference by id) — see [`server-side-tools-and-files.md`](server-side-tools-and-files.md).
- **RAG** when the corpus is large, dynamic, per-tenant, or you must surface citations.

## Contextual Retrieval (Anthropic's recipe — the 2026 default for RAG)
Plain chunking loses context (a chunk says "the company" with no idea which). **Contextual Retrieval** fixes it:
1. **Contextual Embeddings** — before embedding each chunk, prepend a short, chunk-specific context blurb (50-100 tokens) that Claude generates explaining the chunk within the whole document. **Generate these cheaply by caching the full document** as the prompt prefix and asking for per-chunk context (Haiku is fine). Embed the contextualized chunk.
2. **Contextual BM25** — index the same contextualized chunks for lexical/exact-term search.
3. **Hybrid + fuse** — run dense (vector) + BM25, fuse with **Reciprocal Rank Fusion (RRF)** — precision on exact terms + recall on semantics.
4. **Rerank** — pass the top-N (e.g. 150) through a reranker (Voyage rerank / Cohere) → keep top-K (e.g. 20).

**Impact (Anthropic):** contextual embeddings + contextual BM25 cut top-20 retrieval failures ~49%; + reranking ~67% (5.7%→1.9%). Contextual embeddings alone give the best perf/cost (one-time ingestion cost; ~92% Pass@10).

## Embeddings + rerank models (dated — verify)
- **Embeddings:** Claude has no first-party embedding model — Anthropic recommends **Voyage AI** (`voyage-3`-family; **`voyage-context-3`** encodes surrounding context at embed time, reducing the need for the manual context step). Cohere + OpenAI embeddings also work. Pick per language/domain/cost; benchmark on your data.
- **Rerankers:** Voyage rerank, Cohere rerank. A rerank step is the single highest-ROI add after hybrid search.

## Production patterns
- **Cite sources** — return chunk → source metadata so the app (and Claude's [citations](https://platform.claude.com/docs/build-with-claude/citations) feature) can attribute answers; treat retrieved content as **untrusted** (injection — see [`tool-use-and-structured-output.md`](tool-use-and-structured-output.md)).
- **Chunking** — semantic/structural boundaries beat fixed-size; overlap modestly; keep chunks 200-800 tokens depending on content.
- **Eval the retriever separately** from the generator (recall@k, MRR) — see [`evals-and-quality.md`](evals-and-quality.md).
- **Retrieval as a tool** — expose search as a Claude tool / MCP server so the agent decides when to retrieve (agentic RAG) vs always-prepend.

## Sources (retrieved 2026-05-28)
[Anthropic — Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval), [Claude cookbook — contextual embeddings](https://platform.claude.com/cookbook/capabilities-contextual-embeddings-guide), [Voyage AI embeddings/rerank], [claude-cookbooks RAG examples](https://github.com/anthropics/claude-cookbooks). Re-verify model names + the 200K long-context threshold on the Researcher sweep.
