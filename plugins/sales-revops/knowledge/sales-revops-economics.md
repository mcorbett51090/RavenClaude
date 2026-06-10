# Sales & Revenue Operations Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/revops_calc.py`](../scripts/revops_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. Coverage is the leading sufficiency test (§3 #1)

```
required_coverage = 1 / stage_weighted_win_rate
coverage_ratio    = open_pipeline / remaining_quota
gap               = (required_coverage - coverage_ratio) * remaining_quota
```

If you historically win ~25% of weighted pipeline, you need ~4x coverage; reading "we have $4M of pipeline" without the $1M quota and the 25% win-rate is reading one number out of three.

## 2. The forecast is weighted and aged, not summed (§3 #2 #6)

```
weighted_forecast = sum(deal_value * stage_win_rate for deal in open)
slip_adjusted     = weighted_forecast * (1 - aging_haircut)
```

A rep's verbal commit is an *input* to calibrate the stage win-rate, not the model itself — committed-deal forecasts drift with rep optimism.

## 3. Velocity has four levers that trade off (§3 #3)

```
sales_velocity = (open_deals * win_rate * avg_deal_size) / cycle_length_days
```

Pushing volume (more leads) often lowers win-rate; raising ACV often lengthens cycle. The funnel diagnosis says which lever is actually the constraint.

## 4. Quota fits under capacity (§3 #4)

```
capacity        = ramped_reps * productivity_per_rep * ramp_factor
implied_p50      = capacity-based median attainment a quota level produces
```

A quota whose implied median attainment is well below 100% is a design error that inflates the forecast and demoralizes the team.
