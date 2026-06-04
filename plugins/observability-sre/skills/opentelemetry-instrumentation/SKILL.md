---
name: opentelemetry-instrumentation
description: "Instrument a service with OpenTelemetry: OTLP export, semantic conventions, the key spans and metrics, a sampling strategy (head vs tail), cardinality control, and trace/log correlation via propagated context."
---

# OpenTelemetry Instrumentation

**Purpose:** make a service observable, vendor-neutrally.

## Emit OTLP, route in the collector
App code emits OTLP to a **collector**; the collector routes to the backend. Don't bind app code to a vendor SDK.

## Semantic conventions
Use standard attribute names (`http.route`, `service.name`, `db.system`). Portable + queryable.

## Cardinality
High-cardinality identifiers (user-id, request-id) -> **spans/logs**, never metric labels. A metric label with unbounded values explodes the TSDB.

## Sampling
- **Head** sampling: decide at span start — cheap, blind.
- **Tail** sampling: keep errored/slow traces — pricier, smarter.

## Correlate
Propagate **trace context** so a metric anomaly -> exemplar trace -> request logs.
