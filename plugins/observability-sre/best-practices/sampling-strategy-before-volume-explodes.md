# Define the sampling strategy before trace volume makes it a crisis

**Status:** Pattern
**Domain:** Observability / tracing
**Applies to:** `observability-sre`

---

## Why this exists

Tracing every request at 100% is cheap on day one and unaffordable at scale. Teams that defer the sampling decision end up making it under pressure during a cost-reduction sprint — with diminished signal, no time to validate the configuration, and the risk of dropping exactly the traces they needed for the current incident. A well-designed sampling strategy, set before traffic grows, keeps trace cost proportional to insight, not to request volume.

## How to apply

Select a sampling strategy based on traffic volume, trace value, and whether errors/slow requests are rare. The decision tree in `knowledge/observability-sre-decision-trees.md` covers the head vs. tail sampling choice.

| Strategy | When | Cost | Keeps rare/bad? |
|---|---|---|---|
| 100% (no sampling) | Dev/staging, < 1k RPS | High | Yes |
| Probabilistic head sampling | High-volume, uniform interest | Low | No — misses rare errors |
| Rate-limiting | Steady low-volume per service | Low-medium | Sometimes |
| Tail sampling (OTel Collector) | Production, need errored/slow traces | Medium | Yes |
| Parent-based | Distributed system — follow upstream decision | Matches parent | Depends on parent |

```yaml
# OTel Collector: tail sampling — keep errors + slow traces + a 10% baseline
processors:
  tail_sampling:
    decision_wait: 10s
    num_traces: 100000
    expected_new_traces_per_sec: 1000
    policies:
      - name: keep-errors
        type: status_code
        status_code: {status_codes: [ERROR]}
      - name: keep-slow
        type: latency
        latency: {threshold_ms: 1000}
      - name: probabilistic-baseline
        type: probabilistic
        probabilistic: {sampling_percentage: 10}
```

**Do:**
- Instrument at 100% in staging/dev; apply sampling only at the collector in production — this keeps instrumentation portable.
- Use tail sampling (at the collector) for production if you need to keep rare error traces.
- Set the `decision_wait` window long enough to cover your slowest spans before deciding.
- Monitor the collector's `otelcol_processor_tail_sampling_sampling_decision_*` metrics to validate the strategy.

**Don't:**
- Apply head sampling inside the application SDK — you lose the ability to keep error traces after the fact.
- Set sampling rates without measuring the actual trace volume first.
- Tail-sample without ensuring all spans for a trace reach the same collector instance (use a consistent-hash load balancer on trace_id).

## Edge cases / when the rule does NOT apply

Batch/offline inference workloads with very low RPS may be safe at 100% permanently. Re-evaluate whenever you add a new high-volume service or traffic grows 10x.

## See also

- [`../agents/observability-engineer.md`](../agents/observability-engineer.md) — owns the sampling configuration and collector pipeline.
- [`./choose-tail-sampling-for-the-rare-and-bad.md`](./choose-tail-sampling-for-the-rare-and-bad.md) — companion rule on when tail sampling specifically is the right choice.

## Provenance

Codifies the OTel Collector tail sampling processor documentation and the sampling strategy guidance from OpenTelemetry's "Sampling" concept page.

---

_Last reviewed: 2026-06-05 by `claude`_
