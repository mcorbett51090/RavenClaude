---
description: "Produce an OpenTelemetry instrumentation plan: OTLP, semantic conventions, key spans/metrics, sampling, cardinality control, pillar correlation."
argument-hint: "[service + stack + what you can't see]"
---

You are running `/observability-sre:instrument-service`. Use `observability-engineer` + the `opentelemetry-instrumentation` skill.

## Steps
1. Identify the key spans and metrics that answer the unanswered questions.
2. Choose head vs tail sampling with the trade.
3. Audit cardinality; move high-cardinality data off metric labels.
4. Wire trace-context correlation across logs/metrics.
5. Emit the instrumentation plan + a question-driven dashboard sketch + Structured Output block.
