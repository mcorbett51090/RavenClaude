---
description: "Lay out a Claude prompt for a high cache-hit rate — stable content (tools, system, static context) above the cache_control breakpoint, volatile content (timestamps, the incoming message, fresh tool results) below, tool defs never mutated per request."
argument-hint: "[the app/prompt, e.g. 'our chat endpoint paying full input cost every call']"
---

# Add prompt caching

You are running `/claude-app-engineering:add-prompt-caching`. Restructure the prompt for the app the user described (`$ARGUMENTS`) so the cacheable prefix is stable and the per-request content sits below the breakpoint — the highest-leverage cost/latency lever on the Claude API, owned by the `prompt-and-context-engineer` and `claude-app-ops-engineer` agents. A cache read is `0.1×` input cost.

## When to use this

An app makes repeated Claude calls that share a large stable prefix (a system prompt, tool definitions, a static knowledge block) and you want to cut input spend/latency. NOT for one-off single calls with no shared prefix.

## Steps

1. **Separate stable from volatile content** (`cache-the-static-prefix.md`): everything reused across requests (tool definitions, system prompt, static context) goes *above* the `cache_control` breakpoint; everything per-request (a timestamp, the incoming user message, freshly-appended tool results) goes *below* it.
2. **Never mutate or reorder tool definitions per request** (`cache-the-static-prefix.md`): regenerating or reordering the tool array each call is the #1 cache-hit-rate killer — define tools once, statically.
3. **Place the breakpoint respecting invalidation order** (`cache-the-static-prefix.md`): invalidation cascades **tools → system → messages**, so a change at one level busts that level and everything downstream — keep the most stable content highest.
4. **Audit for per-request content that leaked above the breakpoint** (`cache-the-static-prefix.md`): a timestamp or a freshly-appended result sitting in the static prefix busts the cache on every request and the team pays full `1×` input forever — the dominant production cause of a low hit rate.
5. **Coordinate with context budgeting** (`context-budget-the-1m-window.md`): a stable, curated context block caches well; an append-only growing history doesn't — compact stale history below the breakpoint rather than letting it bloat the cached prefix.
6. **Verify the hit rate** (`cost-and-secrets-observability.md`): instrument `cache_read_input_tokens` vs `cache_creation_input_tokens` so the win is a measured number, not an assumption.

## Guardrails

- Mutating tool definitions per request silently busts the cache on every call — treat the tool array as static.
- A single per-request token above the breakpoint defeats the whole prefix — audit for stray timestamps/IDs/fresh results.
- Re-tuning a tool description re-busts the cache; pair caching work with the eval harness so description changes are deliberate, not incidental.
