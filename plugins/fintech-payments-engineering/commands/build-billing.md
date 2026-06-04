---
description: "Build subscription/usage billing: plans + proration, idempotent metering, billing cycle, dunning, clean revenue events."
argument-hint: "[pricing model]"
---

You are running `/fintech-payments-engineering:build-billing`. Use `billing-subscriptions-engineer` + the `subscription-billing` skill.

## Steps
1. Model plans + correct proration on mid-cycle changes.
2. Meter usage idempotently; run a reliable recoverable billing cycle.
3. Add dunning (smart retries, comms, grace); emit clean revenue events.
4. Route revenue recognition/GL to finance.
5. Emit + Structured Output block.
