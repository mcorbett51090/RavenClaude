---
name: implement-metered-billing
description: "Implement usage-based / metered billing correctly — idempotent usage recording, aggregation & rating to billable quantities, on-time usage reporting before invoice close, and counted-vs-billed reconciliation. Use when billing on API calls, seats used, GB, events, or any consumption metric."
---

# Skill: Implement Metered Billing

Usage-based billing is a **metering problem before it is a billing problem**. Revenue is silently lost when usage is under-counted and clawed back when over-counted. This skill builds the counting → rating → reporting → reconciliation path so billed usage equals real usage.

## When to use

- Billing on consumption (API calls, compute, storage, messages, events) or metered seats.
- Adding overage to a base plan (hybrid model).
- Diagnosing a discrepancy between what you counted and what the provider invoiced.

## Steps

1. **Define the meter precisely.** What single unit is billable, at what granularity, with what rounding, over what window (aligned to the billing period)? Ambiguity here becomes a billing dispute.
2. **Record usage idempotently.** Every usage event carries a stable, caller-supplied event key; dedupe on it so retries/at-least-once producers can't double-count. Store raw events before aggregation so you can re-derive.
3. **Aggregate and rate.** Roll raw events to billable quantity per subscription per period; apply the rating rules (tiers, included allowance, overage price). Keep aggregation deterministic and replayable from raw events.
4. **Report before invoice close.** Push usage to the provider (or generate the invoice line) before the billing period closes, respecting the provider's cutoff. Late usage either misses the invoice or triggers a correction — decide which on purpose.
5. **Reconcile counted-vs-billed.** A scheduled job compares your aggregated quantity to what the provider billed and alerts on drift. This is the safety net that catches dropped or duplicated usage. See [`../../knowledge/webhooks-idempotency-and-revrec.md`](../../knowledge/webhooks-idempotency-and-revrec.md).
6. **Handle backfills and corrections explicitly.** When late/corrected usage arrives after close, apply it as an adjustment on the next invoice, not a silent mutation of a closed period.

## Anti-patterns

- Recording usage without an idempotency key, so a producer retry double-bills.
- Aggregating destructively (no raw events) so you can't re-derive or reconcile.
- Reporting usage after the provider's cutoff and losing it silently.
- No counted-vs-billed reconciliation — drift is invisible until a customer disputes.
- Mutating a closed billing period instead of issuing an adjustment.

## Output

A metering implementation: meter definition → idempotent recording → deterministic aggregation/rating → on-time reporting → reconciliation job + drift alert → backfill/correction policy. Prove it with duplicate- and out-of-order-delivery fixtures.
