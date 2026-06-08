---
description: "Set up developer-experience & platform-adoption measurement: pick the framework (DORA/SPACE/DevEx), ship a balanced gaming-resistant metric set, instrument adoption + time-to-prod, and attach a decision to each metric. Never measures individuals."
argument-hint: "[goal, e.g. 'show whether our new golden path is improving time-to-first-deploy']"
---

You are running `/platform-engineering-idp:measure-devex`. Use the `devex-metrics-engineer` discipline
and the `devex-measurement` skill.

## Steps

1. Clarify the decision the measurement must inform.
2. Traverse the metric-framework tree; choose DORA / SPACE dimensions / DevEx as fits the question.
3. Ship a balanced set: 1 delivery + 1 perception + 1 adoption metric, with anti-gaming guardrails.
4. Specify each signal's source (telemetry vs survey) and the adoption funnel (discover -> try ->
   adopt -> retain); name the dashboard shape.
5. Enforce the hard rule: measure the system, never the individual; attach a decision to every metric.
6. Emit the Structured Output block with handoffs (observability-sre for telemetry; platform-product-
   lead to turn the diagnosis into roadmap; applied-statistics for survey/A-B validity).
