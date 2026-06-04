---
name: subscription-billing
description: "Build subscription/usage billing: model plans and prorate mid-cycle changes correctly, meter usage idempotently, run a reliable recoverable billing-cycle job, recover failed payments with smart dunning, and emit clean revenue events for finance."
---

# Subscription Billing

## Plans + proration
Flat/tiered/per-seat/usage. Mid-cycle change -> **prorate** (credit unused, charge new). Proration bugs are the #1 billing complaint.

## Usage metering
Record usage events **idempotently** (dedup key); aggregate for the invoice. Double-count = overcharge dispute; lost = revenue loss.

## Billing cycle
Reliable, **recoverable**, idempotent job: invoice -> charge -> handle result.

## Dunning + events
Smart retries (soft declines) + comms + grace, not churn-inducing. Emit clean **revenue events** -> `finance` for ASC 606.
