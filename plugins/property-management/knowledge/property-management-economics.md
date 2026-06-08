# Property Management Operations Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/property_management_calc.py`](../scripts/property_management_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. NOI is the scorecard, built off EGI (§3 #4)

```
egi = gross_potential_rent - vacancy_and_loss + other_income
noi = egi - operating_expense
value = noi / cap_rate
```

A revenue move that lifts opex more than it lifts EGI lowers NOI — and at a cap rate, lowers value. Gross or collected rent is not the scorecard.

## 2. Occupancy is a flow, not a point (§3 #1)

```
end_occupied   = start_occupied + move_ins - move_outs
end_occupancy  = end_occupied / total_units
monthly_revenue = end_occupied * avg_rent
```

A single occupancy % on a given day hides the move-in/out flow and the renewal stream that actually fill or empty the asset.

## 3. Slow turns are lost rent (§3 #3)

```
lost_rent_during_turn = vacant_units * turn_days * daily_rent
annualized            = lost_rent_during_turn * (365 / turn_days)  # at this turn cadence
```

Every turn day on a vacant unit is rent that never bills; cutting median turn days is a direct NOI lever before any rent increase.

## 4. Delinquency is aged cash (§3 #2)

```
collectable ≈ sum(bucket_balance * bucket_collectability_weight)  # 0-30 > 31-60 > 60+
```

Total delinquency over-states recoverable cash; the realistic write-down flows straight into the EGI bridge as bad debt.
