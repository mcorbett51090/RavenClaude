# FinOps & Cloud Cost Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/finops_cloud_cost_calc.py`](../scripts/finops_cloud_cost_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. Allocation precedes optimization (§3 #1)

```
allocation_coverage = tagged_spend / total_spend
ungoverned_pile     = total_spend - tagged_spend
```

You cannot hold a team accountable for spend they can't see; below a usable coverage threshold, every optimization is a guess about an unattributed pile.

## 2. Unit economics tell the scaling story (§3 #2)

```
cost_per_unit = allocated_cost / units
trend         = cost_per_unit(now) - cost_per_unit(prior)
```

A rising total bill with a falling cost-per-unit is success; a flat bill with a rising cost-per-unit is decay. The sum hides both.

## 3. Rightsize THEN commit (§3 #4 #5)

```
lean_baseline      = current_baseline - waste - oversize_reduction
commitment_savings = lean_baseline * coverage * discount
```

Committing against `current_baseline` instead of `lean_baseline` locks in waste for the 1-3 year term — the most expensive ordering error in FinOps.

## 4. Commitments balance discount vs utilization risk (§3 #3)

```
blended_cost = committed_portion * (1 - discount) + on_demand_portion
risk         = committed_capacity * (1 - utilization)   # locked-in waste if usage drops
```

Max coverage maximizes discount AND utilization risk; the right coverage is the point where the marginal discount no longer pays for the marginal lock-in risk.
