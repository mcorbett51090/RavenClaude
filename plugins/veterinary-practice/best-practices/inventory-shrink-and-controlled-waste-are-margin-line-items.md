# Inventory Shrink and Controlled Waste Are Margin Line Items

**Status:** Pattern
**Domain:** Practice economics / cost management
**Applies to:** `veterinary-practice`

---

## Why this exists

Pharmacy and supply inventory is typically the second or third largest cost category in a veterinary practice, often representing 20–25% of revenue. [unverified — training knowledge] Shrink — unexplained inventory loss from theft, damage, expiry, and unlogged usage — directly erodes this cost line without appearing as a visible budget overrun. Controlled waste — vaccines, injectable medications, and compounded drugs that are opened and not fully used — is an additional margin leak that is rarely tracked. Practices that do not run monthly inventory reconciliation often discover a 3–5% pharmacy-cost variance against expected usage, which at $1M revenue is $30–$50k in unaccounted drug cost. [unverified — training knowledge; verify against your actual cost data]

## How to apply

Build inventory management into monthly financial operations, not just annual stocktaking.

```
Inventory margin protection workflow:
Monthly:
  [ ] Physical count of high-value SKUs (vaccines, injectables, parasite preventives,
      controlled substances, dental consumables)
  [ ] Reconcile physical count vs. expected usage (orders received – logged dispensing)
  [ ] Variance >5% on any SKU → investigate before next order cycle
  [ ] Expiry check: flag items expiring within 90 days for use-up or return

Controlled waste tracking:
  [ ] Log partial-use vials at the time of dispensing: amount used, amount wasted, staff ID
  [ ] Aggregate: monthly controlled-waste cost by drug category
  [ ] Benchmark: actual drug cost % vs. expected drug cost % by service line

Shrink reduction:
  [ ] Lock vaccine refrigerators and high-value drug storage; access log or camera
  [ ] Require two-person sign-off on controlled substance wastage (see controlled-substance rule)
  [ ] Purchase quantities matched to 30–45 day usage; avoid over-stocking that drives expiry waste

Metrics to track:
  - Drug/supply cost as % of revenue: target ~18–22% [unverified — training knowledge]
  - Unexplained inventory variance: target <2% monthly
  - Expiry write-offs: track and report quarterly
```

**Do:**
- Assign a named inventory manager (typically head technician or practice manager) who owns the monthly reconciliation.
- Run the reconciliation against PIMS dispensing records, not against staff memory — logged dispensing data is the source of truth.
- Use the monthly variance data to negotiate purchasing volumes and safety stock levels; over-ordering drives expiry waste.

**Don't:**
- Accept "we're just busy" as an explanation for recurring inventory variance — systematic shrink has a cause (theft, logging gaps, compounding waste) that a pattern will reveal.
- Skip inventory reconciliation when the practice is busy — that is exactly when unlogged usage and diversion risk are highest.
- Treat expiry write-offs as unavoidable cost — they are a purchasing and usage-forecasting failure.

## Edge cases / when the rule does NOT apply

Very small solo-DVM practices with a single-person who manages all inventory may have a lighter monthly process, but the reconciliation principle still applies — the frequency may be every 6 weeks rather than monthly.

## See also

- [`../agents/vet-finance-analyst.md`](../agents/vet-finance-analyst.md) — owns practice P&L including drug/supply cost as a percentage of revenue.
- [`./controlled-substance-compliance-is-non-negotiable-and-audited.md`](./controlled-substance-compliance-is-non-negotiable-and-audited.md) — controlled substance reconciliation is a subset of this rule with its own regulatory requirements.

## Provenance

Standard veterinary practice operations management; grounded in AAHA and VetSuccess practice benchmarking for drug and supply cost as a percentage of revenue; inventory management practice from veterinary practice consulting frameworks.

---

_Last reviewed: 2026-06-05 by `claude`_
