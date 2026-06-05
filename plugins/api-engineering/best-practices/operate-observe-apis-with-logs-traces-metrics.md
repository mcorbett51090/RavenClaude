# Instrument every API with logs, traces, and metrics

**Status:** Absolute rule
**Domain:** API operations / observability
**Applies to:** `api-engineering`

---

## Why this exists

An API without observability is a black box. You cannot distinguish a bug from a load spike, a broken integration from a client error, or a p99 latency regression from a p50 one. The three pillars — structured logs (what happened), distributed traces (where the time went), metrics (how the system is behaving in aggregate) — each answer different operational questions and complement each other. An API that is not observable is not production-ready.

## How to apply

```typescript
// OpenTelemetry — the vendor-neutral standard [verify-at-build]
import { trace, metrics } from '@opentelemetry/api';

const tracer = trace.getTracer('api-service');
const requestCounter = metrics.getMeter('api-service').createCounter('http.server.requests');
const latencyHistogram = metrics.getMeter('api-service').createHistogram('http.server.duration');

app.use((req, res, next) => {
  const span = tracer.startSpan(`${req.method} ${req.route?.path ?? req.path}`);
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;
    requestCounter.add(1, { method: req.method, status: res.statusCode, path: req.route?.path });
    latencyHistogram.record(duration, { method: req.method, path: req.route?.path });
    logger.info({ method: req.method, path: req.path, status: res.statusCode, durationMs: duration });
    span.end();
  });

  next();
});
```

**Do:**
- Emit a structured log line per request: method, path, status, latency, caller identity.
- Propagate `traceparent` (W3C Trace Context) from inbound requests and inject it on all outbound calls.
- Record `p50`, `p95`, `p99` latency histograms and error rates per endpoint.
- Alert on p99 latency breaching SLO and error rate above threshold.
- Tag every metric and log line with the API version and route pattern (not the raw path — avoid high-cardinality).

**Don't:**
- Log raw request bodies that may contain PII or credentials.
- Use the raw URL path as a metric tag — `GET /users/12345` should be `GET /users/{id}`.
- Skip distributed tracing for internal APIs — they are on the critical path of user-facing requests.

## Edge cases / when the rule does NOT apply

Serverless functions that delegate observability entirely to the platform layer (Lambda X-Ray auto-instrumentation) may not need manual span creation — but they still need structured request logs and alerting on error rate.

## See also

- [`../agents/api-platform-engineer.md`](../agents/api-platform-engineer.md) — owns the operate layer including observability setup.
- [`./operate-rate-limit-and-advertise-it.md`](./operate-rate-limit-and-advertise-it.md) — rate limit metrics pair with the error-rate and latency metrics from this rule.

## Provenance

OpenTelemetry specification (opentelemetry.io) and the three-pillars-of-observability framework (logs, traces, metrics). Codifies `api-platform-engineer`'s observability responsibility from CLAUDE.md §1.

---

_Last reviewed: 2026-06-05 by `claude`_
