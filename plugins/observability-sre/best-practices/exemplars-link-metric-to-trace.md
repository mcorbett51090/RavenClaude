# Attach exemplars to histograms so metric spikes link to traces

**Status:** Pattern
**Domain:** Observability / metrics
**Applies to:** `observability-sre`

---

## Why this exists

A latency histogram that shows a P99 spike tells you *that* something is slow; it does not tell you *which request* was slow or *where* in the call graph the time was spent. Without exemplars, the investigator's next step is to write a trace query and hope they can correlate by time window — a manual, lossy process. Exemplars embed a trace ID (and optionally labels) directly into the histogram sample at the moment the slow request was observed, turning "spike at 14:32" into a one-click jump to the offending trace.

## How to apply

Exemplars are attached at the instrumentation layer (OpenTelemetry SDK or Prometheus client) and stored by compatible backends (Prometheus with `--enable-feature=exemplar-storage`, Grafana Mimir, Grafana Tempo, Google Cloud Monitoring).

```python
# OpenTelemetry Python: exemplars attach automatically when a span is active
from opentelemetry import metrics, trace

meter = metrics.get_meter("my.service")
request_duration = meter.create_histogram(
    "http.server.request.duration",
    unit="s",
    description="HTTP server request duration",
)

# Inside a request handler — span context is automatically attached as an exemplar
with tracer.start_as_current_span("handle_request") as span:
    with timer:
        result = process(request)
    request_duration.record(
        timer.elapsed,
        attributes={"http.method": request.method, "http.status_code": result.status}
    )
    # The active span's trace_id is automatically added as an exemplar by the SDK
```

```yaml
# Grafana dashboard: enable exemplar display on a histogram panel
panels:
  - type: timeseries
    datasource: Prometheus
    targets:
      - expr: histogram_quantile(0.99, rate(http_server_request_duration_bucket[5m]))
        exemplar: true     # show exemplar scatter plot on the panel
        legendFormat: "P99 latency"
```

**Do:**
- Enable exemplar storage in your metrics backend (Prometheus flag or managed config).
- Instrument histograms with the OTel SDK — it attaches the active span context automatically.
- Configure your dashboard to show exemplars as a scatter plot overlay on latency panels.
- Tail-sample at the collector to keep the traces that exemplars point to (slow + errored traces).

**Don't:**
- Attach user-identifying data (user IDs, session tokens) as exemplar labels — they end up in your metrics backend.
- Expect exemplars on counters — they are only meaningful on histograms (latency, size distributions).
- Configure exemplars without also configuring tail sampling; exemplars pointing to dropped traces are dead links.

## Edge cases / when the rule does NOT apply

If your metrics backend does not support exemplar storage (older Prometheus, some managed offerings), the instrumentation still works correctly — exemplars are silently dropped — so the overhead is zero. Add the backend support when available; the instrumentation is already correct.

## See also

- [`../agents/observability-engineer.md`](../agents/observability-engineer.md) — owns instrumentation and the telemetry pipeline.
- [`./choose-tail-sampling-for-the-rare-and-bad.md`](./choose-tail-sampling-for-the-rare-and-bad.md) — keep the traces that exemplars reference alive with tail sampling.

## Provenance

Codifies the OpenTelemetry exemplar specification and the Prometheus exemplar storage feature (GA in Prometheus 2.27+). Grafana Tempo and Mimir document the end-to-end exemplar workflow.

---

_Last reviewed: 2026-06-05 by `claude`_
