---
description: "Decide honestly whether a need requires streaming or batch; if streaming, sketch the topology and delivery semantics."
argument-hint: "[the data need + latency requirement]"
---

You are running `/data-streaming-engineering:decide-streaming-vs-batch`. Use `streaming-architect` + the `streaming-vs-batch` skill.

## Steps
1. Traverse the streaming-vs-batch tree by real latency need.
2. If batch fits, route to data-platform with the reasoning.
3. If streaming, sketch topology + platform + delivery semantics + CDC.
4. Emit (from `templates/streaming-topology.md`) + Structured Output block.
