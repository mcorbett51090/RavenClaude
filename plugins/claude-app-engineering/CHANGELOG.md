# Changelog — claude-app-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.0] — 2026-05-28

Knowledge-bank expansion (9 → 13 docs) — a wide-net gap scan surfaced four missing surfaces, each researched and fleshed out:

- `retrieval-and-rag-2026.md` — the RAG-vs-long-context-vs-Files decision (skip RAG under ~200K tokens + caching), Anthropic **Contextual Retrieval** (contextual embeddings + contextual BM25 + RRF + reranking; 49%/67% fewer failed retrievals), Voyage embeddings, chunking, agentic RAG.
- `prompt-engineering-techniques.md` — the quality craft (the leverage ladder: clear+direct → multishot → CoT/thinking → XML → role/system → prefill → chaining), output control, hallucination reduction, the prompt→eval loop. Distinct from the caching (cost) doc and core/prompt-engineer (artifacts).
- `agent-orchestration-patterns.md` — workflows vs agents + the five Anthropic patterns (prompt chaining / routing / parallelization / orchestrator-workers / evaluator-optimizer), Agent Skills as the shared standard, start-simple discipline. RavenClaude is the worked orchestrator-worker example.
- `context-engineering-2026.md` — curating the right tokens in a 1M window: caching layout, retrieve-vs-hold, ordering, context editing/compaction, the memory tool, sub-agent context isolation.

Wired into CLAUDE.md §8. Grounded in Anthropic docs + "Building effective agents" + Contextual Retrieval (retrieved 2026-05-28), dated freshness anchors.

## [0.1.0] — 2026-05-28

Initial release. A Claude app-engineering specialist team built from a researched, expert-reviewed plan (see [`docs/claude-app-engineering-plugin-analysis.md`](../../docs/claude-app-engineering-plugin-analysis.md)).

- **6 agents:** `claude-solution-architect`, `prompt-and-context-engineer`, `mcp-and-server-tools-engineer`, `agent-sdk-engineer`, `eval-engineer`, `claude-app-ops-engineer`.
- **9-doc knowledge bank** (citation-grounded, retrieval-dated 2026-05-28): build-surface decision tree, model-selection + dated 2026 capability map, prompt-caching playbook, tool-use + structured output, MCP server authoring, server-side tools + Files API, Agent SDK + Managed Agents, evals + quality, and FinOps + reliability + security.
- **6 templates:** architecture spec, prompt-and-caching design, MCP server spec, eval plan, cost model, Agent SDK runbook.
- **1 advisory hook** (`check-claude-app-anti-patterns.sh`, `CLAUDE_APP_STRICT=1` to block): hardcoded `sk-ant-` key, `messages.create` with no `max_tokens`, retired model id, full-message logging.
- **14 house opinions.** Seams: prompt-as-artifact → `ravenclaude-core/prompt-engineer`; AI-app security → `ravenclaude-core/security-reviewer`; whole-system architecture → `ravenclaude-core/architect` (a reciprocal prior was added to `core/prompt-engineer.md`).
- Requires `ravenclaude-core@>=0.7.0`. No bundled MCP — documents the Anthropic SDK / Claude Agent SDK prerequisite.

### Built per the round-2 expert review
- Promoted in-app tool-use design into `prompt-and-context-engineer`; made `mcp-and-server-tools-engineer` the MCP + hosted-server-tools owner; added the `server-side-tools-and-files.md` doc; operationalized cache-invalidation churn; made the prompt-engineer seam binding CLAUDE.md text.

### Deferred to a later version
- A `skills/` directory (procedures promoted from `/wrap` feedback) and a `scenarios/` bank (first real engagement scenario).
- Evaluate bundling a Claude/Anthropic MCP server if a stable community one emerges.
