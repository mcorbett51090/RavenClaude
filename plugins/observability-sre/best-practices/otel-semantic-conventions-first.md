# Use OTel semantic conventions for attribute names before inventing your own

**Status:** Absolute rule
**Domain:** Observability / instrumentation
**Applies to:** `observability-sre`

---

## Why this exists

Every time an engineer invents a custom attribute name (`req_path` vs `http.route` vs `request.url.path`), the telemetry from that service becomes incompatible with dashboards, alert queries, and correlation logic that use the standard name. Multiply across ten services and you get ten different ways to say "HTTP method." OpenTelemetry semantic conventions exist precisely to prevent this: they define standard attribute names for HTTP, databases, messaging, RPC, and more, so that any compliant backend, dashboard, or sampling policy can work across services without per-service customization.

## How to apply

Before adding an attribute to a span, metric, or log, check the OTel semantic conventions registry (opentelemetry.io/docs/specs/semconv/). Use the stable or experimental standard name if one exists. Only invent a custom attribute when the standard doesn't cover the concept; prefix custom attributes with your org or service namespace.

| Domain | Examples of standard attribute names |
|---|---|
| HTTP server | `http.request.method`, `http.response.status_code`, `url.path`, `server.address` |
| Database | `db.system`, `db.name`, `db.operation.name`, `db.query.text` |
| Messaging | `messaging.system`, `messaging.destination.name`, `messaging.operation.type` |
| RPC | `rpc.system`, `rpc.service`, `rpc.method`, `rpc.grpc.status_code` |
| Exceptions | `exception.type`, `exception.message`, `exception.stacktrace` |
| Service resource | `service.name`, `service.version`, `service.namespace` |

```python
# OTel Python: use semantic convention constants instead of string literals
from opentelemetry.semconv.trace import SpanAttributes

with tracer.start_as_current_span("handle request") as span:
    span.set_attribute(SpanAttributes.HTTP_REQUEST_METHOD, request.method)
    span.set_attribute(SpanAttributes.HTTP_RESPONSE_STATUS_CODE, response.status_code)
    span.set_attribute(SpanAttributes.URL_PATH, request.path)
    # Custom attribute: prefix with org namespace
    span.set_attribute("acme.tenant_id", request.tenant_id)
```

**Do:**
- Import semantic convention constants from the `opentelemetry-semantic-conventions` package — don't type the strings manually.
- Set `service.name`, `service.version`, and `service.namespace` as resource attributes on every SDK instance.
- Review the semantic conventions changelog when upgrading OTel — attribute names can be stabilized or renamed.

**Don't:**
- Invent `my_http_method` when `http.request.method` exists.
- Put dynamic/high-cardinality values (request IDs, full URLs with query strings) on metric attributes — use the stable, bounded semantic convention attributes on metrics.
- Block instrumentation because the perfect semantic convention name doesn't exist yet — use a namespaced custom attribute and file an issue with the OTel community.

## Edge cases / when the rule does NOT apply

ML model inference spans have no stable OTel semantic conventions yet (as of mid-2026). Use the experimental `gen_ai.*` attributes where available and add custom namespace attributes for the rest; revisit when the convention stabilizes.

## See also

- [`../agents/observability-engineer.md`](../agents/observability-engineer.md) — owns instrumentation standards and the telemetry pipeline.
- [`./correlate-the-three-pillars.md`](./correlate-the-three-pillars.md) — consistent attribute names are what make cross-pillar correlation work.

## Provenance

Codifies the OpenTelemetry Semantic Conventions specification (opentelemetry.io/docs/specs/semconv/) and the OTel community's stability guidance for attribute naming.

---

_Last reviewed: 2026-06-05 by `claude`_
