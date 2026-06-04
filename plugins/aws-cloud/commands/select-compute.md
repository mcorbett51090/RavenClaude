---
description: "Choose AWS compute by workload shape and design the event-driven integration with idempotency + DLQs."
argument-hint: "[workload shape + load]"
---

You are running `/aws-cloud:select-compute`. Use `aws-compute-platform-engineer` + the `aws-compute-selection` skill.

## Steps
1. Traverse the compute-selection tree; name the trade.
2. Design the event-driven flow (SQS/SNS/EventBridge/Step Functions) with idempotent consumers + DLQs.
3. Set autoscaling on a load-tracking signal.
4. Emit (from `templates/event-driven-flow.md`) + Structured Output block.
