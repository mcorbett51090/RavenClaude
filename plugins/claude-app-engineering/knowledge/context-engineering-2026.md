# Context engineering (2026)

**Last reviewed:** 2026-05-28 (**memory-tool status corrected 2026-08-06** — it is GA on the Messages API with no beta header; the rest of the file is unchanged and still carries the 2026-05-28 date) · **Confidence:** medium-high (Anthropic context-management guidance + the 1M-context + memory-tool features; some features dated). 
**Owner:** `prompt-and-context-engineer`. Pairs with [`retrieval-and-rag-2026.md`](retrieval-and-rag-2026.md) (what to retrieve vs hold) and [`prompt-caching-playbook.md`](prompt-caching-playbook.md) (what to cache).

## The shift: from prompt engineering to context engineering
With **1M-token** context (Opus 4.7, Sonnet 4.6), the question is no longer "how do I word the prompt" but **"what is the right *set of tokens* in the window at this step, and in what order."** More context is not better — every token competes for attention; irrelevant or stale context degrades quality ("context rot"). Curate deliberately.

## The levers
1. **Caching layout** — stable, high-value context above the breakpoint (system, tools, long static docs); volatile below. The cheapest way to *keep* large context is to cache it (0.1× read). See [`prompt-caching-playbook.md`](prompt-caching-playbook.md).
2. **Retrieve vs hold** — under ~200K tokens + static → just hold the corpus in context; large/dynamic → retrieve the relevant slice (RAG). The boundary is the first context-engineering decision ([`retrieval-and-rag-2026.md`](retrieval-and-rag-2026.md)).
3. **Order matters** — put long reference material **first** (cacheable + better recall), the actual task/question **last**; ask Claude to quote the relevant span before answering long docs.
4. **Context editing / compaction** — for long-running agent sessions, prune or summarize stale turns/tool-results so the window holds *current* signal, not history. The Agent SDK manages this; in raw Messages-API loops you own it (summarize old turns, drop superseded tool results — but mind cache invalidation).
5. **The memory tool** (**GA on the Messages API — no beta header**; verified 2026-08-06 against the [memory-tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)) — persist durable facts/state *outside* the window and recall on demand, instead of carrying everything inline. It is **client-side**: Claude only *requests* the file operations and your app executes them, so the redaction pass (no secrets/PII), the eviction policy **and** the path-traversal defence are all yours ([`server-side-tools-and-files.md`](server-side-tools-and-files.md); the five distinct memory surfaces are mapped in [memory surfaces (2026)](../../memory-engineering/knowledge/memory-surfaces-2026.md)).
6. **Sub-agent context isolation** — give each sub-agent a *focused* slice, not the whole history (orchestrator-worker — [`agent-orchestration-patterns.md`](agent-orchestration-patterns.md)). Fresh, scoped context produces better per-task output and controls cost.

## Thinking config (dated — keep in the capability map)
- **Adaptive thinking** on Sonnet 4.6 (`thinking: {type: "adaptive"}`; `budget_tokens` deprecated there); extended thinking needs `temperature` unset/1.
- **Thinking blocks consume context + are cached** alongside content (preserved by default on Opus 4.5+/Sonnet 4.6+); keep thinking config stable across turns to protect the cache. Verify exact params in [`model-selection-and-2026-capability-map.md`](model-selection-and-2026-capability-map.md).

## Anti-patterns
- Dumping the whole conversation/corpus "just in case" — pay for tokens that dilute attention.
- Letting an agent's window fill with stale tool-results across a long session (no compaction) → quality + cost decay.
- Re-ordering or mutating cached context per request (busts the cache).
- Using RAG when the corpus fits in context (needless complexity), or stuffing a huge dynamic corpus into context when retrieval is the right move.

## Sources (retrieved 2026-05-28)
Anthropic context-management / long-context guidance, the 1M-context model notes, the [memory-tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) (**GA, no beta header** — retrieved 2026-08-06), and "Building effective agents" (sub-agent context). Re-verify thinking params + memory-tool status on the Researcher sweep — that hedge was correct and went unread for two months; the 2026-08-06 sweep is what retired the beta claim carried here.
