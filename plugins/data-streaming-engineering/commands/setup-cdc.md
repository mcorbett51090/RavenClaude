---
description: "Set up CDC from a database into the stream via Debezium + the transactional outbox, avoiding dual-writes."
argument-hint: "[source DB + target topics]"
---

You are running `/data-streaming-engineering:setup-cdc`. Use `kafka-pipeline-engineer` / `streaming-architect`.

## Steps
1. Design Debezium log-based capture; pair with the transactional outbox (coordinate with backend-engineering).
2. Ensure events match committed state; preserve order per key.
3. Set schema + compatibility for the change events.
4. Emit (from `templates/cdc-outbox.md`) + Structured Output block.
