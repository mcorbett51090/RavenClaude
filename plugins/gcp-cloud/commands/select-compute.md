---
description: "Choose GCP compute by workload shape and design the Pub/Sub integration with idempotency + dead-letter topics."
argument-hint: "[workload shape + data needs]"
---

You are running `/gcp-cloud:select-compute`. Use `gcp-data-and-compute-engineer` + the `gcp-compute-selection` skill.

## Steps
1. Traverse the compute-selection tree (Cloud Run default).
2. Choose the data store by access pattern (route deep modeling to database-engineering).
3. Design Pub/Sub flow with idempotent consumers + dead-letter topics.
4. Emit (from `templates/pubsub-flow.md`) + Structured Output block.
