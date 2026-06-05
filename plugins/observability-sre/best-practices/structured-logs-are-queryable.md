# Emit structured logs — free-text is unsearchable at scale

**Status:** Absolute rule
**Domain:** Observability / logging
**Applies to:** `observability-sre`

---

## Why this exists

Free-text log lines are human-readable but machine-hostile. At any meaningful scale, finding all errors for a specific user_id, tracing a request through ten services, or correlating a log entry with its span requires regex-mining a wall of strings — slow, fragile, and impossible to aggregate. Structured logs (JSON or logfmt) emit each field as a named key-value pair that log backends index, filter, and aggregate without custom parsing rules. The trace_id field that links a log to its span only works if it's a first-class field, not a substring.

## How to apply

Configure the logging library to emit JSON (or logfmt for line-oriented systems). Use the OpenTelemetry log semantic conventions for field names so backends recognize them automatically.

```python
# Python with structlog — always emits JSON in production
import structlog
import logging

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),   # structured JSON output
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

log = structlog.get_logger()

# Inject trace context so logs correlate with spans
from opentelemetry import trace
span = trace.get_current_span()
ctx = span.get_span_context()
log.info(
    "order_placed",
    order_id=order.id,
    user_id=user.id,
    amount_cents=order.total_cents,
    trace_id=format(ctx.trace_id, "032x"),
    span_id=format(ctx.span_id, "016x"),
)
```

```go
// Go with slog (stdlib, Go 1.21+)
slog.Info("order placed",
    "order_id", order.ID,
    "user_id", user.ID,
    "amount_cents", order.TotalCents,
    "trace_id", spanCtx.TraceID().String(),
)
```

Required fields on every log entry:
- `timestamp` (ISO 8601)
- `severity` / `level`
- `service.name` and `service.version`
- `trace_id` and `span_id` (when inside a span)
- `message` — a static string; variable data goes in additional fields

**Do:**
- Use a structured logging library (structlog, zap, slog, logrus with JSON formatter).
- Inject trace context automatically using OTel log bridges or middleware.
- Keep the `message` field a static template; never interpolate user data into it.
- Configure your log backend to parse the JSON fields natively (not as a single `message` string).

**Don't:**
- Emit sensitive data (passwords, tokens, PII) as log fields — they land in your log store forever.
- Use `fmt.Printf` or `print` for application logging; they produce unstructured lines.
- Log at DEBUG level in production without a dynamic sampling mechanism — cardinality cost at scale.

## Edge cases / when the rule does NOT apply

Scripts and one-off CLIs aimed at human operators running them interactively may emit human-readable text — they are not services. Add a `--json` flag if the output is ever consumed by another program.

## See also

- [`../agents/observability-engineer.md`](../agents/observability-engineer.md) — owns log instrumentation and the telemetry pipeline.
- [`./correlate-the-three-pillars.md`](./correlate-the-three-pillars.md) — trace_id in structured logs is how logs join to traces.

## Provenance

Codifies the OpenTelemetry log semantic conventions (opentelemetry.io/docs/specs/semconv/general/logs/) and the structured logging best practices from the 12-Factor App methodology (factor XI: Logs as event streams).

---

_Last reviewed: 2026-06-05 by `claude`_
