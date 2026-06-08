# Mortgage Lending Operations Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/mortgage_lending_calc.py`](../scripts/mortgage_lending_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. Pull-through is the chained funnel (§3 #1)

```
funded      = apps * app_to_approved * approved_to_ctc * ctc_to_funded
pull_through = funded / apps
required_apps = target_funded / (app_to_approved * approved_to_ctc * ctc_to_funded)
```

Fix the stage with the worst rate before buying more applications — a leaking funnel wastes acquisition spend, and the worst stage is usually a cycle bottleneck or a late-stage lock/condition problem.

## 2. Capacity is a function of cycle, not a fixed ratio (§3 #2 #4)

```
loans_per_processor = (working_days / cycle_days) * concurrent_loans_per_day_capacity
monthly_capacity    = processors * loans_per_processor
```

A longer cycle means each open loan occupies a processor longer, so effective loans-per-processor — and total capacity — fall. Staff to the measured cycle and the rate-swing volume, never the last peak.

## 3. Cost-to-originate decides survival in the rate cycle (§3 #5 #7)

```
cost_to_originate = (fixed_cost + variable_cost_per_loan * loans) / loans
breakeven_volume  = fixed_cost / margin_per_loan
```

When a refi boom ends and volume halves, the shops that knew their fixed/variable split and their breakeven volume cut to survive; the ones that staffed to the peak don't.

## 4. Lock/pipeline risk runs on the fallout assumption (§3 #3)

```
hedge_relevant_volume = locked_volume * (1 - expected_fallout)
```

Fallout is what makes the hedge an estimate, not a certainty — the same pull-through fallout that hurts the funnel also sizes the lock exposure. The team frames this; the hedge/secondary-marketing decision is the risk authority's call.
