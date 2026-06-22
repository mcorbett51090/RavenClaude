# Prompt-caching playbook (the #1 cost + latency lever)

**Last reviewed:** 2026-05-28 · **Confidence:** high ([prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), retrieved 2026-05-28). Numeric figures are dated — re-verify on the Researcher sweep.
**Owner:** `prompt-and-context-engineer`.

## The model
Caching reuses a prompt **prefix** across requests. Content up to a `cache_control` breakpoint is cached; subsequent requests with the identical prefix **read** from cache at **0.1× input cost**.

Two ways to set breakpoints:
- **Automatic** (good for conversations): `cache_control` at the request top level — the system places the breakpoint on the last cacheable block and moves it forward as the conversation grows.
- **Explicit** (fine control): `cache_control` on individual blocks, **up to 4 breakpoints total**. On read, the system does a lookback to find the longest matching cached prefix.

## TTL & pricing (Opus 4.7 example, dated 2026-05-28)
| Operation | Multiplier | $/MTok |
|---|---|---|
| Base input | 1× | 5 |
| 5-min cache **write** | 1.25× | 6.25 |
| 1-hour cache **write** | 2× | 10 |
| Cache **read** | **0.1×** | 0.50 |

5-min default: `{"cache_control":{"type":"ephemeral"}}`; 1-hour: add `"ttl":"1h"` (use for async/agentic gaps).

## Minimum cacheable tokens (dated — verify)
Live docs (2026-05-28): **Opus 4.x / Haiku 4.5 = 4,096**; **Sonnet 4.6 = 1,024**; Haiku 3.5 = 2,048. Below the minimum, the request runs **without** caching. Check `usage.cache_creation_input_tokens` / `usage.cache_read_input_tokens` to confirm.

## Cache-miss diagnostics (dated — verify)
The Claude API has a native **cache-diagnostics** beta that names *where* the prefix diverged from the previous request, so you don't have to diff payloads by hand. Pass `diagnostics.previous_message_id` on the request and read `cache_miss_reason` (e.g. `system_changed`, `tools_changed`) off the response. Beta header (2026-06-20): **`cache-diagnosis-2026-04-07`** `[verify-at-use]` ([cache diagnostics](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics), retrieved 2026-06-20). **Claude API only** — not Bedrock/Vertex. Diagnostic fingerprints expire quickly and need closely-spaced same-org requests, so the manual payload-diff (see the [`prompt-caching-audit`](../skills/prompt-caching-audit/SKILL.md) skill) remains the durable fallback.

## The invalidation hierarchy — and the #1 real-world failure mode
Caching follows **tools → system → messages**; a change at one level busts that level **and everything downstream**:
- change a **tool definition** → invalidates *all* caches
- toggle web-search / citations / fast-mode → invalidates system + messages
- change `tool_choice` / add-remove images / change thinking params → invalidates messages

> **House opinion #1 — stable content above the breakpoint, volatile below; never mutate tool defs per request.** The dominant cause of a low hit rate in production is putting per-request content (timestamps, the incoming message, freshly-appended tool results) *above* the breakpoint, or reordering/regenerating tool definitions each call. Lay out: **tools (stable) → system (stable) → long static context (stable) → [BREAKPOINT] → conversation / per-request content (volatile).**

## What can / can't be cached
✅ tool definitions, system blocks, text/image/document blocks in messages, tool_use + tool_result blocks, prior-turn thinking blocks (counted as input on read).
❌ blocks below the minimum, empty text blocks, citations sub-blocks.

## Measure it
On every response check `usage`: `cache_read_input_tokens` (good — paid 0.1×), `cache_creation_input_tokens` (a write happened), `input_tokens` (uncached, after the last breakpoint). **Cache hit rate = cache_read / (cache_read + input)** is the metric to dashboard.

## Pre-warming
Eliminate first-request latency: fire a tiny request with the explicit `cache_control` on the static prefix before users arrive; refresh every ~5 min (5-min TTL) or hourly (1-hour TTL).

## Thinking + caching
On Opus 4.5+/Sonnet 4.6+, prior-turn thinking blocks are preserved by default when non-tool-result content follows, keeping the cache valid. On older models/Haiku, a non-tool-result user turn strips cached thinking and invalidates. Keep thinking config consistent across turns to protect the cache.

> See also [`tool-use-and-structured-output.md`](tool-use-and-structured-output.md) (tool-def stability) and [`model-selection-and-2026-capability-map.md`](model-selection-and-2026-capability-map.md) (dated minimums/multipliers).
