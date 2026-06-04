---
name: model-serving
description: "Serve models reliably: choose online vs batch by the use case, deploy a versioned model from the registry, optimize latency to a budget (batching/quantization/distillation/hardware), and roll out safely with shadow -> canary -> full."
---

# Model Serving

## Online vs batch
Real-time per request -> **online endpoint**. Periodic scoring of many records -> **batch**. Don't mismatch.

## From the registry
Deploy a specific **registered version** with known lineage — not a copied file. Promotion goes through the registry gate.

## Latency
Batching, quantization/distillation, right hardware, caching — to a **budget**. Measure.

## Safe rollout
**Shadow** (compare on live traffic, no user impact) -> **canary** (a slice) -> full, promote on the metric. Blind swaps are silent regressions.
