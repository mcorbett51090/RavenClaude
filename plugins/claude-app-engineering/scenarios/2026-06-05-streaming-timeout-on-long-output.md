---
scenario_id: 2026-06-05-streaming-timeout-on-long-output
contributed_at: 2026-06-05
plugin: claude-app-engineering
product: streaming
product_version: "unknown"
scope: likely-general
tags: [streaming, timeout, max-tokens, backoff, reliability, sse, 429]
confidence: high
reviewed: false
---

## Problem

A report-generation endpoint that asked Claude for long structured outputs (a multi-section summary, `max_tokens` set high) failed intermittently with read-timeout / connection-dropped errors — and worse, the SDK started **refusing the request outright** with a `ValueError` about a non-streaming request that would exceed the timeout. Under a burst of report requests, a second failure mode appeared: `429`s that the app retried immediately in a tight loop, making the rate-limit worse.

## Constraints context

- Non-streaming `messages.create()` with a large `max_tokens`. The SDK refuses a non-streaming request it estimates will run past ~10 minutes (idle connections drop), raising before the call — this is a guard, not a bug `[verify-at-use]` against the SDK streaming docs.
- The output was genuinely long (well above ~16K tokens), so the per-request wall-clock was the issue, not model latency per token.
- The retry path on `429` was a bare `for attempt in range(3): try: ...` with no delay — immediate re-fire.

## Attempts

- Tried: bumping the client `timeout` higher to suppress the SDK guard. Suppressed the *refusal*, but the underlying long-lived idle connection still dropped mid-response on some requests — you can raise the ceiling but you can't keep a minutes-long idle HTTP connection reliably open. Treating the symptom.
- Tried: lowering `max_tokens` to keep requests short. Truncated legitimate long reports mid-output (a `max_tokens` stop) — wrong tradeoff; the reports are *supposed* to be long.
- Tried (the moves that worked):
  1. **Streamed the request** (`messages.stream()` / `stream=True`) and used `.get_final_message()` / `.finalMessage()` to collect the complete response. Streaming keeps the connection active (tokens flow), so the idle-drop / timeout window never opens, and the SDK's non-streaming guard doesn't apply.
  2. **Replaced the tight retry with exponential backoff + jitter**, honoring the `retry-after` header on `429`, with a capped retry count — and leaned on the SDK's built-in retry (it already backs off on 429/5xx; the custom loop was fighting it).

## Resolution

**For any request that can produce long output (or sets a high `max_tokens`), stream — and never retry a `429` without backoff.** Two reliability rules:

1. **Stream long/high-`max_tokens` work.** Above ~16K output tokens, a non-streaming request risks the SDK HTTP timeout; the SDK may even refuse it. Streaming keeps the connection alive token-by-token, so the timeout window doesn't open, and `.get_final_message()`/`.finalMessage()` still hands you the complete `Message` if you don't want to handle individual events `[verify-at-use]`. The large-output ceilings are model-specific and dated — confirm against the capability map.
2. **Back off on rate limits.** `429`/`overloaded` get exponential backoff **with jitter** and a capped retry count; honor `retry-after`. An immediate retry on `429` deepens the rate-limit hole. The SDK auto-retries 429/5xx with backoff by default — prefer configuring `max_retries` over hand-rolling a loop that fights it (house opinion: 429s get backoff + jitter).
3. **Pin and bound.** Keep `max_tokens` set (don't remove it to "avoid truncation" — that's not the fix; streaming is), and pin the model id.

The trap is that the failure is intermittent and load-dependent — it passes in dev with short outputs and a single request, then shows up as flaky timeouts and a 429 spiral under real report volume.

**Action for the next engineer:** if long-output requests time out or the SDK refuses a non-streaming call, switch to streaming + `get_final_message()` before touching `max_tokens`. If `429`s are climbing, check that the retry path backs off with jitter and honors `retry-after` — an immediate retry is the amplifier.

Cross-reference: complements [`../best-practices/reliability-stream-and-back-off.md`](../best-practices/reliability-stream-and-back-off.md) and the reliability section of [`../knowledge/claude-app-finops-reliability-and-security.md`](../knowledge/claude-app-finops-reliability-and-security.md); the async-delivery (polling vs streaming vs webhook) decision tree is in [`../knowledge/claude-app-decision-trees.md`](../knowledge/claude-app-decision-trees.md). Output ceilings + timeout thresholds are dated — `[verify-at-use]`.
