# Cache the static prefix — stable above the breakpoint, volatile below

**Status:** Absolute rule — never mutate tool definitions per request; it is the #1 cache-hit-rate killer.

**Domain:** Prompt + context engineering / FinOps

**Applies to:** `claude-app-engineering`

---

## Why this exists

Prompt caching is the single biggest cost and latency lever on the Claude API: a cache **read** is `0.1×` input cost, so a well-laid-out static prefix can cut input spend by an order of magnitude. Caching reuses a prompt **prefix** up to a `cache_control` breakpoint, and invalidation follows **tools → system → messages** — a change at one level busts that level and everything downstream. The dominant cause of a low hit rate in production is structural, not subtle: per-request content (a timestamp, the incoming message, freshly-appended tool results) placed *above* the breakpoint, or tool definitions regenerated/reordered each call. Both bust the cache on every request, and the team pays full `1×` input forever. House opinion #1 makes the layout non-negotiable: stable content above the breakpoint, volatile below, tool defs never mutated per request.

## How to apply

Lay the prompt out so the expensive, stable bytes sit above one breakpoint and only per-request content changes below it. Then dashboard the hit rate from `usage`.

```python
# tools (stable) -> system (stable) -> long static context (stable)
#   [ cache_control breakpoint ] -> conversation / per-request content (volatile)
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,                      # always set max_tokens (house opinion #11)
    tools=TOOLS,                          # identical object every call — never rebuilt per request
    system=[
        {"type": "text", "text": STATIC_SYSTEM},
        {"type": "text", "text": LONG_STATIC_CONTEXT,
         "cache_control": {"type": "ephemeral"}},   # breakpoint AFTER the stable prefix
    ],
    messages=conversation,                # volatile — lives below the breakpoint
)
# Hit rate = cache_read_input_tokens / (cache_read_input_tokens + input_tokens)
u = response.usage  # watch cache_read_input_tokens vs input_tokens
```

**Do:**
- Order `tools → system → long static docs → [BREAKPOINT] → conversation / per-request content`.
- Build tool definitions **once** and pass the same object every call; keep `tool_choice` and thinking config stable across turns.
- Use the 1-hour TTL (`"ttl":"1h"`) for async/agentic gaps; pre-warm the static prefix before users arrive.
- Confirm you cleared the minimum cacheable tokens (Sonnet 4.6 = 1,024; Opus 4.x / Haiku 4.5 = 4,096) — below it the request runs *uncached*.

**Don't:**
- Put a timestamp, the incoming user message, or a just-appended tool result above the breakpoint.
- Regenerate or reorder tool definitions per request, or toggle web-search/citations mid-session — each busts the cache.
- Optimize a "high token count" you never actually cached — measure `cache_read` first.

## Edge cases / when the rule does NOT apply

- **No reused prefix** — a one-shot call with a unique prompt and no repeated context has nothing to cache; caching adds a write cost (`1.25×`/`2×`) for no read benefit. Skip it.
- **Sub-minimum prefixes** — content below the model's minimum cacheable tokens won't cache regardless of layout; consolidate or accept uncached.
- **Genuinely volatile tools** — if a tool set legitimately changes per request, accept the lower hit rate, but isolate the stable tools above their own breakpoint so they still cache.
- The **redaction / injection** posture of cached tool results is a security concern → `ravenclaude-core/security-reviewer`.

## See also

- [`../knowledge/prompt-caching-playbook.md`](../knowledge/prompt-caching-playbook.md) — breakpoints, TTL, pricing, minimums, the invalidation hierarchy, pre-warming
- [`../knowledge/context-engineering-2026.md`](../knowledge/context-engineering-2026.md) — caching layout as a context lever in the 1M window
- [`../knowledge/model-selection-and-2026-capability-map.md`](../knowledge/model-selection-and-2026-capability-map.md) — the dated minimums and multipliers
- [`../agents/prompt-and-context-engineer.md`](../agents/prompt-and-context-engineer.md) — owns the caching strategy

## Provenance

Codifies house opinion #1 from [`../CLAUDE.md`](../CLAUDE.md) §3 ("cache the static prefix") and the matching anti-pattern (§4). Grounded in the prompt-caching playbook, sourced from the platform prompt-caching docs (retrieved 2026-05-28). Numeric figures (multipliers, minimums) are dated and live in the capability map — verify before quoting a client.

---

_Last reviewed: 2026-05-30 by `claude`_
