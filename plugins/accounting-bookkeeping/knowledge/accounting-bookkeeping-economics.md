# Accounting & Bookkeeping Practice Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/acctgops_calc.py`](../scripts/acctgops_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. The close is a critical path (§3 #1)

```
days_to_close   = sum(durations along the longest dependent task chain)
bottleneck      = the task on the critical path with the largest duration
```

Adding people to non-critical-path tasks doesn't shorten the close; removing or parallelizing the bottleneck does. And reconciliation gates the close — the books can't close on accounts that don't tie (§3 #1 #2).

## 2. The cash conversion cycle frames the cash crunch (§3 #3 #4)

```
DSO = AR / revenue * days
DPO = AP / COGS    * days
DIO = inventory / COGS * days
cash_conversion_cycle = DSO + DIO - DPO
```

A business profitable on accrual can be cash-starved because revenue is booked (DSO high) before it's collected; AP timing (DPO) is the offsetting lever. State the basis or the numbers mislead (§3 #6).

## 3. Bad-debt is weighted by aging (§3 #3)

```
bad_debt_estimate = sum(bucket_balance * bucket_loss_rate for bucket in aging)
```

A dollar in the 90+ bucket is worth far less than a dollar in the current bucket; the aging-weighted estimate is more honest than a flat percentage of AR (§3 #3).

## 4. Controls are cheap insurance (§3 #5)

```
control_gap = same_person(approve, enter, reconcile)   # the classic fraud/error vector
```

Segregation of duties, approval thresholds, and independent reconciliation catch both fraud and honest error; a small practice substitutes compensating controls, not no controls (§3 #5).
