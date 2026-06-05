# Route events through a CDP rather than direct tool integrations

**Status:** Pattern
**Domain:** Product analytics / event routing
**Applies to:** `experimentation-growth-engineering`

---

## Why this exists

A product that sends `track()` calls directly from the app to five analytics
tools (Amplitude, Mixpanel, Hubspot, Intercom, a data warehouse) builds five
parallel integrations that drift apart over time. When the event schema changes,
all five integrations break simultaneously. When a new tool is added, a new
integration is coded from scratch. A Customer Data Platform (Segment, RudderStack,
or equivalent `[verify-at-use]`) acts as the single event bus: the app sends
events once; the CDP fans them out to all destinations. Schema changes and
destination additions happen in the CDP configuration layer, not in app code.

## How to apply

1. **Instrument once** in the app using the CDP SDK (`analytics.track()`,
   `analytics.identify()`, `analytics.page()`).
2. **Configure destinations** in the CDP UI: each tool (Amplitude, warehouse,
   etc.) is a destination that receives a copy of the event stream.
3. **Transform and filter** in the CDP: destination-specific field mappings,
   PII stripping, and sampling rules live in the CDP pipeline, not in app code.

```javascript
// One call, all destinations receive it via the CDP
analytics.track("checkout_initiated", {
  cart_value_cents: 4999,
  item_count: 3,
  currency: "USD",
  experiment_variant: variantId,
});
// CDP routes this to: Amplitude + Warehouse + Hubspot
// Field mapping and PII stripping configured in CDP, not here
```

**Do:**
- Keep app-side calls generic (semantic event names, business-level properties).
- Put tool-specific transformations (field renames, id mapping) in the CDP.
- Version the CDP configuration with the same discipline as code.

**Don't:**
- Import multiple analytics SDKs directly into the app and call them in parallel
  — this recreates the fragmentation problem.
- Rely on the CDP's real-time fan-out for data-warehouse pipelines that need
  guaranteed delivery — use a dedicated event-stream pipeline (Kafka, Kinesis)
  for high-reliability warehouse ingest.
- Let PII flow raw through the CDP without configuring destination-level
  redaction.

## Edge cases / when the rule does NOT apply

- Very early-stage products (< 3 months, < 1 destination): the CDP overhead
  is real and may not be worth it until a second destination is needed.
- Server-side high-throughput event streams (millions/min): a dedicated event
  bus (Kafka) is the better transport; the CDP pattern is designed for product
  telemetry volume, not high-throughput infrastructure events.

## See also

- [`../agents/product-analytics-instrumentation-engineer.md`](../agents/product-analytics-instrumentation-engineer.md) — owns CDP and tracking-plan design
- [`./instrumentation-is-a-designed-schema.md`](./instrumentation-is-a-designed-schema.md) — the schema the CDP fans out must be designed and versioned
- [`./stitch-identity-across-the-login-boundary.md`](./stitch-identity-across-the-login-boundary.md) — `identify()` calls through the CDP handle the identity graph

## Provenance

Standard CDP architecture practice (Segment/RudderStack design documentation
`[verify-at-use]`). The instrument-once pattern is the primary value proposition
of the CDP product category. House opinion #5 from `CLAUDE.md` §2 ("a tracking
plan with consistent naming and types, versioned") is the schema discipline that
this routing pattern enforces.

---

_Last reviewed: 2026-06-05 by `claude`_
