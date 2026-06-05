---
scenario_id: 2026-06-05-missing-instrumentation-trace-gap
contributed_at: 2026-06-05
plugin: observability-sre
product: opentelemetry
product_version: "unknown"
scope: likely-general
tags: [opentelemetry, distributed-tracing, context-propagation, trace-gap, instrumentation, latency]
confidence: medium
reviewed: false
---

## Problem

A checkout flow had intermittent 6–9s p99 latency, but the trace waterfall in the APM tool showed the request entering the edge gateway and then... a 7-second gap before the next span appeared in the payment service. "The trace just goes dark in the middle" — the team could see *that* it was slow but had no span covering the slow hop, so they were guessing at which of three services in between was the culprit.

## Constraints context

- Polyglot estate: Node edge gateway (auto-instrumented), a Java orchestration service (auto-instrumented), a Python pricing service (a homegrown HTTP client, **not** auto-instrumented), and a Go payment service (auto-instrumented).
- OpenTelemetry SDKs were installed in three of the four services; the Python pricing service emitted no spans and — critically — did not **propagate** the incoming `traceparent` header to its downstream calls.
- Because the Python service dropped the trace context, every span emitted *after* it started a **new** trace, so the waterfall showed two disconnected traces that looked like a single 7s gap.
- The team assumed "the gap = the slow service," i.e. that the missing-span service was the bottleneck. It wasn't necessarily — a gap is an *instrumentation* hole, not evidence of where the time went.

## Attempts

- Tried: adding more logging to the orchestration service (the span *before* the gap), hoping to catch the slow call. Confirmed the orchestration service handed off quickly — the slowness was downstream of it — but logs aren't correlated by trace context, so stitching them to the right request across services was manual and error-prone.
- Tried: assuming the un-instrumented Python pricing service was the culprit and starting to optimize its queries. Premature — there was no span proving the time was spent *there* vs. in the call it made onward to payment.
- Tried (the move that worked): instrumented the Python pricing service with the OTel SDK **and**, the load-bearing part, fixed **context propagation** — inject the `traceparent` header on its outbound calls and extract it on its inbound. The two disconnected traces merged into one continuous waterfall, which immediately showed the 7s was actually spent in a **retry loop the pricing service ran against a degraded payment dependency** — not in pricing's own logic at all.

## Resolution

**A trace gap is a missing-instrumentation signal, not a "the slow service is the dark one" signal — and the fix is usually context *propagation*, not just adding spans.** The recipe:

1. **A gap means the trace context was dropped.** When a waterfall goes dark and resumes as a *new* trace id, some service in the path didn't propagate `traceparent` (W3C Trace Context). The missing spans aren't proof of where the time went — they're proof you can't see it yet.
2. **Instrument the dark service AND propagate context.** Adding spans without propagating the incoming context just creates more disconnected traces. The SDK has to **extract** the context on inbound and **inject** it on outbound; auto-instrumentation usually does both, a homegrown HTTP client usually does neither.
3. **Use OTel semantic conventions** for the new spans (HTTP, DB attributes) so they're queryable alongside the auto-instrumented ones, not a bespoke shape.
4. **Only then read the waterfall.** With the trace continuous, the real bottleneck (here: a retry storm against a degraded dependency) is visible — and it was *not* the service that had been dark.

The p99 fix turned out to be bounding the pricing service's retries (timeout + capped backoff) against the degraded payment dependency — a conclusion that was invisible until the trace was whole. Optimizing the pricing service's own code, the team's first guess, would have moved nothing.

**Action for the next engineer:** when a trace "goes dark in the middle," do not assume the dark service is slow. Find the service that dropped the trace context, instrument it *and* fix propagation so the waterfall reconnects, and only then diagnose where the time actually went. The gap is an observability hole, not a verdict.

Cross-reference: [`../knowledge/observability-sre-decision-trees.md`](../knowledge/observability-sre-decision-trees.md) `## Decision Tree: Logs, metrics, or traces — which pillar for this question?`. This is the field-note complement to best-practices `otel-semantic-conventions-first.md`, `correlate-the-three-pillars.md`, and `exemplars-link-metric-to-trace.md`. Instrumentation is `observability-engineer`'s lane; the bounded-retry fix itself is `backend-engineering/backend-reliability-engineer`'s.

**Sources for the cited pattern:** W3C Trace Context (the `traceparent` propagation format) — https://www.w3.org/TR/trace-context/ ; OpenTelemetry context propagation docs — https://opentelemetry.io/docs/concepts/context-propagation/ (retrieved 2026-06-05). Latency figures are illustrative for this engagement; validate against the team's own traces before a deliverable.
