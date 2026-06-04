---
name: semantic-metrics-layer
description: "Build a governed semantic/metrics layer: define each metric once as metrics-as-code (dbt Semantic Layer/MetricFlow) with explicit grain and filters, model entities/dimensions to prevent fan-out, and expose one contract every BI tool consumes — ending metric drift."
---

# Semantic / Metrics Layer

## One definition per metric
Revenue, active user, churn, MRR — defined **once** as metrics-as-code, versioned, PR-reviewed. Two dashboards with two 'revenue's = trust gone.

## Explicit grain + filters
A metric needs its **grain** (per what?) and **filters** (which segment?) stated. Otherwise it's uninterpretable.

## Entities & dimensions
Model joins/grains in the layer so consumers can't fan-out or double-count.

## One contract
All BI tools query the same metrics — the semantic layer is the contract, not each tool's hidden calc. Significance -> `applied-statistics`.
