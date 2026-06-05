# Pre-warm the cache on deploy, not on first user request

**Status:** Pattern
**Domain:** Caching / latency
**Applies to:** `claude-app-engineering`

---

## Why this exists

Prompt-cache entries expire after 5 minutes of inactivity (ephemeral) or up to
60 minutes (extended, where available `[verify-at-build]`). A new deployment that
serves traffic on a cold cache gives the first batch of real users the full
uncached latency until the static prefix warms. For interactive products this
is a felt regression; for high-traffic apps it means uncached cost on the
highest-volume slice of the day — deploy-time traffic.

## How to apply

After each deployment, issue a synthetic "warm" request that exercises the exact
static prefix the production system prompt uses. The warm request doesn't need a
meaningful answer — just a token in, cache miss acknowledged, cache written.

```python
import anthropic, os

SYSTEM_PROMPT = open("prompts/system.txt").read()

def prewarm_cache(model: str):
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=model,
        max_tokens=1,
        system=[{"type": "text", "text": SYSTEM_PROMPT,
                 "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": "ping"}],
    )
    usage = resp.usage
    print(f"Pre-warm: {usage.cache_creation_input_tokens} tokens written, "
          f"{usage.cache_read_input_tokens} read")

prewarm_cache("claude-sonnet-4-6")
```

Run this as a post-deploy hook (CI/CD pipeline step, health-check endpoint) so
cache is warm before real traffic arrives.

**Do:**
- Use the exact same `cache_control` placement and system-prompt text as
  production — any difference writes to a different cache slot.
- Run pre-warm after every deploy that changes the system prompt.
- Log `cache_creation_input_tokens` vs `cache_read_input_tokens` to verify
  warm success.

**Don't:**
- Pre-warm with a truncated or paraphrased system prompt — the cache key is the
  full token sequence.
- Rely on the first live user request to seed the cache in a latency-sensitive
  product.
- Skip the pre-warm step when only the tool definitions changed — tool defs are
  part of the cache key.

## Edge cases / when the rule does NOT apply

- Batch API jobs: asynchronous by design; first-request cold latency is
  immaterial.
- Very-low-traffic apps (< a few requests per hour): the cache will expire
  between requests anyway; optimise cost rather than latency.

## See also

- [`../agents/claude-app-ops-engineer.md`](../agents/claude-app-ops-engineer.md) — monitors cache hit rate
- [`./cache-the-static-prefix.md`](./cache-the-static-prefix.md) — the canonical caching rule this complements
- [`./cost-and-secrets-observability.md`](./cost-and-secrets-observability.md) — logging cache metrics

## Provenance

Codifies cache-warming guidance from
`knowledge/prompt-caching-playbook.md` (retrieved 2026-05-28) §"Pre-warming".
TTL values are dated — re-verify against the capability map before quoting.

---

_Last reviewed: 2026-06-05 by `claude`_
