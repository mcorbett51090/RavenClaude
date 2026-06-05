# Buffer usage events and batch-report to the billing system

**Status:** Pattern
**Domain:** Usage billing / metering
**Applies to:** `fintech-payments-engineering`

---

## Why this exists

A usage-based billing system that makes a billing API call on every discrete
usage event (every API call, every message sent, every compute second) produces
thousands of billing API calls per active customer per day. Billing APIs have
rate limits; high-cardinality event streams overwhelm them, and the cost of the
billing API calls exceeds the value of per-event precision. The correct
architecture is to buffer usage events, aggregate them at a meaningful
granularity (minute, hour, day — depending on billing period), and report in
batches. The billing invoice cares about the total at the period boundary, not
the exact timestamp of each unit.

## How to apply

1. Emit usage events to a lightweight buffer (Redis, Kafka, DynamoDB) — not
   directly to the billing API.
2. An aggregation job (scheduled or streaming) reads from the buffer and
   computes totals at the billing granularity.
3. Report the aggregated total to the billing API (Stripe Meter, Chargebee, etc.
   `[verify-at-use]`) at a cadence that fits within rate limits and billing
   precision requirements.

```python
# Step 1: Emit usage event to Redis (fast, fire-and-forget for the hot path)
redis.incr(f"usage:{customer_id}:{feature}:{hour_bucket}")

# Step 2: Hourly aggregation job
def report_usage():
    now = datetime.utcnow()
    hour_bucket = now.strftime("%Y%m%d%H")
    customers = redis.scan_match(f"usage:*:api_calls:{hour_bucket}")

    for key in customers:
        _, customer_id, feature, _ = key.split(":")
        quantity = int(redis.getdel(key) or 0)
        if quantity == 0:
            continue

        # Report to billing API with idempotency key
        stripe.billing.meter_events.create(
            event_name="api_calls",
            payload={
                "stripe_customer_id": customer_id,
                "value": str(quantity),
            },
            identifier=f"{customer_id}:{feature}:{hour_bucket}",  # idempotency
        )
```

**Do:**
- Choose a buffer granularity (minute/hour) aligned with your billing period
  precision — hourly is typical for daily/monthly billing.
- Use an idempotency key per aggregation bucket so the reporting job is safely
  retryable.
- Monitor buffer depth and aggregation lag as SLIs.

**Don't:**
- Call the billing API on every raw usage event.
- Aggregate at too coarse a granularity (e.g. daily) if your billing period is
  monthly and you need mid-month upgrade/downgrade proration.
- Let the usage buffer grow unbounded without a confirmed report to the billing
  system — events in the buffer are not yet billed.

## Edge cases / when the rule does NOT apply

- Very-low-frequency usage (< 10 events/day/customer): direct reporting per
  event is acceptable; the buffer overhead is not worth it.
- Prepaid unit depletion (customer has a finite bucket of credits): real-time
  decrement is required to enforce the limit; use an atomic counter, not a
  batch report.

## See also

- [`../agents/billing-subscriptions-engineer.md`](../agents/billing-subscriptions-engineer.md) — owns usage metering and billing cycle
- [`./every-money-operation-is-idempotent.md`](./every-money-operation-is-idempotent.md) — the reporting job carries an idempotency key
- [`./subscription-as-a-state-machine.md`](./subscription-as-a-state-machine.md) — usage billing occurs within the subscription lifecycle

## Provenance

Standard usage-based billing architecture practice. The buffer-then-batch
pattern is the recommended approach in Stripe Billing usage records documentation
`[verify-at-use]`. Rate limit management is documented in all major billing
platform APIs.

---

_Last reviewed: 2026-06-05 by `claude`_
