# Budget the 1M context window — curate the right tokens, compact the rest

**Status:** Pattern — strong default; dumping the whole corpus/history "just in case" is the anti-pattern.

**Domain:** Prompt + context engineering

**Applies to:** `claude-app-engineering`

---

## Why this exists

A 1M-token window (Opus 4.7, Sonnet 4.6 [verify-at-build]) is not a license to dump everything in. Every token competes for attention; irrelevant or stale context measurably degrades output quality ("context rot") *and* costs money on every uncached request. The two failure modes are symmetric: stuffing a huge dynamic corpus inline when retrieval was the right move, and letting a long-running agent session fill its window with superseded tool-results that no compaction ever prunes. The discipline is to ask, at each step, **"what is the right *set* of tokens in this window, and in what order"** — and to actively shrink history as it goes stale, rather than treating the window as append-only.

## How to apply

Order long static reference material first (cacheable + better recall), the task/question last; compact stale turns; offload durable facts to the memory tool instead of carrying them inline.

```python
# Ordering: long reference FIRST (cacheable), the actual ask LAST.
system = [
    {"type": "text", "text": ROLE_AND_RULES},
    {"type": "text", "text": LONG_REFERENCE_DOC,                    # first → cached + recalled well
     "cache_control": {"type": "ephemeral"}},
]
messages = [
    *compacted_history,        # summarize old turns; DROP superseded tool_results
    {"role": "user", "content": f"<question>{user_ask}</question>"},  # the ask, last
]
# In a raw Messages-API loop YOU own compaction. The Agent SDK manages it for you.
# Rough budget gate before sending:
assert estimate_tokens(system, messages) < BUDGET, "compact or retrieve a slice instead"
```

**Do:**
- Put long reference material **first** (cacheable, better recall); the question **last**; ask Claude to quote the relevant span before answering a long doc.
- **Compact** long agent sessions — summarize old turns, drop superseded tool results — so the window holds *current* signal, not history (mind cache invalidation when you edit above a breakpoint).
- Offload durable facts/state to the **memory tool** (public beta [verify-at-build]) with a redaction pass + eviction policy, instead of carrying them inline every turn.
- Give each sub-agent a **focused slice**, not the whole history — fresh scoped context produces better per-task output and controls cost.

**Don't:**
- Dump the whole conversation/corpus "just in case" — you pay for tokens that dilute attention.
- Let an agent's window accrete stale tool-results across a long session with no compaction — quality and cost both decay.
- Stuff a huge dynamic corpus inline when retrieval is the right move (or run RAG when the corpus fits — see [`rag-skip-it-under-200k.md`](./rag-skip-it-under-200k.md)).

## Edge cases / when the rule does NOT apply

- **Small, static corpus under ~200K tokens** [verify-at-build] — just hold it inline and cache the prefix; the curation overhead isn't worth it. Compaction is for *long-running* or *large* contexts.
- **Short, single-shot calls** — there's no history to compact; the rule targets accumulation over time.
- **Cache-protected prefixes** — don't reorder/edit cached context per request to "optimize" it; that busts the cache (see [`cache-the-static-prefix.md`](./cache-the-static-prefix.md)). Compact *below* the breakpoint.
- The **redaction posture** of anything written to the memory tool is a security concern → `ravenclaude-core/security-reviewer`.

## See also

- [`../knowledge/context-engineering-2026.md`](../knowledge/context-engineering-2026.md) — the levers: caching layout, retrieve-vs-hold, ordering, compaction, the memory tool, sub-agent isolation
- [`./cache-the-static-prefix.md`](./cache-the-static-prefix.md) — caching is the cheapest way to *keep* large context (0.1× read)
- [`./rag-skip-it-under-200k.md`](./rag-skip-it-under-200k.md) — the retrieve-vs-hold boundary
- [`../agents/prompt-and-context-engineer.md`](../agents/prompt-and-context-engineer.md) — owns the context budget

## Provenance

Codifies the context-engineering discipline from [`../CLAUDE.md`](../CLAUDE.md) (the prompt-and-context-engineer's step 2, "budget the context") and the §4 anti-pattern (letting a window fill with stale tool-results). Grounded in [`../knowledge/context-engineering-2026.md`](../knowledge/context-engineering-2026.md) (Anthropic context-management guidance + 1M-context + memory-tool, retrieved 2026-05-28). Window sizes and the ~200K threshold are dated — verify against the capability map.

---

_Last reviewed: 2026-05-30 by `claude`_
