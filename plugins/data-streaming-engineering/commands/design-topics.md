---
description: "Design topics and partitioning keyed for required ordering, with schema-registry governance and retention by purpose."
argument-hint: "[data + ordering/throughput needs]"
---

You are running `/data-streaming-engineering:design-topics`. Use `kafka-pipeline-engineer` + the `kafka-platform` skill.

## Steps
1. Choose the partition key for required ordering; set partition count for throughput.
2. Register schemas with compatibility rules; plan additive evolution.
3. Set retention/compaction by consumption purpose.
4. Emit (from `templates/topic-design.md`) + Structured Output block.
