# Instrument the token economics — log usage per request, never log the prompt

**Status:** Absolute rule — you cannot manage a cost or a cache hit rate you don't measure; and `print(messages)` is a secret/PII leak (#8).

**Domain:** FinOps / observability

**Applies to:** `claude-app-engineering`

---

## Why this exists

Every cost lever in this plugin — caching ([`cache-the-static-prefix.md`](./cache-the-static-prefix.md)), the routing ladder ([`right-size-with-a-routing-ladder.md`](./right-size-with-a-routing-ladder.md)), Batch — is invisible until you instrument it. The single most common reason a team "optimizes" the wrong thing is they tuned a high token count they never actually cached, because they never read `usage`. The response carries the whole economic picture per request: `input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`, `stop_reason`. Logging those (and *only* those) gives you the two metrics that matter — **cache hit rate** and **cost-per-resolved-task** — and the latency/throttle signals for reliability. The matching prohibition is non-negotiable and hook-enforced: **never log the full prompt/messages** — they carry user PII and can carry secrets, and `print(messages)` / `logger.info(messages)` ships both to your log sink (#8).

## How to apply

Log structured usage metadata per request — never the message bodies — and dashboard cache hit rate, cost-per-resolved-task, p95 latency, and throttle rate.

```python
resp = client.messages.create(model="claude-sonnet-4-6", max_tokens=1024, ...)
u = resp.usage
log.info("claude_call", extra={                       # METADATA only — never the prompt/messages
    "model": "claude-sonnet-4-6",
    "input_tokens": u.input_tokens,
    "output_tokens": u.output_tokens,
    "cache_read": u.cache_read_input_tokens,           # paid 0.1x — the good number
    "cache_write": u.cache_creation_input_tokens,      # a write happened
    "stop_reason": resp.stop_reason,                   # "max_tokens" here = truncation, alarm on it
    "latency_ms": elapsed_ms, "request_id": resp.id,
})
# Cache hit rate = cache_read / (cache_read + input_tokens). Dashboard it WITH cost-per-resolved-task.
#   keys live in env / secret manager, NEVER as `sk-ant-...` literals in source (#8, hook-flagged).
```

**Do:**
- Log per request: model, `input`/`output`/`cache_read`/`cache_creation` tokens, `stop_reason`, latency, request id — and **derive cost** from them.
- Dashboard **cache hit rate** and **cost-per-resolved-task** together (the cache layout multiplies the routing ladder's savings), plus p95 latency and error/throttle rate.
- **Alarm on `stop_reason == "max_tokens"`** — it's silent truncation, an overspend-and-quality signal; size `max_tokens` to the real output (#11).
- Keep API keys in **env / secret manager**, never a `sk-ant-…` literal in source — the hook flags both this and full-message logging (#8).

**Don't:**
- `print(messages)` / `console.log(messages)` / `logger.*(messages)` — logs the full prompt with PII/secrets; the named anti-pattern (#8), hook-flagged.
- Optimize a raw token count you never confirmed was cached — read `cache_read` first ([`cache-the-static-prefix.md`](./cache-the-static-prefix.md)).
- Track raw token spend as the headline metric — the headline is **cost-per-resolved-task** ([`right-size-with-a-routing-ladder.md`](./right-size-with-a-routing-ladder.md)).

## Edge cases / when the rule does NOT apply

- **Debugging a prompt locally** may need to see message content — do it in a dev-only path behind a flag, redacted, never the production logger; the production rule stands.
- **Required audit trails** of model I/O must go through a **redaction pass** (strip PII/secrets) and a restricted store — not the general application log; the redaction posture escalates to `ravenclaude-core/security-reviewer`.
- **Batch jobs** report usage per request in the results file — instrument them too; offline ≠ unmeasured ([`right-size-with-a-routing-ladder.md`](./right-size-with-a-routing-ladder.md) covers the Batch lever).
- Pricing **multipliers** that turn tokens into dollars are dated — keep them in the capability map, not hard-coded in the logger (#14).

## See also

- [`../knowledge/claude-app-finops-reliability-and-security.md`](../knowledge/claude-app-finops-reliability-and-security.md) — cost levers in priority order, observability, the never-log-prompts rule
- [`../knowledge/prompt-caching-playbook.md`](../knowledge/prompt-caching-playbook.md) — the `usage` fields + cache-hit-rate formula
- [`./cache-the-static-prefix.md`](./cache-the-static-prefix.md) · [`./right-size-with-a-routing-ladder.md`](./right-size-with-a-routing-ladder.md) — the levers this measures
- [`../agents/claude-app-ops-engineer.md`](../agents/claude-app-ops-engineer.md) — owns FinOps + observability

## Provenance

Codifies house opinion #8 (secrets/PII, never log full prompts) and the observability + cost-per-resolved-task discipline from [`../CLAUDE.md`](../CLAUDE.md) §3 and [`../knowledge/claude-app-finops-reliability-and-security.md`](../knowledge/claude-app-finops-reliability-and-security.md). The `usage` fields are grounded in [`../knowledge/prompt-caching-playbook.md`](../knowledge/prompt-caching-playbook.md) (Anthropic prompt-caching docs, retrieved 2026-05-28). The full-message-logging + key-literal checks are hook-enforced ([`../hooks/check-claude-app-anti-patterns.sh`](../hooks/check-claude-app-anti-patterns.sh)).

---

_Last reviewed: 2026-05-30 by `claude`_
