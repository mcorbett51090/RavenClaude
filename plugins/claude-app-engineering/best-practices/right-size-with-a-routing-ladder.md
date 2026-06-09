# Right-size the model with a routing ladder — measure cost-per-resolved-task

**Status:** Pattern — strong default; defaulting every call to Opus is the anti-pattern.

**Domain:** Model selection / FinOps

**Applies to:** `claude-app-engineering`

---

## Why this exists

Defaulting every request to the most capable model (Opus) is the most common way a Claude app overspends without buying quality. The 2026 lineup is tiered for exactly this: **Haiku 4.5** is cheap/fast/high-volume, **Sonnet 4.6** is the balanced default for most app work (1M context, adaptive thinking), and **Opus 4.8** is reserved for the hard reasoning tail (1M context). House opinion #3 is "right-size with a routing ladder": a cheap model triages or classifies, escalate-on-uncertainty to a stronger model, and reserve the flagship for the genuinely hard cases. The metric that keeps this honest is **cost-per-resolved-task, not raw token count** — a Haiku call that fails and re-routes to Opus is *more* expensive than starting on Sonnet, so the ladder is only a win when you measure end-to-end resolution, not per-call price.

## How to apply

Triage cheap, escalate on a measurable uncertainty signal, and reserve the flagship for the tail. Pin and `max_tokens`-bound every call; track resolution cost, not tokens.

```python
def answer(task):
    # 1. cheap triage / classify
    draft = call("claude-haiku-4-5", task, max_tokens=512)
    if confident(draft):                 # programmatic or self-reported confidence
        return draft
    # 2. escalate on uncertainty to the balanced default
    mid = call("claude-sonnet-4-6", task, max_tokens=1024)
    if confident(mid):
        return mid
    # 3. reserve the flagship for the genuinely hard tail
    return call("claude-opus-4-8", task, max_tokens=2048)
# Dashboard cost-per-RESOLVED-task + cache hit rate, not raw tokens.
```

**Do:**
- Start volume/classification work on **Haiku**; default general app work to **Sonnet 4.6**; reserve **Opus** for the hard tail.
- Define an explicit escalation signal (schema-invalid output, low self-reported confidence, a judge flag) — don't escalate on vibes.
- Pin the model id and always set `max_tokens` (house opinion #11); keep version-specific thinking params in the capability map, not baked into code.
- Default the **eval judge** to Haiku and run eval/backfill batches through the Batch API (50% off, house opinion #10).
- Measure **cost-per-resolved-task** and the cache hit rate together — the cache layout multiplies the ladder's savings.

**Don't:**
- Default every call to Opus "to be safe" — that's the named anti-pattern.
- Optimize raw token count instead of resolution cost — a cheap call that re-routes costs more.
- Hard-code a retired model id (`claude-2`/`claude-instant`/`claude-1`) — the hook flags it; pin a current 4.x model.

## Edge cases / when the rule does NOT apply

- **Uniformly hard workloads** (deep agentic reasoning, code refactors across a large repo) may justify starting on Opus — the ladder's triage step would just add a re-route cost. Right-sizing can land on Opus; it just shouldn't *default* there unmeasured.
- **Strict latency budgets** can rule out a multi-hop ladder; a single right-sized model beats a chain that adds round-trips.
- **Re-baselining on a new model** is a deliberate eval event ([`evals-before-vibes.md`](./evals-before-vibes.md)), not an automatic swap — the platform ships monthly and defaults change.
- The exact model lineup, context sizes, and thinking-param names are **dated** — verify against the capability map before quoting a client (house opinion #14).

## See also

- [`../knowledge/model-selection-and-2026-capability-map.md`](../knowledge/model-selection-and-2026-capability-map.md) — the dated lineup + the routing-ladder discipline (the freshness anchor)
- [`../knowledge/claude-app-finops-reliability-and-security.md`](../knowledge/claude-app-finops-reliability-and-security.md) — the cost levers in priority order (caching → routing → Batch → max_tokens)
- [`./cache-the-static-prefix.md`](./cache-the-static-prefix.md) — the caching lever that multiplies the ladder's savings
- [`../agents/claude-solution-architect.md`](../agents/claude-solution-architect.md) · [`../agents/claude-app-ops-engineer.md`](../agents/claude-app-ops-engineer.md)

## Provenance

Codifies house opinion #3 from [`../CLAUDE.md`](../CLAUDE.md) §3 ("right-size with a routing ladder") and the §4 anti-pattern ("defaulting to Opus; optimizing raw tokens instead of cost-per-resolved-task"). Grounded in the model-selection capability map and the FinOps knowledge file, sourced from the platform release notes/API docs (retrieved 2026-05-28). Model names and statuses are dated — verify before quoting.

---

_Last reviewed: 2026-05-30 by `claude`_
