---
name: prompt-caching-audit
description: "Step-by-step playbook for diagnosing a low cache hit rate, finding the breakpoint placement errors that cause it, and correcting them. Covers TTL tradeoffs, pre-warming, tool-definition stability, and the per-model minimum-token floors."
---

# Prompt Caching Audit

## When to invoke

- Cache hit rate is below 80 % on a workload with stable system prompts.
- Cost spiked after a feature change — suspect a busted breakpoint.
- A new endpoint is being designed and caching is not yet specified.

## Step 1 — Read the hit-rate signal

Retrieve `cache_creation_input_tokens` and `cache_read_input_tokens` from the API response `usage` block (not the dashboard — the dashboard is delayed).

| Metric | Formula | Target |
|---|---|---|
| Hit rate | `cache_read / (cache_read + cache_creation)` | ≥ 80 % |
| Cache savings | `(cache_read × 0.1 × price) / total_cost` | visible on routing ladder |
| Effective input cost | `(cache_creation × 1.25 + cache_read × 0.1 + non-cached × 1.0) × base_price` | compare to non-cached baseline |

If `cache_creation` equals `cache_read + cache_creation` (ratio ≈ 1.0), **nothing is being read from cache** — the breakpoint is broken or content is mutating every call.

## Step 2 — Locate the breakpoint regression

> **First, if you're on the Claude API:** the native **cache-diagnostics** beta reports the first prefix divergence directly via `cache_miss_reason` (pass `diagnostics.previous_message_id`) — see [`../../knowledge/prompt-caching-playbook.md`](../../knowledge/prompt-caching-playbook.md) for the current beta header `[verify-at-use]`. It is Claude-API-only (not Bedrock/Vertex); the manual checks below are the fallback — and the durable check, since diagnostic fingerprints expire quickly.

Work through each cause in order:

1. **Tool definitions mutating per request.** Dump two consecutive raw `messages.create` payloads and diff the `tools` array. Any field change (description rewrite, schema property reorder, dynamic example injection) invalidates the cache block containing tools. Fix: build the tools array once at startup and freeze it.

2. **Breakpoint placed below volatile content.** The `cache_control: {"type": "ephemeral"}` marker must sit at the boundary where stable prefix ends and per-request content begins. A breakpoint anywhere inside the per-request turn caches nothing useful. Fix: move the marker to the last stable block (usually the end of the system prompt, or the end of the few-shot examples).

3. **Content below the per-model minimum.** Each model has a minimum cacheable-block size; below it the block is silently not cached. The floors are model-specific and dated — **don't hardcode them here; read the current values from [`../../knowledge/prompt-caching-playbook.md`](../../knowledge/prompt-caching-playbook.md) §"Minimum cacheable tokens" (the dated source of truth)** `[verify-at-use]`. Fix: measure `cache_creation_input_tokens` — if it never appears, the block is under that model's floor.

4. **Multiple breakpoints competing.** Up to four `cache_control` blocks are honoured per request. If an agent is setting a new marker on every retrieved document chunk, the oldest blocks get evicted. Fix: pin the stable prefix with one breakpoint; use a second only for a large but infrequently-changed context section (e.g., a reference doc).

5. **TTL mismatch.** Default TTL is 5 minutes. A workload with >5 min inter-call gaps gets no reuse benefit. Fix: use the extended TTL tier (1 hour, 2× creation surcharge) if inter-call gaps are long but content is genuinely stable.

## Step 3 — Verify the fix

After deploying the corrected breakpoint placement:

```python
resp = client.messages.create(...)
u = resp.usage
print(f"hit={u.cache_read_input_tokens}  miss={u.cache_creation_input_tokens}  "
      f"rate={u.cache_read_input_tokens/(u.cache_read_input_tokens+u.cache_creation_input_tokens+1):.1%}")
```

Run 10 consecutive identical-prefix calls. Hit rate should climb to ≥ 80 % by call 3 (after the initial creation). If still 0 %, re-examine whether the payload truly matches the earlier call byte-for-byte (serialize tools + system to a hash and compare).

## Pre-warming checklist (new deployments)

- [ ] Send one warm-up call at server startup before the first real user request arrives.
- [ ] Confirm system prompt + tools clear the model's minimum cacheable-block size before marking the breakpoint (the dated per-model floors live in [`../../knowledge/prompt-caching-playbook.md`](../../knowledge/prompt-caching-playbook.md) `[verify-at-use]`).
- [ ] Confirm tool schema is frozen in a module-level constant — not rebuilt per-request.
- [ ] Log `cache_creation_input_tokens` on the first call and `cache_read_input_tokens` on subsequent ones; alert if read drops to zero mid-session.

## Pitfalls

- Placing `cache_control` on a user message block — caching is for the prefix *above* the current turn, not inside it.
- Assuming the SDK's `messages.create` helper rebuilds the tools list — it passes through whatever Python/TS object you give it; the freeze is your responsibility.
- Treating a 70 % hit rate on a new endpoint as "good" when it's really a warmup artefact — measure over a 1 h window, not the first 10 calls.
- Using extended TTL for content that actually changes every few minutes (you pay the 2× creation surcharge for no reuse gain).
