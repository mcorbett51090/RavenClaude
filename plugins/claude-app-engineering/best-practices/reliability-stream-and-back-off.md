# Stream for latency, back off on 429 — the two reliability reflexes

**Status:** Absolute rule — retrying a 429 immediately with no backoff is the named anti-pattern (#9); a blocking non-streamed call is a felt-latency regression for interactive UX.

**Domain:** Reliability / latency

**Applies to:** `claude-app-engineering`

---

## Why this exists

Two reliability defaults separate a production Claude app from a demo. **Latency:** a non-streamed call makes the user wait for the *entire* completion before seeing a token — for any interactive surface that's a felt regression, when **streaming** delivers time-to-first-token in a fraction of the time. **Throttling:** the API returns `429` / `overloaded` under load, and the wrong reflex — retry immediately — makes it worse, hammering an already-saturated endpoint in a tight loop (a self-inflicted outage). House opinion #9 is the right reflex: **exponential backoff + jitter, capped retries, and idempotency for non-idempotent effects**. The jitter matters as much as the backoff — without it, every throttled client retries in lockstep and you get a thundering herd. These are reflexes, not features: build them in once at the client layer and every call inherits them.

## How to apply

Stream interactive responses (handle partial/aborted streams); wrap calls in capped exponential backoff with jitter, and use idempotency keys so a retry can't double-apply an effect.

```python
import random, time
def call_with_backoff(fn, *, max_retries=5, base=0.5, cap=30):
    for attempt in range(max_retries):
        try:
            return fn()
        except (RateLimitError, APIStatusError) as e:        # 429 / 529 overloaded
            if attempt == max_retries - 1:  raise            # capped — don't retry forever
            sleep = min(cap, base * 2 ** attempt) + random.uniform(0, base)  # backoff + JITTER
            time.sleep(sleep)                                # never retry immediately (#9)

# Interactive UX: stream for time-to-first-token; handle partial/aborted streams.
with client.messages.stream(model="claude-sonnet-4-6", max_tokens=1024, messages=msgs) as s:
    for text in s.text_stream:
        emit(text)                                           # render incrementally
# Non-idempotent effect behind a retry? carry an idempotency key so a retry can't double-apply.
```

**Do:**
- **Stream** interactive responses for time-to-first-token; handle partial and aborted streams gracefully.
- On `429` / `overloaded`, **exponential backoff + jitter**, **capped** retries — never retry immediately (#9).
- Carry an **idempotency key** for any non-idempotent effect behind a retry, so a retried call can't double-charge / double-write (composes with [`mcp-author-the-narrow-server.md`](./mcp-author-the-narrow-server.md)).
- Add **timeouts + circuit breakers** around tool execution and downstream calls so one slow dependency doesn't stall the loop.

**Don't:**
- Retry a 429 in a tight immediate loop — the named anti-pattern (#9); you amplify the overload.
- Drop the **jitter** — synchronized retries across clients create a thundering herd that re-throttles everyone.
- Block on a full non-streamed completion for an interactive surface when streaming would cut felt latency.

## Edge cases / when the rule does NOT apply

- **Batch / async (non-interactive)** work doesn't stream and shouldn't pay interactive rates — route it through the Batch API (50% off) instead (#10, [`right-size-with-a-routing-ladder.md`](./right-size-with-a-routing-ladder.md)).
- **The SDKs retry some errors for you** — know which, and own the *budget* and the user-facing degradation on top; don't assume the default covers your idempotency needs.
- **Strictly machine-to-machine** paths may not need streaming (no human waiting) — the backoff reflex still applies.
- **A hard per-tenant quota** (not transient load) won't clear by retrying — surface it; backoff is for transient throttling, not a billing/limit wall.

## See also

- [`../knowledge/claude-app-finops-reliability-and-security.md`](../knowledge/claude-app-finops-reliability-and-security.md) — 429/backoff, streaming, timeouts/circuit breakers, observability
- [`./cost-and-secrets-observability.md`](./cost-and-secrets-observability.md) — the throttle-rate + p95 metrics that tell you backoff is working
- [`./agent-guardrail-the-loop.md`](./agent-guardrail-the-loop.md) — the loop budget that backoff retries live inside
- [`../agents/claude-app-ops-engineer.md`](../agents/claude-app-ops-engineer.md) — owns reliability

## Provenance

Codifies house opinion #9 (429/overloaded → exponential backoff + jitter, capped, idempotency) and the streaming/timeout reliability guidance from [`../CLAUDE.md`](../CLAUDE.md) §3 and [`../knowledge/claude-app-finops-reliability-and-security.md`](../knowledge/claude-app-finops-reliability-and-security.md) (platform docs + established practice, retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
