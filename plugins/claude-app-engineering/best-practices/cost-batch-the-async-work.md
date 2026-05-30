# Batch the async work — don't pay interactive rates for offline jobs

**Status:** Pattern — strong default; running evals, backfills, or bulk enrichment at interactive rates is the named anti-pattern (#10).

**Domain:** FinOps

**Applies to:** `claude-app-engineering`

---

## Why this exists

A large fraction of a Claude app's token spend is *not* latency-sensitive: nightly evals, historical backfills, bulk document enrichment, dataset labelling, the LLM-judge passes in your eval harness. Running that work through the interactive Messages API pays full price for a property nobody needs — sub-second latency on a job that can wait. The **Batch API is 50% off** with a roughly-24-hour async SLA [verify-at-build], and the `output-300k-2026-03-24` beta header raises batch `max_tokens` to 300k on the larger models [verify-at-build]. House opinion #10 is the simple discipline: **any workload with no human waiting on it belongs on Batch.** It's the third cost lever after caching and the routing ladder, and it's the one most often left on the table because the offline jobs were built on the same client path as the interactive ones.

## How to apply

Route any non-interactive workload — evals, backfills, bulk enrichment, the judge passes — through the Batch API; reserve the interactive path for human-waiting requests.

```python
# Offline / no human waiting -> Batch (50% off, ~24h SLA). Submit many requests as one batch.
batch = client.messages.batches.create(requests=[
    {"custom_id": f"case-{c.id}",
     "params": {"model": "claude-haiku-4-5", "max_tokens": 512,   # judge defaults to Haiku
                "messages": c.messages}}
    for c in golden_set                                            # eval = the canonical Batch job
])
# Poll/await results; each result carries its own usage -> instrument it too (cost-and-secrets-observability).
# Interactive path (human waiting) stays on messages.create with streaming + backoff.
```

**Do:**
- Route **evals, backfills, bulk enrichment, dataset labelling, and the LLM-judge passes** through the **Batch API** (50% off, ~24h async) — the canonical offline jobs (#10).
- Default the **eval judge to Haiku** and run the judge batch through Batch — compounding the cheapest-judge and the Batch discount ([`evals-before-vibes.md`](./evals-before-vibes.md)).
- Instrument Batch jobs too — each result carries `usage`; offline is not unmeasured ([`cost-and-secrets-observability.md`](./cost-and-secrets-observability.md)).
- Verify the **Batch limits and the `output-300k` beta header string** before relying on raised `max_tokens` — both are dated ([verify-at-build]).

**Don't:**
- Run evals / backfills / bulk jobs at **interactive rates** when they could wait — the named anti-pattern (#10); you pay double for latency nobody needs.
- Put **human-waiting** requests on Batch — the ~24h SLA is a non-starter for interactive UX (stream those instead, [`reliability-stream-and-back-off.md`](./reliability-stream-and-back-off.md)).
- Quote the 50% discount, the SLA, or the 300k header as fixed — they're dated; verify against the capability map (#14).

## Edge cases / when the rule does NOT apply

- **Latency-sensitive** work (anything a human is waiting on) stays interactive — Batch's async SLA disqualifies it.
- **Real-time pipelines** (streaming ingestion that must keep up) aren't "async" in the batchable sense even if unattended — they have a latency budget.
- **Tiny one-off** jobs may not be worth the batch-submission overhead — the discount matters at volume.
- Batch composes with the other levers but doesn't replace them — **caching first, routing ladder second, Batch third** is the priority order ([`../knowledge/claude-app-finops-reliability-and-security.md`](../knowledge/claude-app-finops-reliability-and-security.md)).

## See also

- [`../knowledge/claude-app-finops-reliability-and-security.md`](../knowledge/claude-app-finops-reliability-and-security.md) — cost levers in priority order (caching → routing → Batch → max_tokens)
- [`./right-size-with-a-routing-ladder.md`](./right-size-with-a-routing-ladder.md) — the routing lever Batch compounds with
- [`./evals-before-vibes.md`](./evals-before-vibes.md) — the judge passes that are the canonical Batch workload
- [`../agents/claude-app-ops-engineer.md`](../agents/claude-app-ops-engineer.md) — owns FinOps

## Provenance

Codifies house opinion #10 from [`../CLAUDE.md`](../CLAUDE.md) §3 ("batch the async") and the §4 anti-pattern ("running evals/backfills/bulk jobs at interactive rates instead of Batch"). Grounded in [`../knowledge/claude-app-finops-reliability-and-security.md`](../knowledge/claude-app-finops-reliability-and-security.md) (Batch API: 50% off, ~24h, `output-300k-2026-03-24` beta header — platform docs, retrieved 2026-05-28). Discount, SLA, and header string are dated — verify against [`../knowledge/model-selection-and-2026-capability-map.md`](../knowledge/model-selection-and-2026-capability-map.md).

---

_Last reviewed: 2026-05-30 by `claude`_
