# Emit structured logs with a correlation ID on every request

**Status:** Absolute rule
**Domain:** Observability
**Applies to:** `backend-engineering`

---

## Why this exists

Unstructured text logs cannot be queried reliably in production; you cannot `filter where latency > 500` on a log line that buries the latency in the middle of a sentence. A correlation ID that flows through every log line, downstream service call, and error report is the only way to reconstruct the full trace of a multi-service request during an incident. Without these two disciplines, debugging in production means guessing.

## How to apply

Emit JSON (or logfmt) logs. Inject the correlation ID at the request entry point (from the `X-Request-ID` / `traceparent` header, or generate one) and carry it through the request context.

```typescript
// Middleware: attach correlation ID to context
app.use((req, res, next) => {
  const correlationId = req.headers['x-request-id'] ?? crypto.randomUUID();
  req.ctx = { correlationId };
  res.setHeader('X-Request-ID', correlationId);
  next();
});

// Structured log entry
logger.info({
  correlationId: req.ctx.correlationId,
  event: 'order.created',
  orderId: order.id,
  durationMs: Date.now() - start,
  userId: req.user.id,
});
```

Forward the correlation ID on every outbound call:

```
headers['X-Request-ID'] = ctx.correlationId;
```

**Do:**
- Use consistent field names across all services: `correlationId`, `durationMs`, `event`, `level`.
- Log at the request boundary (ingress + egress latency) at minimum; add key business events at INFO.
- Include `userId` / `tenantId` on every log line where the caller is known — it triples the debugging speed.
- Propagate the correlation ID to background jobs spawned from the request.

**Don't:**
- Log sensitive PII (passwords, full card numbers, tokens) in any log level.
- Use string interpolation for log messages — `"User " + id + " logged in"` can't be queried.
- Emit a new correlation ID mid-request — one request, one ID.

## Edge cases / when the rule does NOT apply

Batch jobs and scheduled workers are not tied to a single request correlation ID; they should use a `jobRunId` instead. Systems that write logs to a storage backend with a built-in schema (e.g., OpenTelemetry OTLP export) may use their SDK's structured context instead of a hand-rolled approach.

## See also

- [`../agents/backend-reliability-engineer.md`](../agents/backend-reliability-engineer.md) — owns operational observability.
- [`./health-endpoints-for-every-service.md`](./health-endpoints-for-every-service.md) — health endpoints and structured logs are the two minimum observability primitives.

## Provenance

Industry standard: OpenTelemetry trace-context propagation, the twelve-factor app logging factor, and `backend-reliability-engineer`'s observability posture. Structured logging is table stakes for any production backend.

---

_Last reviewed: 2026-06-05 by `claude`_
